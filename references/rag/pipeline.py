"""
GeoIntern-Agent RAG Pipeline
=============================
GeoGPT-inspired RAG pipeline for geology field internship.
- Geology-aware PDF chunking (by formation/structure/route entities, not token windows)
- Multi-index retrieval: exact match + TF-IDF semantic + hierarchy expansion
- Route-aware reranking
- Citation-preserving output

Usage:
  python pipeline.py index    # Build index from references/rag/ PDFs
  python pipeline.py search "飞仙关组什么岩性" --route emeishan-2
"""

import json
import re
import sys
import os
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from typing import Optional
import pickle

import fitz  # pymupdf
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# OCR for scanned PDFs
from PIL import Image
import io
import pytesseract

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent.parent  # geointern-agent/
RAG_DIR = ROOT_DIR / "references" / "rag"
INDEX_DIR = RAG_DIR / "index"
PDF_DIRS = {
    "guidebook": RAG_DIR / "guidebook",
    "textbook": RAG_DIR / "textbook",
    "notes": RAG_DIR / "notes",
}
PAGE_IMG_DIR = RAG_DIR / "page_images"

# Tesseract OCR config
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
os.environ["TESSDATA_PREFIX"] = str(RAG_DIR / "tessdata")

# ---------------------------------------------------------------------------
# Geology-specific patterns (Chinese)
# ---------------------------------------------------------------------------

CJK = r"[一-鿿]"  # CJK Unified Ideographs

# Common Chinese grammar particles and non-geological words
# If an entity starts with or consists entirely of these, it's a false positive
_GRAMMAR_PARTICLES = {
    "为", "的", "与", "和", "或", "及", "其", "以", "而", "等",
    "该", "此", "则", "被", "把", "从", "在", "对", "是", "有",
    "呈", "见", "具", "较", "不", "也", "都", "就", "但", "了",
    "到", "所", "中", "上", "下", "出", "后", "前", "要",
    "水平", "垂直", "发育", "主要", "一般", "特征", "描述", "明显",
    "十分", "非常", "可以", "可能", "没有", "不是", "属于",
    "分为", "包括", "存在", "分别", "一部分", "大部分",
}

# Formation/stratigraphic unit names: name + suffix
# "层" is tricky — it appears in both "XX层" (formation bed) and "XX断层" (fault).
# We match generously here and filter false positives in _filter_entities().
_RE_FORMATION_BASE = re.compile(
    rf"({CJK}{{2,6}}(?:组|系|统|阶|群|段|层))"
)

# Structure names: name + structure type
_RE_STRUCTURE_BASE = re.compile(
    rf"({CJK}{{2,8}}(?:断层|背斜|向斜|节理|褶皱|不整合|断裂|破碎带))"
)

# Lithology names: specific rock types
# Whitelist of known lithology prefixes + general pattern for unknown ones
_RE_LITHOLOGY_BASE = re.compile(
    rf"((?:玄武|花岗|安山|辉长|闪长|流纹|凝灰|粗面|正长|辉绿|橄榄|"
    rf"砂|砾|泥|页|灰|白云|大理|片麻|片|千枚|板|石英|"
    rf"角|粉砂|粘土|铝土|铁|锰|磷|膏盐|"
    rf"生物碎屑|鲕粒|竹叶|豹皮|"
    rf"){{1,2}}(?:岩|石))"
    rf"|"
    rf"({CJK}{{2,3}}岩(?!层|石|溶|脉|体|块|土|工|料|画|油|气|矿))"  # General XX岩 with exclusions
)

# Route/observation point references
RE_ROUTE_POINT = re.compile(
    r"(路线\s*[一二三四五六七八九十\d]+|观察点\s*\d+|点\s*\d+|"
    r"清音电站|龙门硐|五显岗|清音阁|洪椿坪|四溪沟|川主庙|两河口|凉水井|"
    r"回龙山|挖断山|牛背山|木鱼山|万年寺|观心坡|大峨寺)"
)


