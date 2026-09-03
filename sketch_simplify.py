"""VTracer 简化参数对比 — 找最优素描管线"""

import vtracer
import os

PHOTOS = {
    "D0601": "output/D0601_outcrop.jpg",
    "D0605": "output/D0605_outcrop.jpg",
}

# 四组参数，从原始到极简
PRESETS = [
    ("raw",        None,  None,  None),   # 原始 VTracer binary
    ("moderate",   20,    90,    None),   # 中等简化: 去碎斑 + 线条流畅
    ("clean",      50,    120,   10),     # 干净: 去更多噪音 + 删短线
    ("skeleton",   100,   150,   20),     # 骨架: 只留地质主干
]

for name, img_path in PHOTOS.items():
    out_dir = f"output/sketch_test/{name}_simplify"
    os.makedirs(out_dir, exist_ok=True)

    for preset, fs, ct, lt in PRESETS:
        out_svg = f"{out_dir}/{preset}.svg"
        print(f"{name} {preset}...", end=" ", flush=True)
        vtracer.convert_image_to_svg_py(
            img_path,
            out_svg,
            colormode="binary",
            mode="spline",
            filter_speckle=fs,
            corner_threshold=ct,
            length_threshold=lt,
        )
        size = os.path.getsize(out_svg)
        print(f"{size/1024:.0f} KB")

    # 也试一组双边滤波预处理 + 简化参数
    import cv2
    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    filtered = cv2.bilateralFilter(gray, 15, 100, 100)
    pre_path = f"{out_dir}/_pre_bilateral.png"
    cv2.imwrite(pre_path, filtered)

    for preset, fs, ct, lt in PRESETS[1:]:  # 跳过 raw
        out_svg = f"{out_dir}/bilateral_{preset}.svg"
        print(f"{name} bilateral+{preset}...", end=" ", flush=True)
        vtracer.convert_image_to_svg_py(
            pre_path,
            out_svg,
            colormode="binary",
            mode="spline",
            filter_speckle=fs,
            corner_threshold=ct,
            length_threshold=lt,
        )
        size = os.path.getsize(out_svg)
        print(f"{size/1024:.0f} KB")

print("\n完成")
