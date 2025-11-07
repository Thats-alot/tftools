# tftools/api.py
from __future__ import annotations
from typing import Iterable, List, Dict, Any, Tuple, Optional, Union
import re

# ---------- namespace & dataset resolution ----------

_ALIASES = {
    "b": "B", "bhsa": "B",
    "l": "L", "lxx": "L",
    "m": "M", "macula": "M",
    "d": "D", "dss": "D",
    "n": "N", "gnt": "N", "n1904": "N",
}

def _user_ns():
    try:
        from IPython import get_ipython
        ip = get_ipython()
        if ip is not None and hasattr(ip, "user_ns"):
            return ip.user_ns
    except Exception:
        pass
    return globals()

def _resolve_ds(ds: str) -> Tuple[Any, Any, Any]:
    """Return (F, L, T) from a dataset key like 'B','L','M','D','N' or names."""
    ns = _user_ns()
    key = _ALIASES.get((ds or "").strip().lower(), None) or (ds or "").strip().upper()
    mapping = {
        "B": ("Fbhs", "Lbhs", "Tbhs"),
        "L": ("Flxx", "Llxx", "Tlxx"),
        "M": ("Fhb",  "Lhb",  "Thb"),
        "D": ("Fdss", "Ldss", "Tdss"),
        "N": ("Fgnt", "Lgnt", "Tgnt"),
    }
    if key not in mapping:
        raise NameError(f"Unknown dataset key {ds!r}. Use B/L/M/D/N (or BHSA/LXX/MACULA/DSS/GNT).")
    fn, ln, tn = mapping[key]
    try:
        return ns[fn], ns[ln], ns[tn]
    except KeyError as missing:
        raise NameError(f"Dataset {ds!r} not loaded (missing {missing.args[0]}).") from None

# ---------- SBL mapping (robust: uses tftools.booknm if available) ----------

_SBL_FALLBACK = {
    'Genesis':'Gen','Exodus':'Exod','Leviticus':'Lev','Numeri':'Num','Deuteronomium':'Deut',
    'Josua':'Josh','Judices':'Judg','Ruth':'Ruth','Samuel_I':'1 Sam','Samuel_II':'2 Sam',
    'Reges_I':'1 Kgs','Reges_II':'2 Kgs','Chronica_I':'1 Chr','Chronica_II':'2 Chr',
    'Esra':'Ezra','Nehemia':'Neh','Esther':'Esth','Iob':'Job','Psalmi':'Ps','Proverbia':'Prov',
    'Ecclesiastes':'Eccl','Canticum':'Song','Jesaia':'Isa','Jeremia':'Jer','Threni':'Lam',
    'Ezechiel':'Ezek','Daniel':'Dan','Hosea':'Hos','Joel':'Joel','Amos':'Amos','Obadia':'Obad',
    'Jona':'Jonah','Micha':'Mic','Nahum':'Nah','Habakuk':'Hab','Zephania':'Zeph','Haggai':'Hag',
    'Sacharia':'Zech','Maleachi':'Mal'
}

def _to_sbl(book: str) -> str:
    try:
        from .booknm import to_sbl as _to_sbl
        return _to_sbl(book, strict=False)
    except Exception:
        return _SBL_FALLBACK.get(book, book)

def _book_maps(F, T) -> Tuple[Dict[str, str], Dict[str, str]]:
    """
    Build two maps for this dataset:
      ds_book -> SBL, and SBL -> ds_book
    """
    ds_to_sbl: Dict[str, str] = {}
    sbl_to_ds: Dict[str, str] = {}
    for bnode in F.otype.s("book"):
        b, c, v = T.sectionFromNode(bnode)
        if b:
            s = _to_sbl(b)
            ds_to_sbl[b] = s
            sbl_to_ds[s] = b
    return ds_to_sbl, sbl_to_ds

# ---------- small TF helpers ----------

def _first_feature(F, *names) -> Optional[str]:
    for n in names:
        if hasattr(F, n):
            return n
    return None

def _verse_node_from_any(T, node: int) -> Optional[int]:
    b, c, v = T.sectionFromNode(int(node))
    if b is None or c is None or v is None:
        return None
    return T.nodeFromSection((b, c, v))

def _ref_string(T, node: int, style: str = "sbl") -> str:
    b, c, v = T.sectionFromNode(int(node))
    if b is None:
        return "?"
    out = _to_sbl(b) if style.lower() == "sbl" else b
    if c is None:
        return out
    return f"{out} {c}:{v}" if v is not None else f"{out} {c}"