def _filter_entities(entities: list[str]) -> list[str]:
    """Remove false positives from entity extraction."""
    # Known non-formation patterns that the regex might catch
    _NON_FORMATION_PATTERNS = {
        "断层", "岩层", "矿层", "煤层", "沙层", "土层", "夹层",
        "盖层", "储层", "底层", "表层", "地层",
    }
    result = []
    for e in entities:
        e = e.strip()
        if not e or len(e) < 3:
            continue
        # Skip known non-formation patterns
        if any(nfp in e for nfp in _NON_FORMATION_PATTERNS):
            continue
        # Extract the "name" part by removing known suffixes
        # (remove suffixes from longest to shortest to handle compound suffixes)
        name_part = e
        for suffix in ["破碎带", "不整合", "断裂", "断层", "背斜", "向斜", "褶皱", "节理",
                        "组", "系", "统", "阶", "群", "段", "层"]:
            if name_part.endswith(suffix):
                name_part = name_part[:-len(suffix)]
                break
        # Must have a meaningful name part
        if len(name_part) < 2:
            continue
        # Skip if name starts with grammar particle
        if any(name_part.startswith(gp) for gp in _GRAMMAR_PARTICLES):
            continue
        result.append(e)
    return result

# Hierarchy mapping: series/system → subordinate formations
# Will be populated from extracted text
HIERARCHY: dict[str, list[str]] = {}

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Chunk:
    """A geology-aware text chunk."""
    id: str
    text: str
    source: str          # "guidebook" | "textbook" | "notes"
    filename: str
    page: int
    page_image: str = ""  # relative path to page PNG (for scanned PDFs)
    route_hints: list[str] = field(default_factory=list)   # e.g. ["emeishan-1"]
    formations: list[str] = field(default_factory=list)     # extracted formation names
    structures: list[str] = field(default_factory=list)     # extracted structure names
    lithologies: list[str] = field(default_factory=list)    # extracted lithology names
    heading: str = ""   # nearest section heading


@dataclass
class SearchResult:
    """A single search result."""
    chunk_id: str
    score: float
    text: str
    source: str
    filename: str
    page: int
    page_image: str = ""
    formations: list[str] = field(default_factory=list)
    structures: list[str] = field(default_factory=list)
    route_hints: list[str] = field(default_factory=list)
    match_type: str = ""  # "exact" | "semantic" | "hierarchy"


# ---------------------------------------------------------------------------
# OCR for scanned PDF pages
# ---------------------------------------------------------------------------

def _ocr_page(page: fitz.Page, dpi: int = 300) -> str:
    """OCR a scanned PDF page. Returns extracted text."""
    pix = page.get_pixmap(dpi=dpi)
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    text = pytesseract.image_to_string(img, lang="chi_sim+eng")
    return text.strip()


def _save_page_image(page: fitz.Page, pdf_name: str, page_num: int, dpi: int = 150) -> str:
    """Save a page as PNG for visual reference. Returns relative path."""
    PAGE_IMG_DIR.mkdir(parents=True, exist_ok=True)
    stem = Path(pdf_name).stem
    img_name = f"{stem}_p{page_num + 1:04d}.png"
    img_path = PAGE_IMG_DIR / img_name
    if not img_path.exists():
        pix = page.get_pixmap(dpi=dpi)
        pix.save(str(img_path))
    return f"references/rag/page_images/{img_name}"


# ---------------------------------------------------------------------------
# PDF extraction
# ---------------------------------------------------------------------------

