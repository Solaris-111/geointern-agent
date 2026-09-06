"""知识库向量检索：TF-IDF 语义检索 + 地质实体精确匹配，供 web 服务注入 prompt。"""
from pathlib import Path
import re

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

REF_DIR = Path(__file__).resolve().parent.parent / "references"

# 地质实体：组/系/统/阶/群/段、构造、常见岩性、沉积构造
RE_ENTITY = re.compile(
    r"[一-鿿]{2,6}(?:组|系|统|阶|群|段)"
    r"|断层|背斜|向斜|节理|褶皱|不整合|断裂|剪切带|推覆|构造"
    r"|(?:玄武岩|花岗岩|安山岩|辉长岩|闪长岩|流纹岩|凝灰岩|橄榄岩|辉绿岩|"
    r"砂岩|泥岩|页岩|灰岩|白云岩|大理岩|片麻岩|片岩|千枚岩|板岩|石英岩|"
    r"砾岩|粉砂岩|角岩|糜棱岩|硅质岩)"
    r"|(?:层理|波痕|泥裂|缝合线|叠层石|鲍马序列|交错层理|水平层理|平行层理|"
    r"粒序层理|重荷模|火焰构造)"
)

STOPWORDS = {
    "怎么", "什么", "如何", "怎样", "为什么", "判断", "鉴定", "识别", "描述",
    "特征", "区别", "对比", "区分", "方法", "步骤", "有哪些", "是什么",
    "类型", "种类", "几种", "哪些", "野外", "观察", "分析", "注意", "请问",
    "帮我", "一下", "这个", "那个", "一个", "还是", "以及", "还有", "应该",
    "可以", "是不是", "的", "了", "是", "有", "在", "和", "与", "或",
}

# 全局索引状态（懒加载 + 缓存）
_state = {"chunks": None, "vectorizer": None, "matrix": None}


def _load_chunks():
    """加载 references/ 下所有 markdown，按标题切成块。"""
    chunks = []
    for md in sorted(REF_DIR.rglob("*.md")):
        try:
            text = md.read_text(encoding="utf-8")
        except Exception:
            continue
        rel = str(md.relative_to(REF_DIR))
        blocks = re.split(r"(?m)^(#{1,3}\s+.*)$", text)
        if len(blocks) == 1:
            body = text.strip()
            if len(body) > 30:
                chunks.append({"title": md.stem, "file": rel, "text": body[:2000]})
        else:
            for i in range(1, len(blocks), 2):
                title = blocks[i].lstrip("#").strip()
                body = (blocks[i + 1] if i + 1 < len(blocks) else "").strip()
                if body:
                    chunks.append({"title": title, "file": rel,
                                   "text": f"{title}\n{body}"[:1500]})
    return chunks


def _build_index():
    """构建 TF-IDF 向量索引（char 级 n-gram，适配中文）。"""
    chunks = _load_chunks()
    vectorizer = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        analyzer="char_wb",
    )
    matrix = vectorizer.fit_transform([c["text"] for c in chunks])
    return chunks, vectorizer, matrix


def _ensure_index():
    if _state["chunks"] is None:
        chunks, vectorizer, matrix = _build_index()
        _state["chunks"] = chunks
        _state["vectorizer"] = vectorizer
        _state["matrix"] = matrix


def _query_entities(query):
    """提取查询里的地质实体（用于精确匹配加权）。"""
    return set(RE_ENTITY.findall(query))


def search(query, top_k=4):
    """混合检索：TF-IDF 向量相似度 + 地质实体精确匹配。"""
    _ensure_index()
    chunks = _state["chunks"]
    entities = _query_entities(query)

    query_vec = _state["vectorizer"].transform([query])
    sims = cosine_similarity(query_vec, _state["matrix"])[0]

    scored = []
    for idx, chunk in enumerate(chunks):
        score = float(sims[idx]) * 3.0
        for e in entities:
            if e in chunk["text"]:
                score += 2.0
        if score > 0.01:
            scored.append((score, chunk))

    scored.sort(key=lambda x: -x[0])
    return [c for _, c in scored[:top_k]]


def build_context(query):
    """把检索结果拼成可注入 prompt 的上下文文本；无结果返回空串。"""
    results = search(query)
    if not results:
        return ""
    lines = ["以下是从知识库检索到的参考资料，回答时请参考，但不要逐字照抄："]
    for i, r in enumerate(results, 1):
        lines.append(f"\n【资料{i}】{r['file']} · {r['title']}\n{r['text']}")
    return "\n".join(lines)