def _tokens_for_vnode(F, L, T, vnode: int, *, for_ds: str) -> List[str]:
    # default per dataset; BHSA -> g_cons / g_cons_utf8
    if for_ds.upper() in {"B", "BHSA"}:
        feat = _first_feature(F, "g_cons_utf8", "g_cons")
    else:
        feat = _first_feature(F, "g_word_utf8", "text")
    if feat is None:
        feat = "text"
    fobj = getattr(F, feat)
    return [fobj.v(w) for w in L.d(vnode, otype="word")]

# ---------- parse node specs ----------

def _normalize_nodes(nodes: Union[int, str, Iterable[int]]) -> List[int]:
    """
    Accept 65, [65,72], "65-70, 91, 100-102" and return a flat list of ints.
    """
    if isinstance(nodes, int):
        return [nodes]
    if isinstance(nodes, str):
        out: List[int] = []
        for part in re.split(r"[,\s]+", nodes.strip()):
            if not part:
                continue
            if "-" in part:
                a, b = part.split("-", 1)
                out.extend(range(int(a), int(b) + 1))
            else:
                out.append(int(part))
        return out
    # iterable
    return [int(x) for x in nodes]

# ---------- parse verse specs ----------

_PART = re.compile(
    r"""
    ^\s*
    (?P<b1>[1-3]?\s*[A-Za-z.\s]+?)      # book 1 (SBL or dataset)
    \s+
    (?P<c1>\d+)
    (?:
        :(?P<v1>\d+)
        (?:\s*-\s*
            (?:
                (?P<b2>[1-3]?\s*[A-Za-z.\s]+?)\s+  # optional book 2
            )?
            (?P<c2>\d+)
            (?::(?P<v2>\d+))?
        )?
    )?
    \s*$
    """,
    re.VERBOSE | re.IGNORECASE,
)

def _sbl_to_ds_book(F, T, token: str) -> str:
    ds_to_sbl, sbl_to_ds = _book_maps(F, T)
    sbl = _to_sbl(token)
    if sbl in sbl_to_ds:
        return sbl_to_ds[sbl]
    # maybe the token is already dataset label
    if token in ds_to_sbl:
        return token
    # try capitalization-insensitive hit on dataset labels
    for dsb in ds_to_sbl:
        if dsb.lower() == token.lower():
            return dsb
    raise ValueError(f"Book not recognized in this dataset: {token!r}")

def _verses_from_spec(F, T, spec: str) -> List[int]:
    """
    Turn 'Gen 2:1-4; 3:1' or 'Genesis 2:1 - 3:10' into verse-node list.
    Also accepts commas as separators.
    """
    items = [p.strip() for p in re.split(r"[;,]", spec) if p.strip()]
    out: List[int] = []
    for item in items:
        m = _PART.match(item)
        if not m:
            raise ValueError(f"Bad verse ref segment: {item!r}")
        b1 = _sbl_to_ds_book(F, T, m.group("b1"))
        c1 = int(m.group("c1"))
        v1 = m.group("v1")
        b2 = m.group("b2")
        c2 = m.group("c2")
        v2 = m.group("v2")

        if v1 is None:
            # chapter-only: all verses in c1
            out.extend(T.nodesFromSection((b1, c1)))
            continue

        a = int(v1)
        if c2 is None:
            # single verse
            n = T.nodeFromSection((b1, c1, a))
            if n: out.append(n)
            continue

        # we have a range
        b2 = _sbl_to_ds_book(F, T, b2) if b2 else b1
        c2 = int(c2)
        z = int(v2) if v2 else None

        # same chapter
        if b1 == b2 and c1 == c2:
            for vv in range(a, z + 1 if z else a):
                n = T.nodeFromSection((b1, c1, vv))
                if n: out.append(n)
            continue

        # cross-chapter
        # start chunk: verses a..end(c1)
        start_verses = T.nodesFromSection((b1, c1))
        for n in start_verses:
            _, _, v = T.sectionFromNode(n)
            if v is not None and v >= a:
                out.append(n)
        # middle chapters
        # naive walk: increment chapter until c2 (same book)
        # (books differing are supported because b2 may differ)
        cur_b, cur_c = b1, c1 + 1
        while (cur_b != b2) or (cur_c < c2):
            out.extend(T.nodesFromSection((cur_b, cur_c)))
            cur_c += 1
        # final chunk: verses 1..z
        last_verses = T.nodesFromSection((b2, c2))
        for n in last_verses:
            _, _, v = T.sectionFromNode(n)
            if v is not None and (z is None or v <= z):
                out.append(n)
    return out

# ---------- tables ----------