def extract_pdfs() -> list[dict]:
    """Extract text page-by-page from all PDFs in rag directories.
    For scanned (image-only) pages, uses OCR."""
    documents = []
    for source_name, pdf_dir in PDF_DIRS.items():
        if not pdf_dir.exists():
            continue
        for pdf_path in pdf_dir.glob("*.pdf"):
            try:
                doc = fitz.open(str(pdf_path))
                ocr_count = 0
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    text = page.get_text()
                    if not text.strip():
                        # Scanned page — use OCR
                        text = _ocr_page(page)
                        ocr_count += 1
                    if text.strip():
                        # Save page image for visual reference
                        img_rel_path = _save_page_image(page, pdf_path.name, page_num)
                        documents.append({
                            "text": text,
                            "source": source_name,
                            "filename": pdf_path.name,
                            "page": page_num + 1,
                            "page_image": img_rel_path,
                        })
                doc.close()
                status = f"  [OK] {pdf_path.name} ({len(doc)} pages"
                if ocr_count > 0:
                    status += f", {ocr_count} OCR'd"
                status += ")"
                print(status)
            except Exception as e:
                print(f"  [SKIP] {pdf_path.name}: {e}")
    return documents


# ---------------------------------------------------------------------------
# Geology-aware chunking
# ---------------------------------------------------------------------------

def _extract_entities(text: str) -> dict:
    """Extract geological entities from text."""
    raw_formations = [m.group(1) for m in _RE_FORMATION_BASE.finditer(text)]
    raw_structures = [m.group(1) for m in _RE_STRUCTURE_BASE.finditer(text)]
    raw_lithologies = [m.group(0) for m in _RE_LITHOLOGY_BASE.finditer(text)]
    raw_routes = [m.group(0) for m in RE_ROUTE_POINT.finditer(text)]

    return {
        "formations": list(set(_filter_entities(raw_formations))),
        "structures": list(set(_filter_entities(raw_structures))),
        "lithologies": list(set(_filter_entities(raw_lithologies))),
        "route_hints": list(set(raw_routes)),
    }


def _find_section_boundaries(text: str) -> list[int]:
    """
    Find natural section boundaries in geology text.
    Looks for: route headers, formation name lines, numbered observation points,
    section headings (第X章, 第X节, X、, (X)).
    """
    boundaries = [0]
    lines = text.split("\n")
    char_pos = 0
    for line in lines:
        stripped = line.strip()
        if not stripped:
            char_pos += len(line) + 1
            continue
        # Route headers
        if re.match(r"^(路线\s*[一二三四五六七八九十\d])", stripped):
            boundaries.append(char_pos)
        # Numbered points
        elif re.match(r"^[\(（]?\d+[\)）]?[\.、\s]", stripped) and len(stripped) < 80:
            boundaries.append(char_pos)
        # Formation/unit standalone lines
        elif re.match(r"^[一-鿿]{1,6}(?:组|系|统|阶|群)$", stripped):
            boundaries.append(char_pos)
        # Chapter/section headers
        elif re.match(r"^(第[一二三四五六七八九十\d]+[章节]|[\d一二三四五六七八九十]+[、．.])", stripped):
            boundaries.append(char_pos)
        char_pos += len(line) + 1
    if len(text) > boundaries[-1] + 50:
        boundaries.append(len(text))
    return sorted(set(boundaries))


def chunk_documents(documents: list[dict]) -> list[Chunk]:
    """Split documents into geology-aware chunks."""
    chunks = []
    chunk_id = 0
    for doc in documents:
        text = doc["text"]
        source = doc["source"]
        filename = doc["filename"]
        page = doc["page"]

        # Find natural boundaries
        boundaries = _find_section_boundaries(text)

        for i in range(len(boundaries) - 1):
            start = boundaries[i]
            end = boundaries[i + 1]
            chunk_text = text[start:end].strip()

            # Skip chunks that are too short or just noise
            if len(chunk_text) < 20:
                continue
            # Skip pages that are mostly tables/footers (high digit-to-text ratio)
            digits = sum(c.isdigit() for c in chunk_text)
            if len(chunk_text) > 0 and digits / len(chunk_text) > 0.4:
                continue

            entities = _extract_entities(chunk_text)

            # Determine route hints from text content
            route_hints = _resolve_route_hints(chunk_text, entities["route_hints"])

            chunks.append(Chunk(
                id=f"chunk_{chunk_id:04d}",
                text=chunk_text,
                source=source,
                filename=filename,
                page=page,
                page_image=doc.get("page_image", ""),
                route_hints=route_hints,
                formations=entities["formations"],
                structures=entities["structures"],
                lithologies=entities["lithologies"],
                heading=_extract_heading(chunk_text),
            ))
            chunk_id += 1

    return chunks


