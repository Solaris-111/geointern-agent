"""双边滤波直通 VTracer — 不经过 Canny"""

import vtracer
import cv2
import os

def pipeline(name, img_path, out_dir, bf_d=9, bf_sigma=75):
    """双边滤波 → 灰度 → VTracer binary"""
    os.makedirs(out_dir, exist_ok=True)

    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    filtered = cv2.bilateralFilter(gray, bf_d, bf_sigma, bf_sigma)

    cv2.imwrite(f"{out_dir}/bilateral.png", filtered)

    vtracer.convert_image_to_svg_py(
        f"{out_dir}/bilateral.png",
        f"{out_dir}/bilateral.svg",
        colormode="binary",
        corner_threshold=50,
        mode="spline",
    )

    # 也试一组更激进的双边滤波 (去纹理力度更大)
    filtered_strong = cv2.bilateralFilter(gray, 15, 100, 100)
    cv2.imwrite(f"{out_dir}/bilateral_strong.png", filtered_strong)
    vtracer.convert_image_to_svg_py(
        f"{out_dir}/bilateral_strong.png",
        f"{out_dir}/bilateral_strong.svg",
        colormode="binary",
        corner_threshold=50,
        mode="spline",
    )

    print(f"{name} 完成:")
    for f in sorted(os.listdir(out_dir)):
        size = os.path.getsize(f"{out_dir}/{f}")
        print(f"  {f} ({size/1024:.0f} KB)")


# D0601 燧石条带
pipeline("D0601", "output/D0601_outcrop.jpg", "output/sketch_test/D0601_bilateral")

# D0605 叠层石
pipeline("D0605", "output/D0605_outcrop.jpg", "output/sketch_test/D0605_bilateral")
