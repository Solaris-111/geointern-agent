import json
import os
from pathlib import Path

import requests

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from openai import OpenAI
from pydantic import BaseModel

import rag_search

BASE_DIR = Path(__file__).resolve().parent
SKILL_PATH = BASE_DIR.parent / "SKILL.md"

load_dotenv(BASE_DIR / ".env")


def load_system_prompt() -> str:
    text = SKILL_PATH.read_text(encoding="utf-8")
    # 去掉 skill 的 frontmatter（--- 之间的元信息，模型不需要）
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            text = parts[2]
    return text.strip()


SYSTEM_PROMPT = load_system_prompt()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)
MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-pro")

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")

VISION_PROMPT = (
    "请以地质学家的视角描述这张图片："
    "1. 观察尺度（远景/近景/手标本/薄片）；"
    "2. 岩性特征（颜色、粒度、结构、构造）；"
    "3. 可能的岩石类型；"
    "4. 特殊地质现象（层理、断层、褶皱、化石、沉积构造等）。"
    "简洁专业，不要套话。"
)


def vision_analyze(image_b64, question=""):
    """用 Qwen-VL 识别图片，返回地质描述。"""
    if not DASHSCOPE_API_KEY:
        return "[未配置 DASHSCOPE_API_KEY]"
    image_url = image_b64 if image_b64.startswith("data:") else f"data:image/jpeg;base64,{image_b64}"
    prompt = VISION_PROMPT
    if question:
        prompt = f"用户问题：{question}\n\n{prompt}"
    try:
        resp = requests.post(
            "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
            headers={"Authorization": f"Bearer {DASHSCOPE_API_KEY}"},
            json={
                "model": "qwen-vl-max",
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": image_url}},
                        {"type": "text", "text": prompt},
                    ],
                }],
            },
            timeout=90,
        )
    except requests.exceptions.Timeout:
        return "[识图超时：图片可能过大，请换一张更小的图片]"
    except requests.exceptions.RequestException as e:
        return f"[识图请求失败：{e}]"
    if resp.status_code != 200:
        return f"[识图失败：API 返回 {resp.status_code}]"
    data = resp.json()
    if "choices" not in data:
        err = data.get("error", {})
        msg = err.get("message", "") if isinstance(err, dict) else str(err)
        return f"[识图失败：{msg or '未知错误'}]"
    return data["choices"][0]["message"]["content"]

app = FastAPI(title="GeoIntern-Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    messages: list
    images: list = []


@app.get("/")
def index():
    return HTMLResponse((BASE_DIR / "index.html").read_text(encoding="utf-8"))


@app.post("/chat")
def chat(req: ChatRequest):
    user_query = ""
    for m in reversed(req.messages):
        if isinstance(m, dict) and m.get("role") == "user":
            user_query = str(m.get("content", ""))
            break
    vision_desc = ""
    if req.images:
        try:
            vision_desc = vision_analyze(req.images[0], user_query)
        except Exception as e:
            vision_desc = f"[识图失败：{e}]"
    context_parts = []
    if user_query:
        rag_ctx = rag_search.build_context(user_query)
        if rag_ctx:
            context_parts.append(rag_ctx)
    if vision_desc:
        context_parts.append("【图片识别结果（Qwen-VL）】\n" + vision_desc)
    context = "\n\n".join(context_parts)
    system_content = SYSTEM_PROMPT + ("\n\n" + context if context else "")
    history = [{"role": "system", "content": system_content}] + req.messages

    def gen():
        try:
            stream = client.chat.completions.create(
                model=MODEL,
                messages=history,
                stream=True,
            )
            for chunk in stream:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta
                # 只推最终答案，跳过 reasoning_content（思考过程不展示给用户）
                content = getattr(delta, "content", None)
                if content:
                    yield f"data: {json.dumps({'content': content}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