def _resolve_route_hints(text: str, route_refs: list[str]) -> list[str]:
    """Convert text route references to normalized route IDs."""
    hints = []
    route_map = {
        "路线一": "emeishan-1", "路线1": "emeishan-1",
        "路线二": "emeishan-2", "路线2": "emeishan-2",
        "路线三": "emeishan-3", "路线3": "emeishan-3",
        "路线四": "emeishan-4", "路线4": "emeishan-4",
        "路线五": "emeishan-5", "路线5": "emeishan-5",
        "清音电站": "emeishan-1", "龙门硐电站": "emeishan-1",
        "龙门硐口": "emeishan-2",
        "五显岗": "emeishan-3", "清音阁": "emeishan-3", "洪椿坪": "emeishan-3",
        "四溪沟": "emeishan-4",
        "川主庙": "emeishan-5", "两河口": "emeishan-5", "凉水井": "emeishan-5",
        "回龙山": "emeishan-1", "挖断山": "emeishan-1", "牛背山": "emeishan-1",
        "木鱼山": "emeishan-3", "万年寺": "emeishan-3",
        "观心坡": "emeishan-3", "大峨寺": "emeishan-3",
    }
    for ref in route_refs:
        if ref in route_map:
            hints.append(route_map[ref])
    return list(set(hints)) if hints else []


def _extract_heading(text: str) -> str:
    """Extract the nearest section heading from chunk text."""
    lines = text.strip().split("\n")
    for line in lines[:3]:
        stripped = line.strip()
        if len(stripped) < 60 and (
            re.match(r"^(第[一二三四五六七八九十\d]+[章节])", stripped)
            or re.match(r"^(路线\s*[一二三四五六七八九十\d]+)", stripped)
            or re.match(r"^[\d一二三四五六七八九十]+[、．.]", stripped)
        ):
            return stripped
    return ""


# ---------------------------------------------------------------------------
# Hierarchy building
# ---------------------------------------------------------------------------

def build_hierarchy(chunks: list[Chunk]) -> dict[str, list[str]]:
    """
    Build stratigraphic hierarchy from chunk data.
    Maps parent (系/统) → children (组/段).
    """
    hierarchy: dict[str, set[str]] = defaultdict(set)

    # Known Chinese stratigraphic hierarchy
    known = {
        "二叠系": ["茅口组", "栖霞组", "峨眉山玄武岩组", "龙潭组", "长兴组", "大隆组"],
        "三叠系": ["飞仙关组", "嘉陵江组", "雷口坡组", "须家河组", "垮洪洞组"],
        "下三叠统": ["飞仙关组", "嘉陵江组"],
        "中三叠统": ["雷口坡组"],
        "上三叠统": ["须家河组", "垮洪洞组"],
        "侏罗系": ["自流井组", "沙溪庙组", "遂宁组", "蓬莱镇组"],
        "白垩系": ["夹关组", "灌口组", "名山组"],
        "下白垩统": ["夹关组"],
        "上白垩统": ["灌口组", "名山组"],
    }

    # Also extract from text: if a chunk contains both "XX系" and "YY组",
    # infer the hierarchy
    for chunk in chunks:
        systems = [f for f in chunk.formations if f.endswith("系") or f.endswith("统")]
        formations = [f for f in chunk.formations if f.endswith("组")]
        for sys in systems:
            for fm in formations:
                hierarchy[sys].add(fm)

    # Merge known hierarchy
    for k, v in known.items():
        hierarchy[k].update(v)

    return {k: list(v) for k, v in hierarchy.items()}


# ---------------------------------------------------------------------------
# Index building
# ---------------------------------------------------------------------------