def _word_table(F, L, T, vnode: int, ref_s: str, *, base_feat: str, extra: Iterable[str] | None):
    words = L.d(vnode, otype="word")
    base = getattr(F, base_feat, None)
    if base is None:
        # graceful fallback
        base_feat = _first_feature(F, "g_cons_utf8", "g_cons", "g_word_utf8", "text") or "text"
        base = getattr(F, base_feat)
    rows: List[Dict[str, Any]] = []
    for i, w in enumerate(words, start=1):
        row = {
            "node": w,
            "ref": f"{ref_s}",
            "i": i,
            "word": base.v(w),
        }
        if extra:
            for feat in extra:
                fobj = getattr(F, feat, None)
                row[feat] = fobj.v(w) if fobj else None
        rows.append(row)
    try:
        import pandas as pd  # type: ignore
        df = pd.DataFrame(rows)
        return df
    except Exception:
        return rows

# ---------- public API ----------

def getref(
    nodes: Union[int, str, Iterable[int]],
    ds: str,
    *,
    words: bool = False,
    otherFeatures: Optional[Iterable[str]] = None,
    join: Optional[str] = None,
    style: str = "sbl",
) -> Union[str, List[Any]]:
    """
    From word node id(s) -> verse ref(s), optionally verse tokens or a feature table.

    nodes:
      65                    -> single node
      [65,72]               -> many nodes
      "65-70, 91, 100-102"  -> ranges

    ds: 'B'/'BHSA', 'L'/'LXX', 'M', 'D', 'N'/'GNT'

    Modes:
      - default: print refs, return list of refs (deduped per verse)
      - words=True: for each verse, print the ref and return tokens (string if join given)
      - otherFeatures={'prs_nu',...}: print ref, and return a DataFrame per verse with columns:
          node, ref, i, word (BHSA: g_cons*), plus the requested feature columns
    """
    F, L, T = _resolve_ds(ds)
    dskey = _ALIASES.get(ds.lower(), ds).upper()

    node_list = _normalize_nodes(nodes)
    # map to unique verse nodes while preserving order
    seen_v = set()
    vnodes: List[int] = []
    for n in node_list:
        v = _verse_node_from_any(T, n)
        if v and v not in seen_v:
            seen_v.add(v)
            vnodes.append(v)

    results: List[Any] = []
    for vnode in vnodes:
        ref_s = _ref_string(T, vnode, style=style)
        print(ref_s)

        if otherFeatures:
            base_feat = "g_cons_utf8" if dskey == "B" and hasattr(F, "g_cons_utf8") else (
                        "g_cons" if dskey == "B" and hasattr(F, "g_cons") else
                        (_first_feature(F, "g_word_utf8", "text") or "text"))
            table = _word_table(F, L, T, vnode, ref_s, base_feat=base_feat, extra=otherFeatures)
            results.append(table)
            continue

        if words:
            toks = _tokens_for_vnode(F, L, T, vnode, for_ds=dskey)
            results.append(" ".join(toks) if join is not None else toks)
            if join is None:
                # also pretty print tokens on one line (quoted)
                try:
                    print(", ".join(repr(t) for t in toks))
                except Exception:
                    pass
            continue

        # refs only
        results.append(ref_s)

    return results[0] if (isinstance(nodes, int) and len(results) == 1 and not otherFeatures and not words) else results

def getver(
    verses: str,
    ds: str,
    *,
    words: bool = False,
    otherFeatures: Optional[Iterable[str]] = None,
    join: Optional[str] = None,
    style: str = "sbl",
) -> List[Any]:
    """
    From verse reference(s) -> same outputs as getref.

    Accepts:
      "Gen 1:1"
      "Genesis 1:1"
      "gen 1:1"
      "Gen 2:1-4"
      "Gen 2:1 - 3:10"
      "Ezek 1:1-3; 2:1"  (semicolon or comma separated)

    Returns a list (one item per verse) containing refs, token lists/strings, or DataFrames,
    matching the mode (words / otherFeatures / refs only).
    """
    F, L, T = _resolve_ds(ds)
    dskey = _ALIASES.get(ds.lower(), ds).upper()

    vnodes = _verses_from_spec(F, T, verses)

    results: List[Any] = []
    for vnode in vnodes:
        ref_s = _ref_string(T, vnode, style=style)
        print(ref_s)

        if otherFeatures:
            base_feat = "g_cons_utf8" if dskey == "B" and hasattr(F, "g_cons_utf8") else (
                        "g_cons" if dskey == "B" and hasattr(F, "g_cons") else
                        (_first_feature(F, "g_word_utf8", "text") or "text"))
            table = _word_table(F, L, T, vnode, ref_s, base_feat=base_feat, extra=otherFeatures)
            results.append(table)
            continue

        if words:
            toks = _tokens_for_vnode(F, L, T, vnode, for_ds=dskey)
            results.append(" ".join(toks) if join is not None else toks)
            if join is None:
                try:
                    print(", ".join(repr(t) for t in toks))
                except Exception:
                    pass
            continue

        results.append(ref_s)

    return results