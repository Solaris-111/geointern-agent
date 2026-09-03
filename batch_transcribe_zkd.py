"""Batch transcribe field notebook images using Qwen-VL."""
import base64, requests, json, sys, os, time, io
from PIL import Image
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

NOTEBOOK_DIR = Path(r"D:\geointern-agent\field_notebooks\周口店")
OUTPUT_FILE = NOTEBOOK_DIR / "full_transcript.md"

PROMPT = """你是一个野外地质实习野簿转录员。请逐字转录这页野簿的所有内容。

要求：
1. 逐字转录，保留原文格式和换行
2. 如果是素描图，描述图中的地质内容（岩性、构造、地层界线、标注文字等）
3. 如果是表格，转换为Markdown表格
4. 不确定的字用 [?] 标注
5. 照片横拍（旋转90°）的内容，请先在心里旋转后再转录

输出格式：只输出转录内容，不要加任何说明。"""

def transcribe_images(image_paths, batch_size=1):
    results = {}
    total = len(image_paths)

    for i, img_path in enumerate(image_paths):
        print(f"[{i+1}/{total}] Processing: {img_path.name}...")

        try:
            img = Image.open(img_path)

            # Resize if too large
            if max(img.size) > 2000:
                ratio = 2000 / max(img.size)
                img = img.resize((int(img.size[0]*ratio), int(img.size[1]*ratio)))

            # Save as PNG for base64
            tmp_path = img_path.with_suffix('.tmp.png')
            img.save(tmp_path)

            with open(tmp_path, 'rb') as f:
                b64 = base64.b64encode(f.read()).decode()

            # Clean up temp file
            tmp_path.unlink()

            content_blocks = [
                {'type': 'image_url', 'image_url': {'url': f'data:image/png;base64,{b64}'}},
                {'type': 'text', 'text': PROMPT}
            ]

            resp = requests.post(
                'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions',
                headers={'Authorization': f"Bearer {os.getenv('DASHSCOPE_API_KEY')}"},
                json={
                    'model': 'qwen-vl-max',
                    'messages': [{'role': 'user', 'content': content_blocks}]
                },
                timeout=120
            )

            result = resp.json()
            content = result['choices'][0]['message']['content']
            results[img_path.name] = content
            print(f"  -> OK ({len(content)} chars)", flush=True)

            # Rate limit: 1 request per second
            time.sleep(0.5)

        except Exception as e:
            print(f"  -> ERROR: {e}")
            results[img_path.name] = f"[转录失败: {e}]"

    return results


def check_orientation(image_paths):
    """Quick check of first few images for orientation."""
    for img_path in image_paths[:3]:
        img = Image.open(img_path)
        print(f"{img_path.name}: size={img.size}, mode={img.mode}")
        # Check EXIF orientation
        try:
            exif = img._getexif()
            if exif:
                orientation = exif.get(274, 1)  # 274 = Orientation tag
                orient_map = {1:'normal', 3:'180°', 6:'90°CW', 8:'90°CCW'}
                print(f"  EXIF orientation: {orient_map.get(orientation, orientation)}")
        except:
            print(f"  No EXIF orientation data")


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--check':
        imgs = sorted(NOTEBOOK_DIR.glob("IMG20260803162*.jpg"))
        check_orientation(imgs[:3])
    elif len(sys.argv) > 1 and sys.argv[1] == '--test':
        imgs = sorted(NOTEBOOK_DIR.glob("IMG202608031624*.jpg"))
        results = transcribe_images(imgs[:2])
        for name, text in results.items():
            print(f"\n=== {name} ===")
            print(text)
    elif len(sys.argv) > 1 and sys.argv[1] == '--continue':
        # Resume from existing transcript
        existing = {}
        if OUTPUT_FILE.exists():
            current_section = None
            current_text = []
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('## ') and line.strip().endswith('.jpg'):
                        if current_section and current_text:
                            existing[current_section] = ''.join(current_text).strip()
                        current_section = line.strip('# ').strip()
                        current_text = []
                    elif current_section:
                        current_text.append(line)
                if current_section and current_text:
                    existing[current_section] = ''.join(current_text).strip()
        print(f"Resuming: {len(existing)} pages already transcribed")

        all_imgs = sorted(NOTEBOOK_DIR.glob("*.jpg"))
        imgs = [p for p in all_imgs if 'day1' not in str(p) and p.name not in existing]
        print(f"Remaining: {len(imgs)} images")

        if not imgs:
            print("All done!")
            sys.exit(0)

        # Start from scratch with checkpointing
        checkpoint_file = NOTEBOOK_DIR / "transcript_checkpoint.json"
        if checkpoint_file.exists():
            with open(checkpoint_file, 'r', encoding='utf-8') as f:
                results = json.load(f)
            imgs = [p for p in imgs if p.name not in results]
            print(f"Loaded checkpoint: {len(results)} done, {len(imgs)} remaining")
        else:
            results = {}

        for i, img_path in enumerate(imgs):
            print(f"[{i+1}/{len(imgs)}] {img_path.name}...", end=' ', flush=True)

            try:
                img = Image.open(img_path)
                if max(img.size) > 2000:
                    ratio = 2000 / max(img.size)
                    img = img.resize((int(img.size[0]*ratio), int(img.size[1]*ratio)))
                tmp_path = img_path.with_suffix('.tmp.png')
                img.save(tmp_path)
                with open(tmp_path, 'rb') as f:
                    b64 = base64.b64encode(f.read()).decode()
                tmp_path.unlink()

                resp = requests.post(
                    'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions',
                    headers={'Authorization': f"Bearer {os.getenv('DASHSCOPE_API_KEY')}"},
                    json={'model': 'qwen-vl-max', 'messages': [{'role': 'user', 'content': [
                        {'type': 'image_url', 'image_url': {'url': f'data:image/png;base64,{b64}'}},
                        {'type': 'text', 'text': PROMPT}
                    ]}]},
                    timeout=120
                )

                content = resp.json()['choices'][0]['message']['content']
                results[img_path.name] = content
                print(f"OK ({len(content)} chars)", flush=True)

                # Save checkpoint every 10 images
                if (i + 1) % 10 == 0:
                    with open(checkpoint_file, 'w', encoding='utf-8') as f:
                        json.dump(results, f, ensure_ascii=False)
                    print(f"  [checkpoint: {len(results)} pages saved]", flush=True)

                time.sleep(0.3)

            except Exception as e:
                print(f"ERROR: {e}", flush=True)
                results[img_path.name] = f"[转录失败: {e}]"
                # Save checkpoint on error too
                with open(checkpoint_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False)

        # Merge with existing and write final output
        all_results = {**existing, **results}
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write("# 野簿完整转录（峨眉山 + 北戴河 + 周口店）\n\n")
            for name in sorted(all_results.keys()):
                f.write(f"## {name}\n\n")
                f.write(all_results[name])
                f.write("\n\n---\n\n")

        # Clean checkpoint
        if checkpoint_file.exists():
            checkpoint_file.unlink()

        print(f"\nDone. {len(all_results)} pages -> {OUTPUT_FILE}")