def build_indices(chunks: list[Chunk], hierarchy: dict[str, list[str]]):
    """
    Build three indices:
    1. exact_index:  formation/structure name → chunk_ids
    2. semantic_index: TF-IDF matrix + vectorizer
    3. route_index:   route_id → chunk_ids (for route-biased reranking)
    """
    INDEX_DIR.mkdir(parents=True, exist_ok=True)

    # --- Exact match index ---
    exact_index: dict[str, list[str]] = defaultdict(list)
    for chunk in chunks:
        for fm in chunk.formations:
            exact_index[fm].append(chunk.id)
        for st in chunk.structures:
            exact_index[st].append(chunk.id)
        for lith in chunk.lithologies:
            exact_index[lith].append(chunk.id)

    # --- Semantic index (TF-IDF) ---
    texts = [chunk.text for chunk in chunks]
    vectorizer = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        token_pattern=r"(?u)\b\w+\b",  # Chinese chars are treated as "words"
        # Actually Chinese needs character-level. Let's use a custom analyzer.
        analyzer="char_wb",
    )
    tfidf_matrix = vectorizer.fit_transform(texts)

    # --- Route index ---
    route_index: dict[str, list[str]] = defaultdict(list)
    for chunk in chunks:
        for route in chunk.route_hints:
            route_index[route].append(chunk.id)

    # --- Save ---
    # Chunks
    with open(INDEX_DIR / "chunks.json", "w", encoding="utf-8") as f:
        json.dump([asdict(chunk) for chunk in chunks], f, ensure_ascii=False, indent=2)

    # Exact index
    with open(INDEX_DIR / "exact_index.json", "w", encoding="utf-8") as f:
        json.dump(dict(exact_index), f, ensure_ascii=False, indent=2)

    # TF-IDF
    with open(INDEX_DIR / "vectorizer.pkl", "wb") as f:
        pickle.dump(vectorizer, f)
    with open(INDEX_DIR / "tfidf_matrix.npy", "wb") as f:
        np.save(f, tfidf_matrix.toarray())

    # Route index
    with open(INDEX_DIR / "route_index.json", "w", encoding="utf-8") as f:
        json.dump(dict(route_index), f, ensure_ascii=False, indent=2)

    # Hierarchy
    with open(INDEX_DIR / "hierarchy.json", "w", encoding="utf-8") as f:
        json.dump(hierarchy, f, ensure_ascii=False, indent=2)

    # Metadata
    with open(INDEX_DIR / "meta.json", "w", encoding="utf-8") as f:
        json.dump({
            "total_chunks": len(chunks),
            "total_formations": len(exact_index),
            "vectorizer_features": len(vectorizer.get_feature_names_out()),
            "routes_indexed": list(route_index.keys()),
        }, f, ensure_ascii=False, indent=2)

    print(f"\n  Indexed {len(chunks)} chunks")
    print(f"  Exact match keys: {len(exact_index)}")
    print(f"  TF-IDF features:  {len(vectorizer.get_feature_names_out())}")
    print(f"  Routes indexed:   {list(route_index.keys())}")


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

