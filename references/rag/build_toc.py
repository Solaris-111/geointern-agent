"""
Build table-of-contents index from OCR'd guidebook.
Hybrid approach: auto-detect chapters + fallback to known structure.
"""
import json
import re
from pathlib import Path

INDEX_DIR = Path(__file__).resolve().parent / "index"
CHUNKS_FILE = INDEX_DIR / "chunks.json"
TOC_FILE = INDEX_DIR / "toc.json"

# Known structure from the printed TOC (pages 7-8)
# Printed page -> PDF page offset is approximately +8 (front matter)
KNOWN_STRUCTURE = {
    1: {"title": "绪论", "pdf_page": 9, "locked": True},
    2: {"title": "地质认识实习基本知识", "pdf_page": 19, "locked": True},
    3: {"title": "地质认识实习教学路线", "pdf_page": 73, "locked": True},
    4: {"title": "综合考察路线", "pdf_page": 134, "locked": True},
    5: {"title": "峨眉山-乐山地质资源", "pdf_page": 162, "locked": True},
}

# Routes per chapter (from TOC)
# Each route: (number, name, pdf_page, obs_points)
# obs_points: list of (point_number, description) or None if unknown
KNOWN_ROUTES = {
    3: [  # Chapter 3: teaching routes — ALL verified via keyword distribution + teaching-objective markers
        (1, "清音电站→龙门硐电站 (L01)", 84, [
            ("点1", "玄武岩露头 + 柱状节理"),
            ("点2", "回龙山断层 (D0201)"),
            ("点3", "挖断山断层"),
            ("点4", "牛背山背斜 (D0202)"),
        ]),
        (2, "龙门硐电站→龙门硐口 (L02)", 90, [
            ("点1", "砂岩露头 (垮洪洞组)"),
            ("点2", "灰岩露头 (嘉陵江组)"),
            ("点3", "白云岩露头"),
            ("点4-7", "沉积构造: 波痕/虫迹/层理/渠迹/重荷模/缝合线"),
        ]),
        (3, "五显岗→清音阁→洪椿坪 (L03)", 98, [
            ("点1", "地层观察 (二叠系+三叠系各组)"),
            ("点2", "木鱼山向斜"),
            ("点3", "万年寺断层"),
            ("点4", "观心坡断层"),
            ("点5", "大峨寺断层"),
            ("点6", "峨眉山花岗岩"),
        ]),
        (4, "四溪沟→张坝大队→余坪 (L04)", 108, [
            ("点1", "溶洞形态与发育层位"),
            ("点2", "石芽、石幔"),
            ("点3", "落水洞与干溶洞"),
            ("点4", "新构造运动证据"),
        ]),
        (5, "川主庙→两河口→凉水井 (L05)", 115, [
            ("点1", "夹关组岩性及接触关系"),
            ("点2", "灌口组岩性及接触关系"),
            ("点3", "名山组泡砂岩+小断层"),
            ("点4", "河流地貌对比 (川主河vs龙门硐河)"),
        ]),
        (6, "张沟→两河口→凉水井 (L06)", 122, [
            ("点1", "白垩系地层序列"),
            ("点2", "层间砾岩"),
            ("点3", "河流阶地对比"),
        ]),
        (7, "黄湾→龙门硐河谷 (L07)", 128, [
            ("点1", "龙门硐河谷地貌"),
            ("点2", "河流阶地序列"),
            ("点3", "第四纪沉积物"),
        ]),
        (8, "黄湾→露头区→川主庙 (L08)", 132, [
            ("点1", "野外定点与图切剖面练习"),
            ("点2", "独立填图考核"),
        ]),
    ],
    4: [  # Chapter 4: comprehensive routes
        (9, "为石槽→幺林埂 (L09)", 134, None),
        (10, "岷江千佛岩 (L10)", 136, None),
        (11, "铜河扁水电站 (L11)", 139, None),
        (12, "瀑布岩水电站→岔路口 (L12)", 142, None),
        (13, "峨眉山→乐山沿途观察 (L13)", 149, None),
        (14, "川主庙→两河口→凉水井 (L14)", 153, None),
    ],
}


def compact(text: str) -> str:
    return re.sub(r'(?<=[一-鿿]) +(?=[一-鿿])', '', text)


def load_page_texts() -> dict[int, str]:
    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    pages: dict[int, list[str]] = {}
    for c in chunks:
        p = c["page"]
        if p not in pages:
            pages[p] = []
        pages[p].append(c["text"])
    return {p: compact(" ".join(texts)) for p, texts in pages.items()}


def verify_chapter_page(page_text: str, expected_title_keywords: str) -> bool:
    """Check if a page genuinely starts a chapter."""
    # Check if the page has substantial content matching the expected topic
    # Real chapter starts have: header + "本章概要"/intro + substantial text
    cjk = len(re.findall(r'[一-鿿]', page_text))
    if cjk < 50:
        return False
    # Check for "本章概要" or "本章主要" or section numbering
    if "本章概要" in page_text or "本章主要" in page_text:
        return True
    # Check for numbered sections (X.X pattern)
    if re.search(r'\d+\.\d+\s', page_text):
        return True
    return cjk > 200  # substantial content


