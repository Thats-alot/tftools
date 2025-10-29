# tftools/refs.py
from __future__ import annotations
from typing import List, Tuple, Optional, Iterable
from functools import lru_cache
import re

from .booknm import to_sbl, citation as _citation
from .core import first_existing_feature

__all__ = [
    "ref_sbl",
    "ref_dataset",
    "cite",
    "cite_range",
    "verse_node_from_any",
    "verse_words",
    "sbl_to_dataset_book",
    "nodes_from_sbl_refs",
]

# ---------- Basic reference helpers ----------

def ref_dataset(T, node: int) -> str:
    """
    Reference using the dataset's native book label (e.g., 'Jesaia 1:1').
    Safe for any node type: word/phrase/clause/verse/chapter/book.
    """
    b, c, v = T.sectionFromNode(node)
    if b is None:
        return "?"
    if c is None:
        return f"{b}"
    if v is None:
        return f"{b} {c}"
    return f"{b} {c}:{v}"

def ref_sbl(T, node: int) -> str:
    """
    Reference in SBL notation (e.g., 'Ezek 1:1'), regardless of dataset labels.
    """
    b, c, v = T.sectionFromNode(node)
    if b is None:
        return "?"
    sb = to_sbl(b, strict=False)
    if c is None:
        return sb
    if v is None:
        return f"{sb} {c}"
    return f"{sb} {c}:{v}"

def cite(book_like: str, chapter: int | str, verse: int | str | None = None) -> str:
    """
    Build an SBL-style citation string, e.g., 'Gen 1:1' or '2 Kgs 3'.
    """
    return _citation(book_like, chapter, verse)

def cite_range(book_like: str, chapter: int | str, v1: int | str, v2: int | str) -> str:
    """
    Build an SBL-style verse range, e.g., 'Ezek 1:1–3'.
    """
    b = to_sbl(book_like, strict=False)
    return f"{b} {chapter}:{v1}\u2013{v2}"  # en dash

# ---------- Verse resolution & word dumping ----------

def verse_node_from_any(T, node: int) -> Optional[int]:
    """
    If 'node' lies inside a verse, return that verse node; else None.
    """
    b, c, v = T.sectionFromNode(node)
    if b is None or c is None or v is None:
        return None
    return T.nodeFromSection((b, c, v))

def verse_words(
    F,
    L,
    T,
    node: int,
    *,
    feature: str | Iterable[str] = "default",
) -> List[str] | List[Tuple]:
    """
    Return word-level feature values for the verse containing 'node'.

    - feature="default": tries 'g_cons_utf8' → 'g_word_utf8' → 'text'
    - feature="g_word_utf8" (LXX), "g_cons_utf8" (BHSA), "text" (GNT), etc., also fine.
    - If multiple features are given, returns list of tuples.
    """
    v = verse_node_from_any(T, node)
    if not v:
        return []

    words = L.d(v, otype="word")

    feats = (feature,) if isinstance(feature, str) else tuple(feature)
    fobjs = []
    for fname in feats:
        if fname == "default":
            fname = first_existing_feature(F, "g_cons_utf8", "g_word_utf8", "text") or "text"
        fobj = getattr(F, fname, None)
        if fobj is None:
            # try common fallbacks
            for alt in ("g_cons_utf8", "g_word_utf8", "text"):
                fobj = getattr(F, alt, None)
                if fobj is not None:
                    break
        fobjs.append(fobj)

    if len(fobjs) == 1:
        f = fobjs[0]
        return [] if f is None else [f.v(w) for w in words]

    out: List[Tuple] = []
    for w in words:
        out.append(tuple(f.v(w) if f is not None else None for f in fobjs))
    return out

# ---------- SBL → dataset book mapping & parsing ----------

