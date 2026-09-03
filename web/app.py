import json
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from openai import OpenAI
from pydantic import BaseModel

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

app = FastAPI(title="GeoIntern-Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    messages: list


@app.get("/")
def index():
    return HTMLResponse((BASE_DIR / "index.html").read_text(encoding="utf-8"))


@app.post("/chat")
def chat(req: ChatRequest):
    history = [{"role": "system", "content": SYSTEM_PROMPT}] + req.messages

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