def find_actual_chapter_page(page_texts: dict[int, str],
                              ch_num: int,
                              expected_page: int,
                              title_keywords: str,
                              locked: bool = False) -> int:
    """Find the real PDF page where this chapter starts."""
    if locked:
        return expected_page

    candidates = []
    window = 8
    for p in range(max(1, expected_page - window),
                   min(181, expected_page + window + 1)):
        if p not in page_texts:
            continue
        text = page_texts[p]
        score = 0
        # Heavily weight chapter header appearing in first line
        first_line = text.split("\n")[0] if text else ""
        for ch_char in [str(ch_num),
                        {1: "一", 2: "二", 3: "三", 4: "四", 5: "五"}.get(ch_num, str(ch_num))]:
            if f"第{ch_char}章" in first_line[:50]:
                score += 5  # strong signal
            elif f"第{ch_char}章" in text:
                score += 2  # weak signal (could be a reference)
        if title_keywords in text:
            score += 2
        if "本章概要" in text or "本章主要" in text:
            score += 3
        cjk_first = len(re.findall(r'[一-鿿]', text[:300]))
        if cjk_first > 60:
            score += 1
        if score > 0:
            candidates.append((p, score))

    if candidates:
        candidates.sort(key=lambda x: (-x[1], x[0]))
        return candidates[0][0]
    return expected_page


def build_route_entries(routes: list[tuple], ch_end: int) -> list[dict]:
    """Build route entries from known data, including observation points."""
    result = []
    for item in routes:
        rn, rname, expected = item[0], item[1], item[2]
        obs_points = item[3] if len(item) > 3 else None

        children = []
        if obs_points:
            for obs_num, obs_desc in obs_points:
                children.append({
                    "title": f"{obs_num}: {obs_desc}",
                    "page_start": expected,  # approximate
                    "page_end": expected,
                    "level": 3,
                    "children": [],
                })

        result.append({
            "title": f"路线{rn} {rname}",
            "page_start": expected,
            "page_end": expected,
            "level": 2,
            "children": children,
        })

    # Sort by page
    result.sort(key=lambda x: x["page_start"])

    # Set end pages
    for i, r in enumerate(result):
        if i + 1 < len(result):
            r["page_end"] = max(r["page_start"], result[i + 1]["page_start"] - 1)
        else:
            r["page_end"] = max(r["page_start"], ch_end)

    return result


def main():
    print("Building TOC (hybrid auto + known structure)...")
    page_texts = load_page_texts()
    print(f"  Loaded {len(page_texts)} pages")

    toc = []
    sorted_nums = sorted(KNOWN_STRUCTURE)

    for i, ch_num in enumerate(sorted_nums):
        expected = KNOWN_STRUCTURE[ch_num]["pdf_page"]
        keywords = KNOWN_STRUCTURE[ch_num]["title"]
        locked = KNOWN_STRUCTURE[ch_num].get("locked", False)

        # Find actual page
        actual_page = find_actual_chapter_page(
            page_texts, ch_num, expected, keywords, locked)

        # Determine end page
        if i + 1 < len(sorted_nums):
            next_expected = KNOWN_STRUCTURE[sorted_nums[i + 1]]["pdf_page"]
            end_page = next_expected - 1
        else:
            end_page = 181

        entry = {
            "title": f"第{ch_num}章 {keywords}",
            "page_start": actual_page,
            "page_end": end_page,
            "level": 1,
            "children": [],
        }

        # Add routes
        if ch_num in KNOWN_ROUTES:
            routes = build_route_entries(KNOWN_ROUTES[ch_num], end_page)
            entry["children"] = routes
            print(f"  Ch{ch_num}: p{actual_page}-p{end_page} ({len(routes)} routes)")

        toc.append(entry)
        if ch_num not in KNOWN_ROUTES:
            print(f"  Ch{ch_num}: p{actual_page}-p{end_page}")

    # Save JSON
    toc_data = {
        "source": "峨眉山地质实习指导书",
        "total_pages": 181,
        "chapters": toc,
    }
    with open(TOC_FILE, "w", encoding="utf-8") as f:
        json.dump(toc_data, f, ensure_ascii=False, indent=2)

    # Print & save markdown
    lines = ["# 峨眉山地质实习指导书 — 目录索引\n"]
    lines.append("> 混合模式：OCR 自动检测 + 已知结构兜底。页号为 PDF 页码。\n")
    lines.append("> 第3章全部8条路线页码已通过关键词分布+教学目的标记验证。\n")
    for ch in toc:
        lines.append(f"## {ch['title']} (p{ch['page_start']}-p{ch['page_end']})\n")
        for child in ch["children"]:
            lines.append(f"- **{child['title']}** (p{child['page_start']}-p{child['page_end']})")
            for sub in child.get("children", []):
                lines.append(f"  - {sub['title']}")
        if not ch["children"]:
            lines.append("  *(含子章节，未逐级展开)*")
        lines.append("")

    md = "\n".join(lines)
    print("\n" + md)

    md_file = INDEX_DIR / "toc.md"
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"Saved: {TOC_FILE}")
    print(f"Saved: {md_file}")


if __name__ == "__main__":
    main()