class RAGSearch:
    """Loads indices and performs hybrid search."""

    def __init__(self):
        self.chunks: dict[str, Chunk] = {}
        self.exact_index: dict[str, list[str]] = {}
        self.route_index: dict[str, list[str]] = {}
        self.hierarchy: dict[str, list[str]] = {}
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix: Optional[np.ndarray] = None
        self._loaded = False

    def load(self):
        """Load all indices from disk."""
        if self._loaded:
            return

        if not (INDEX_DIR / "chunks.json").exists():
            raise FileNotFoundError(
                f"Index not found at {INDEX_DIR}. Run 'python pipeline.py index' first."
            )

        with open(INDEX_DIR / "chunks.json", "r", encoding="utf-8") as f:
            chunk_dicts = json.load(f)
            self.chunks = {d["id"]: Chunk(**d) for d in chunk_dicts}

        with open(INDEX_DIR / "exact_index.json", "r", encoding="utf-8") as f:
            self.exact_index = json.load(f)

        with open(INDEX_DIR / "route_index.json", "r", encoding="utf-8") as f:
            self.route_index = json.load(f)

        with open(INDEX_DIR / "hierarchy.json", "r", encoding="utf-8") as f:
            self.hierarchy = json.load(f)

        with open(INDEX_DIR / "vectorizer.pkl", "rb") as f:
            self.vectorizer = pickle.load(f)

        self.tfidf_matrix = np.load(INDEX_DIR / "tfidf_matrix.npy")

        self.chunk_ids = list(self.chunks.keys())
        self._loaded = True

    def search(
        self,
        query: str,
        current_route: Optional[str] = None,
        top_k: int = 5,
    ) -> list[SearchResult]:
        """
        Hybrid search: exact → semantic → hierarchy → rerank.

        Parameters
        ----------
        query : str
            Search query in Chinese or English.
        current_route : str, optional
            e.g. "emeishan-2" — boosts results from this route.
        top_k : int
            Number of results to return.

        Returns
        -------
        list[SearchResult]
            Ranked search results with citations.
        """
        if not self._loaded:
            self.load()

        scored: dict[str, SearchResult] = {}

        # ---- Phase 1: Exact match -------------------------------------------
        query_entities = _extract_entities(query)
        exact_matches: set[str] = set()
        for key in (query_entities["formations"]
                    + query_entities["structures"]
                    + query_entities["lithologies"]):
            if key in self.exact_index:
                for cid in self.exact_index[key]:
                    exact_matches.add(cid)
                    chunk = self.chunks[cid]
                    scored[cid] = SearchResult(
                        chunk_id=cid,
                        score=1.0,
                        text=chunk.text,
                        source=chunk.source,
                        filename=chunk.filename,
                        page=chunk.page,
                        page_image=chunk.page_image,
                        formations=chunk.formations,
                        structures=chunk.structures,
                        route_hints=chunk.route_hints,
                        match_type="exact",
                    )

        # ---- Phase 2: Hierarchy expansion -----------------------------------
        hierarchy_hits: set[str] = set()
        for entity in (query_entities["formations"]
                       + query_entities["structures"]):
            if entity in self.hierarchy:
                for child in self.hierarchy[entity]:
                    if child in self.exact_index:
                        for cid in self.exact_index[child]:
                            hierarchy_hits.add(cid)
                            if cid not in scored:
                                chunk = self.chunks[cid]
                                scored[cid] = SearchResult(
                                    chunk_id=cid, score=0.7,
                                    text=chunk.text,
                                    source=chunk.source,
                                    filename=chunk.filename,
                                    page=chunk.page,
                                    page_image=chunk.page_image,
                                    formations=chunk.formations,
                                    structures=chunk.structures,
                                    route_hints=chunk.route_hints,
                                    match_type="hierarchy",
                                )

        # ---- Phase 3: Semantic search (TF-IDF) ------------------------------
        try:
            query_vec = self.vectorizer.transform([query])
            sims = cosine_similarity(query_vec, self.tfidf_matrix)[0]
            top_indices = np.argsort(sims)[::-1][:top_k * 3]
            for idx in top_indices:
                if sims[idx] < 0.05:  # threshold
                    continue
                cid = self.chunk_ids[idx]
                chunk = self.chunks[cid]
                score = float(sims[idx]) * 0.6  # semantic score < exact match
                if cid not in scored or score > scored[cid].score:
                    scored[cid] = SearchResult(
                        chunk_id=cid, score=score,
                        text=chunk.text,
                        source=chunk.source,
                        filename=chunk.filename,
                        page=chunk.page,
                        page_image=chunk.page_image,
                        formations=chunk.formations,
                        structures=chunk.structures,
                        route_hints=chunk.route_hints,
                        match_type="semantic",
                    )
        except Exception as e:
            # Fallback: keyword substring match
            for cid, chunk in self.chunks.items():
                if query in chunk.text and cid not in scored:
                    scored[cid] = SearchResult(
                        chunk_id=cid, score=0.3,
                        text=chunk.text,
                        source=chunk.source,
                        filename=chunk.filename,
                        page=chunk.page,
                        page_image=chunk.page_image,
                        formations=chunk.formations,
                        structures=chunk.structures,
                        route_hints=chunk.route_hints,
                        match_type="keyword",
                    )

        # ---- Phase 4: Rerank by route context -------------------------------
        results = list(scored.values())
        if current_route:
            for r in results:
                if current_route in r.route_hints:
                    r.score *= 1.3  # boost route-relevant chunks
                # Also boost if the chunk has no route hint (likely general/background)
                elif not r.route_hints:
                    r.score *= 1.0  # neutral
                else:
                    r.score *= 0.7  # penalize chunks from other routes

        # Sort by score, deduplicate near-duplicate chunks
        results.sort(key=lambda x: x.score, reverse=True)
        seen_texts = set()
        deduped = []
        for r in results:
            text_key = r.text[:80]
            if text_key not in seen_texts:
                deduped.append(r)
                seen_texts.add(text_key)

        return deduped[:top_k]


