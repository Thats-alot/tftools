# tftools/core.py
from __future__ import annotations
from typing import Any, Iterable, List, Optional, Tuple
from functools import lru_cache
from .booknm import to_sbl

# --- NEW: find the right namespace (Jupyter-friendly) -----------------------
def _user_ns():
    try:
        from IPython import get_ipython
        ip = get_ipython()
        if ip is not None and hasattr(ip, "user_ns"):
            return ip.user_ns
    except Exception:
        pass
    return None

# --- NEW: resolve a dataset key like "B" -> the right T object --------------
def _T_from_dskey(dskey: str):
    ns = _user_ns() or globals()
    k = (dskey or "").strip().upper()
    # candidates: T object names and app names you already use
    candidates = {
        "B": ["Tbhs", "B", "BHSA", "BHS"],
        "BHSA": ["Tbhs", "B", "BHSA", "BHS"],
        "L": ["Tlxx", "L", "LXX"],
        "LXX": ["Tlxx", "L", "LXX"],
        "M": ["Thb", "M", "MACULA"],
        "MACULA": ["Thb", "M", "MACULA"],
        "D": ["Tdss", "D", "DSS"],
        "DSS": ["Tdss", "D", "DSS"],
        "N": ["Tgnt", "N", "GNT", "N1904"],
        "GNT": ["Tgnt", "N", "GNT", "N1904"],
    }.get(k, [])
    for name in candidates:
        if name in ns:
            obj = ns[name]
            # If it's an app (B/L/M/...), grab its T
            if hasattr(obj, "api") and hasattr(obj.api, "T"):
                return obj.api.T
            # If it's already a T object
            if hasattr(obj, "sectionFromNode"):
                return obj
    raise NameError(
        f"Could not find a Text-Fabric T for dataset '{dskey}'. "
        f"Make sure you've run your usual use(...), e.g. B = use(...); Tbhs = B.api.T"
    )

# --- UPDATED: getref accepts (T, node) OR (node, 'B') -----------------------
def getref(arg1, arg2=None, *, style: str = "sbl") -> str:
    """
    getref(T, node, style='sbl'|'dataset')
    getref(node, 'B', style='sbl'|'dataset')   # 'B','BHSA','L','M','D','N' accepted
    """
    # case 1: legacy form getref(T, node)
    if hasattr(arg1, "sectionFromNode"):
        T, node = arg1, int(arg2)
    else:
        # case 2: new form getref(node, 'B')
        node, dskey = int(arg1), arg2
        if not isinstance(dskey, str):
            raise TypeError("When calling getref(node, dskey), dskey must be a string like 'B' or 'BHSA'.")
        T = _T_from_dskey(dskey)

    book, chap, verse = T.sectionFromNode(node)
    if book is None:
        return "?"
    book_out = to_sbl(book, strict=False) if style.lower() == "sbl" else book
    if chap is None:
        return f"{book_out}"
    if verse is None:
        return f"{book_out} {chap}"
    return f"{book_out} {chap}:{verse}"