@lru_cache(maxsize=64)
def _dataset_book_map(idF: int, idT: int, books_key: str = "book") -> Tuple[dict, dict]:
    """
    Build two maps for a dataset:
      - ds_book -> SBL
      - SBL -> ds_book
    We derive dataset book labels by inspecting actual book nodes.
    """
    # We can't keep F/T objects in the cache key (unhashable), so callers pass ids
    # and we stash the real objects on function attributes temporarily.
    F = _dataset_book_map._F[idF]
    T = _dataset_book_map._T[idT]

    # Collect dataset's book labels
    ds_books = []
    for bnode in F.otype.s(books_key):  # 'book' nodes
        b, c, v = T.sectionFromNode(bnode)
        if b and (not ds_books or ds_books[-1] != b):
            ds_books.append(b)

    ds_to_sbl = {b: to_sbl(b, strict=False) for b in ds_books}
    # Invert (SBL abbrevs are unique; if not, last wins)
    sbl_to_ds = {}
    for b, s in ds_to_sbl.items():
        sbl_to_ds[s] = b
    return ds_to_sbl, sbl_to_ds

# stash of live objects so _dataset_book_map can recover them from ids
_dataset_book_map._F = {}  # type: ignore[attr-defined]
_dataset_book_map._T = {}  # type: ignore[attr-defined]

def sbl_to_dataset_book(F, T, sbl: str) -> str:
    """
    Given an SBL book abbreviation (e.g., 'Ezek'), return the dataset's canonical book label
    (e.g., 'Jesaia' for BHSA/Isaiah, or 'Isaiah' for LXX/GNT datasets).
    """
    idF, idT = id(F), id(T)
    _dataset_book_map._F[idF] = F  # type: ignore[attr-defined]
    _dataset_book_map._T[idT] = T  # type: ignore[attr-defined]
    _, sbl_to_ds = _dataset_book_map(idF, idT)
    key = to_sbl(sbl, strict=False)  # normalize, in case someone passes 'Isaiah'
    if key not in sbl_to_ds:
        raise ValueError(f"SBL book {sbl!r} not recognized in this dataset")
    return sbl_to_ds[key]

# Accept things like:
#   "Ezek 1", "Ezek 1:1", "Ezek 1:1-3", "Ezek 1:1–3; 2:1; Gen 3"
_SBL_BOOK = r"[1-3]?\s*[A-Za-z]{2,}\.?"   # simple SBL-ish token
_PART = re.compile(
    rf"^\s*(?P<book>{_SBL_BOOK})\s+(?P<chap>\d+)(?::(?P<v1>\d+)(?:[\-\u2013](?P<v2>\d+))?)?\s*$",
    re.IGNORECASE,
)

def nodes_from_sbl_refs(F, T, refs: str) -> List[int]:
    """
    Parse a semicolon/comma-separated list of SBL references into verse nodes for this dataset.
    Examples:
      "Ezek 1:1-3; 2:1"
      "Gen 1; Exod 3:14"
    Chapter-only items return *all verses of that chapter*.
    """
    idF, idT = id(F), id(T)
    _dataset_book_map._F[idF] = F  # type: ignore[attr-defined]
    _dataset_book_map._T[idT] = T  # type: ignore[attr-defined]
    ds_to_sbl, sbl_to_ds = _dataset_book_map(idF, idT)

    pieces = [p.strip() for p in re.split(r"[;,]", refs) if p.strip()]
    out: List[int] = []

    last_book_sbl: Optional[str] = None
    for p in pieces:
        m = _PART.match(p)
        if not m:
            # allow shorthand like ":3" to continue previous book+chapter? too magical; raise:
            raise ValueError(f"Bad SBL ref segment: {p!r}")

        book_sbl = to_sbl(m.group("book"), strict=False)
        chap = int(m.group("chap"))
        v1 = m.group("v1")
        v2 = m.group("v2")

        # Resolve dataset book label
        ds_book = sbl_to_ds.get(book_sbl)
        if ds_book is None:
            raise ValueError(f"SBL book {book_sbl!r} not found in this dataset")

        if v1 is None:
            # all verses of chapter
            nodes = T.nodesFromSection((ds_book, chap))
            out.extend(nodes)
        else:
            a = int(v1)
            b = int(v2) if v2 else a
            for vv in range(a, b + 1):
                n = T.nodeFromSection((ds_book, chap, vv))
                if n:
                    out.append(n)

        last_book_sbl = book_sbl

    return out