# ---------------------------------------------------------------------------
# TOC integration
# ---------------------------------------------------------------------------

_toc_cache: Optional[dict] = None


def _load_toc() -> Optional[dict]:
    """Load TOC index, cached."""
    global _toc_cache
    if _toc_cache is not None:
        return _toc_cache
    toc_file = INDEX_DIR / "toc.json"
    if toc_file.exists():
        with open(toc_file, "r", encoding="utf-8") as f:
            _toc_cache = json.load(f)
    return _toc_cache


def locate_page_in_toc(page: int) -> str:
    """Given a PDF page number, return TOC breadcrumb."""
    toc = _load_toc()
    if not toc:
        return ""
    parts = []
    for ch in toc.get("chapters", []):
        if ch["page_start"] <= page <= ch["page_end"]:
            parts.append(ch["title"])
            for child in ch.get("children", []):
                if child["page_start"] <= page <= child["page_end"]:
                    parts.append(child["title"])
                    break
            break
    return " > ".join(parts) if parts else ""


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def format_results(results: list[SearchResult], query: str) -> str:
    """Format search results for agent consumption."""
    if not results:
        return f"未找到与「{query}」相关的内容。请尝试使用更具体的术语（如地层名、构造名）。"

    lines = [f"查询「{query}」找到 {len(results)} 条结果：\n"]
    for i, r in enumerate(results, 1):
        match_label = {"exact": "精确匹配", "hierarchy": "层级匹配",
                       "semantic": "语义匹配", "keyword": "关键词匹配"}
        citation = f"来源：{r.filename} 第{r.page}页"
        toc_loc = locate_page_in_toc(r.page)
        if toc_loc:
            citation += f" | 目录：{toc_loc}"
        if r.page_image:
            citation += f" [页面图片]({r.page_image})"
        if r.route_hints:
            citation += f"（相关路线：{', '.join(r.route_hints)}）"

        # Truncate text for display
        text_preview = r.text[:300].replace("\n", " ")
        if len(r.text) > 300:
            text_preview += "..."

        lines.append(
            f"### 结果 {i} [{match_label.get(r.match_type, r.match_type)}] "
            f"score={r.score:.2f}\n"
            f"> {citation}\n\n"
            f"{text_preview}\n"
        )

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def cmd_index():
    """Build index from PDFs."""
    print("GeoIntern RAG Pipeline — Index Builder")
    print("=" * 50)

    pdf_files = list(RAG_DIR.glob("**/*.pdf"))
    if not pdf_files:
        print("\n  No PDFs found in references/rag/")
        print("  Put your internship guidebook PDF in:")
        print(f"    {RAG_DIR / 'guidebook'}/")
        print(f"    {RAG_DIR / 'textbook'}/")
        sys.exit(0)

    print(f"\n  Found {len(pdf_files)} PDF(s):")
    for p in pdf_files:
        print(f"    - {p.relative_to(RAG_DIR)}")

    print("\n[1/4] Extracting text from PDFs...")
    documents = extract_pdfs()
    if not documents:
        print("  No text extracted. Check PDF files.")
        sys.exit(1)

    print(f"\n[2/4] Chunking {len(documents)} pages by geological entities...")
    chunks = chunk_documents(documents)
    if not chunks:
        print("  No chunks created.")
        sys.exit(1)

    print(f"\n[3/4] Building hierarchy...")
    hierarchy = build_hierarchy(chunks)
    print(f"  Hierarchy entries: {len(hierarchy)}")

    print(f"\n[4/4] Building indices...")
    build_indices(chunks, hierarchy)

    # Auto-build TOC after indexing
    print(f"\n[5/5] Building table of contents...")
    try:
        import subprocess
        toc_script = str(ROOT_DIR / "references" / "rag" / "build_toc.py")
        result = subprocess.run(
            [sys.executable, toc_script],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print("  TOC built successfully.")
        else:
            print(f"  TOC build warning: {result.stderr[:200]}")
    except Exception as e:
        print(f"  TOC build skipped: {e}")

    print("\nDone. Index ready at:", str(INDEX_DIR))


def cmd_search():
    """Search the index."""
    import argparse
    parser = argparse.ArgumentParser(description="GeoIntern RAG Search")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--route", "-r", default=None,
                        help="Current route (e.g. emeishan-2)")
    parser.add_argument("--top", "-k", type=int, default=5,
                        help="Number of results")
    parser.add_argument("--json", action="store_true",
                        help="Output as JSON")
    args = parser.parse_args()

    searcher = RAGSearch()
    try:
        searcher.load()
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    results = searcher.search(args.query, current_route=args.route, top_k=args.top)

    if args.json:
        output = []
        for r in results:
            output.append({
                "score": r.score,
                "match_type": r.match_type,
                "text": r.text,
                "source": r.source,
                "filename": r.filename,
                "page": r.page,
                "formations": r.formations,
                "structures": r.structures,
                "route_hints": r.route_hints,
            })
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print(format_results(results, args.query))


