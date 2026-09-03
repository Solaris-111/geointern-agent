import base64, requests, json, os

API_KEY = os.getenv("DASHSCOPE_API_KEY")

with open(r"E:\成长日志\大三上\周口店大报告图片\1.png", "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode()

with open("d:/geointern-agent/_boundary_prompt.txt", "r", encoding="utf-8") as f:
    prompt = f.read()

resp = requests.post(
    "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
    headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
    json={
        "model": "qwen-vl-max",
        "messages": [{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}},
                {"type": "text", "text": prompt}
            ]
        }]
    },
    timeout=60
)

result = resp.json()
with open("d:/geointern-agent/output/boundary_result.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print("Done. Status:", resp.status_code)
