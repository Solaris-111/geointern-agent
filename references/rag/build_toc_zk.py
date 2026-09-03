"""
Build TOC for Zhoukoudian guidebook separately.
"""
import json, re
from pathlib import Path

INDEX_DIR = Path(__file__).resolve().parent / "index"
CHUNKS_FILE = INDEX_DIR / "chunks.json"
TOC_FILE = INDEX_DIR / "toc_zhoukoudian.json"

KNOWN_STRUCTURE = {
    1: {"title": "绪论", "pdf_page": 7},
    2: {"title": "周口店地区区域地质概况", "pdf_page": 11},
    3: {"title": "野外地质调查工作方法", "pdf_page": 41},
    4: {"title": "周口店地区教学路线指导", "pdf_page": 81},
    5: {"title": "地质图的绘制及报告编写", "pdf_page": 112},
    6: {"title": "常用地质基本知识（约500词）", "pdf_page": 118},
}

KNOWN_ROUTES = {
    4: [
        (1,  "踏勘路线", 81),
        (2,  "八角寨—拴马庄桥 中元古代地层观察", 83),
        (3,  "黄院东山梁 下古生界地层观察", 86),
        (4,  "太平山南坡 上古生界地层观察", 88),
        (5,  "太平山北坡 上古生界地层观察", 90),
        (6,  "房山岩体+热接触变质岩观察 (探矿厂→官地→羊屎沟)", 93),
        (7,  "羊屎沟 动力变质岩观察", 95),
        (8,  "太平山背斜+地层+构造观察 (探矿厂→煤炭沟→太平山→探矿厂)", 97),
        (9,  "孤山口 构造观察 (孤山口火车站)", 99),
        (10, "孤山口褶皱构造观察 (孤山口火车站)", 100),
        (11, "房山断裂构造观察 (探矿厂→牛口峪→房山西)", 102),
        (12, "逆冲推覆构造观察", 104),
        (13, "164背斜+逆冲推覆构造 (探矿厂→一条龙)", 106),
        (14, "黄山店褶皱冲断构造 (探矿厂→黄山店→探矿厂)", 107),
        (15, "上方山岩溶地貌观察 (圣水峪→上方山→云水洞)", 108),
        (16, "独立填图实践", 110),
    ],
}


def main():
    print("Building Zhoukoudian TOC...")

    toc = []
    sorted_nums = sorted(KNOWN_STRUCTURE)

    for i, ch_num in enumerate(sorted_nums):
        ch = KNOWN_STRUCTURE[ch_num]
        start = ch["pdf_page"]
        end = KNOWN_STRUCTURE[sorted_nums[i + 1]]["pdf_page"] - 1 \
            if i + 1 < len(sorted_nums) else 126

        entry = {
            "title": f"第{ch_num}章 {ch['title']}",
            "page_start": start,
            "page_end": end,
            "level": 1,
            "children": [],
        }

        if ch_num in KNOWN_ROUTES:
            routes = KNOWN_ROUTES[ch_num]
            route_entries = []
            for rn, rname, rpage in routes:
                route_entries.append({
                    "title": f"路线{rn} {rname}",
                    "page_start": rpage,
                    "page_end": rpage,
                    "level": 2,
                    "children": [],
                })
            # Set end pages
            route_entries.sort(key=lambda x: x["page_start"])
            for j, r in enumerate(route_entries):
                r["page_end"] = route_entries[j + 1]["page_start"] - 1 \
                    if j + 1 < len(route_entries) else end
            entry["children"] = route_entries
            print(f"  Ch{ch_num}: p{start}-p{end} ({len(routes)} routes)")

        toc.append(entry)
        if ch_num not in KNOWN_ROUTES:
            print(f"  Ch{ch_num}: p{start}-p{end}")

    # Save JSON
    toc_data = {
        "source": "周口店地区地质实习指导书（王根厚主编）",
        "total_pages": 126,
        "chapters": toc,
    }
    with open(TOC_FILE, "w", encoding="utf-8") as f:
        json.dump(toc_data, f, ensure_ascii=False, indent=2)

    # Markdown
    lines = ["# 周口店地区地质实习指导书 — 目录索引\n"]
    lines.append("> 页号为 PDF 页码。路线页码范围为估算。\n")
    for ch in toc:
        lines.append(f"## {ch['title']} (p{ch['page_start']}-p{ch['page_end']})\n")
        for child in ch["children"]:
            lines.append(f"- **{child['title']}** (p{child['page_start']}-p{child['page_end']})")
        if not ch["children"]:
            lines.append("  *(含子章节，未逐级展开)*")
        lines.append("")

    md = "\n".join(lines)
    md_file = INDEX_DIR / "toc_zhoukoudian.md"
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(md)

    print(f"\nSaved: {TOC_FILE}")
    print(f"Saved: {md_file}")
    print(md)


if __name__ == "__main__":
    main()
