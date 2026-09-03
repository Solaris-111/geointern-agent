import base64, requests, json, sys, os

API_KEY = os.getenv("DASHSCOPE_API_KEY")

img_path = sys.argv[1] if len(sys.argv) > 1 else r"E:\成长日志\大三上\周口店大报告图片\1.png"
with open(img_path, "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode()

prompt = """请详细描述这张图片的内容。这是一张地质相关的图片，可能是野外照片、地质图件、剖面图、柱状图、素描图或文档扫描件。

请按以下结构回答：
1. 图片类型：这是什么类型的图？（野外照片/地质图/剖面图/柱状图/素描/表格/文字文档）
2. 如果是图件：图中标注了哪些地质信息？（地层、构造、产状、比例尺、图例等）
3. 如果是照片：拍摄了什么地质现象？
4. 所有可见的文字、标注、数字
5. 其他值得注意的细节"""

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
# Write to file to avoid encoding issues
with open("d:/geointern-agent/_analyze_result.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("Done! Result saved to _analyze_result.json")
print("Status:", resp.status_code)
if "choices" in result:
    print(result["choices"][0]["message"]["content"][:500])
elif "error" in result:
    print("Error:", result["error"])
