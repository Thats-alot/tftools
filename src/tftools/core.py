# tftools/core.py
from __future__ import annotations
from typing import Any, Iterable, List, Optional, Tuple
from functools import lru_cache

from .booknm import to_sbl

def getref(T, node: int, *, style: str = "dataset") -> str:
    """
    Return a reference string for any TF node.
      style="dataset" -> uses the dataset's own book name
      style="sbl"     -> uses SBL abbreviation (via booknm.to_sbl)
    Examples: "Genesis 1:1" (dataset) or "Gen 1:1" (SBL)
    """
    book, chap, verse = T.sectionFromNode(node)
    if book is None:
        return "?"
    book_str = to_sbl(book, strict=False) if style.lower() == "sbl" else book
    if chap is None:
        return f"{book_str}"
    if verse is None:
        return f"{book_str} {chap}"
    return f"{book_str} {chap}:{verse}"

def verse_node(T, node: int) -> Optional[int]:
    """
    Resolve the verse that contains 'node', or None if not inside a verse.
    """
    b, c, v = T.sectionFromNode(node)
    if b is None or c is None or v is None:
        return None
    return T.nodeFromSection((b, c, v))

def first_existing_feature(F, *names: str) -> Optional[str]:
    """
    Return the first feature name that exists on F, or None if none exist.
    """
    for n in names:
        if hasattr(F, n):
            return n
    return None

def words_in_verse(
    F,
    L,
    T,
    node: int,
    *,
    features: Iterable[str] | str = ("g_cons_utf8", "g_word_utf8", "text"),
) -> List[str] | List[Tuple]:
    """
    Return word-level feature values for the verse containing 'node'.

    - If 'features' is a single name, returns List[str].
    - If 'features' is multiple names, returns List[Tuple[...]].
    - Falls back across common feature names if the requested one is missing.
    """
    v = verse_node(T, node)
    if not v:
        return []
    wnodes = L.d(v, otype="word")

    # normalize features to a tuple
    feats = (features,) if isinstance(features, str) else tuple(features)

    # build feature objects with fallback
    fobjs: List[Any] = []
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
        if fobj is None:
            # nothing available for this slot; keep placeholder to preserve tuple width
            fobjs.append(None)
        else:
            fobjs.append(fobj)

    if len(fobjs) == 1:
        f = fobjs[0]
        return [] if f is None else [f.v(w) for w in wnodes]

    # multiple features → tuples
    out: List[Tuple] = []
    for w in wnodes:
        row = tuple(f.v(w) if f is not None else None for f in fobjs)
        out.append(row)
    return out