def cmd_toc():
    """Show table of contents or locate a page."""
    toc = _load_toc()
    if not toc:
        print("TOC not built yet. Run 'python pipeline.py index' first.")
        return

    if len(sys.argv) > 2:
        # Locate a specific page
        try:
            page = int(sys.argv[2])
            loc = locate_page_in_toc(page)
            if loc:
                print(f"p{page} → {loc}")
            else:
                print(f"p{page}: 不在目录范围内")
        except ValueError:
            # Search TOC by keyword
            query = sys.argv[2]
            _print_toc_search(toc, query)
    else:
        # Print full TOC
        toc_md = INDEX_DIR / "toc.md"
        if toc_md.exists():
            print(toc_md.read_text(encoding="utf-8"))
        else:
            print(json.dumps(toc, ensure_ascii=False, indent=2))


def _print_toc_search(toc: dict, query: str):
    """Search TOC entries for a keyword."""
    found = []

    def _search(entries, path=""):
        for e in entries:
            fp = f"{path} > {e['title']}" if path else e['title']
            if query in e['title']:
                found.append((fp, e['page_start'], e['page_end']))
            if e.get("children"):
                _search(e["children"], fp)

    _search(toc.get("chapters", []))
    if found:
        print(f"TOC 中匹配「{query}」的条目：")
        for title, start, end in found:
            print(f"  {title} (p{start}-p{end})")
    else:
        print(f"TOC 中未找到「{query}」")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python pipeline.py index              # Build index from PDFs")
        print("  python pipeline.py search <query>     # Search with optional --route")
        print("  python pipeline.py toc [page|keyword] # Show TOC or locate a page")
        sys.exit(0)

    cmd = sys.argv[1]
    if cmd == "index":
        sys.argv = [sys.argv[0]]  # clear args for argparser in search
        cmd_index()
    elif cmd == "toc":
        sys.argv = [sys.argv[0]] + sys.argv[2:]
        cmd_toc()
    elif cmd == "search":
        sys.argv = [sys.argv[0]] + sys.argv[2:]
        cmd_search()
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
