import base64, requests, json, os

API_KEY = os.getenv("DASHSCOPE_API_KEY")

img_dir = r"E:\成长日志\大三上\周口店大报告图片"
results = {}

for fname in sorted(os.listdir(img_dir)):
    if not fname.endswith('.png'):
        continue
    fpath = os.path.join(img_dir, fname)
    with open(fpath, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()

    prompt = "用一句话描述这张图是什么类型的图件（地质图/剖面图/柱状图/素描图/照片/表格），以及图中最关键的地质信息。如果图上有高程数字、等高线或地形标注，请特别说明。"

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
        timeout=30
    )

    result = resp.json()
    content = result.get("choices", [{}])[0].get("message", {}).get("content", "no response")
    results[fname] = content
    print(f"{fname}: done ({len(content)} chars)")

# Save all results
with open("d:/geointern-agent/output/images_check.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print("\nAll results saved.")
