# tftools/booknm.py
from __future__ import annotations
from functools import lru_cache
import re
import difflib
from typing import Dict, Iterable, Tuple

# --- Your BHS → SBL mapping (as provided) -----------------------------------
BHS_TO_SBL: Dict[str, str] = {
    'Genesis': 'Gen',
    'Exodus': 'Exod',
    'Leviticus': 'Lev',
    'Numeri': 'Num',
    'Deuteronomium': 'Deut',
    'Josua': 'Josh',
    'Judices': 'Judg',
    'Ruth': 'Ruth',
    'Samuel_I': '1 Sam',
    'Samuel_II': '2 Sam',
    'Reges_I': '1 Kgs',
    'Reges_II': '2 Kgs',
    'Chronica_I': '1 Chr',
    'Chronica_II': '2 Chr',
    'Esra': 'Ezra',
    'Nehemia': 'Neh',
    'Esther': 'Esth',
    'Iob': 'Job',
    'Psalmi': 'Ps',
    'Proverbia': 'Prov',
    'Ecclesiastes': 'Eccl',
    'Canticum': 'Song',
    'Jesaia': 'Isa',
    'Jeremia': 'Jer',
    'Threni': 'Lam',
    'Ezechiel': 'Ezek',
    'Daniel': 'Dan',
    'Hosea': 'Hos',
    'Joel': 'Joel',
    'Amos': 'Amos',
    'Obadia': 'Obad',
    'Jona': 'Jonah',
    'Micha': 'Mic',
    'Nahum': 'Nah',
    'Habakuk': 'Hab',
    'Zephania': 'Zeph',
    'Haggai': 'Hag',
    'Sacharia': 'Zech',
    'Maleachi': 'Mal',
}

# --- English → SBL (OT) to catch what TF often emits via T.sectionFromNode ---
EN_TO_SBL: Dict[str, str] = {
    'Genesis':'Gen','Exodus':'Exod','Leviticus':'Lev','Numbers':'Num','Deuteronomy':'Deut',
    'Joshua':'Josh','Judges':'Judg','Ruth':'Ruth',
    '1 Samuel':'1 Sam','2 Samuel':'2 Sam','1 Kings':'1 Kgs','2 Kings':'2 Kgs',
    '1 Chronicles':'1 Chr','2 Chronicles':'2 Chr',
    'Ezra':'Ezra','Nehemiah':'Neh','Esther':'Esth','Job':'Job','Psalms':'Ps','Psalm':'Ps',
    'Proverbs':'Prov','Ecclesiastes':'Eccl',
    'Song of Songs':'Song','Song of Solomon':'Song','Canticles':'Song','Song':'Song',
    'Isaiah':'Isa','Jeremiah':'Jer','Lamentations':'Lam','Ezekiel':'Ezek','Daniel':'Dan',
    'Hosea':'Hos','Joel':'Joel','Amos':'Amos','Obadiah':'Obad','Jonah':'Jonah',
    'Micah':'Mic','Nahum':'Nah','Habakkuk':'Hab','Zephaniah':'Zeph','Haggai':'Hag',
    'Zechariah':'Zech','Malachi':'Mal',
}

# Optionally extend with NT if you ever need SBL NT abbreviations:
# EN_NT_TO_SBL = { 'Matthew':'Matt', 'Mark':'Mark', ... }  # (omitted by default)

ROMAN_TO_ARABIC = {
    "I":"1","II":"2","III":"3","IV":"4","V":"5","VI":"6","VII":"7","VIII":"8","IX":"9","X":"10",
}

def _denoise(s: str) -> str:
    s = s.strip().lower()
    # normalize multiple whitespace/punct variants
    s = re.sub(r"[\u00A0\s._\-]+", " ", s)  # collapse whitespace/punct to spaces
    s = s.replace("’", "'").replace("‘","'").replace("´","'")
    return s

def _roman_prefix_to_arabic(s: str) -> str:
    m = re.match(r"^(i{1,3}|iv|v|vi{0,3}|ix|x)\b", s.strip(), re.I)
    if not m:
        return s
    r = m.group(1).upper()
    return s.replace(m.group(1), ROMAN_TO_ARABIC.get(r, r), 1).strip()

def _strip_nonword(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s)

def _all_alias_keys(name: str) -> Iterable[str]:
    """
    Yield a few normalized aliases for a name:
    - raw denoised
    - roman-to-arabic prefix variant
    - fully squashed alnum
    """
    d = _denoise(name)
    yield d
    ra = _roman_prefix_to_arabic(d)
    if ra != d:
        yield ra
    yield _strip_nonword(d)
    if ra != d:
        yield _strip_nonword(ra)

def _expand_numbered_bhs(bhs_key: str) -> Iterable[str]:
    """
    For e.g. 'Samuel_I' -> '1 Samuel', '1Sam', 'I Samuel', 'First Samuel', etc.
    For non-numbered names, yields the humanized form.
    """
    nice = bhs_key.replace("_", " ")
    yield nice
    m = re.search(r"(.*)\s+(i{1,3}|iv|v|vi{0,3}|ix|x)$", nice, re.I)
    if m:
        base, roman = m.groups()
        arab = ROMAN_TO_ARABIC.get(roman.upper(), roman)
        yield f"{arab} {base}"
        yield f"{arab}{base.replace(' ', '')}"
        yield f"{roman} {base}"
        # common short book-base variants
        short = {
            "Samuel":"Sam", "Reges":"Kgs", "Chronica":"Chr"
        }.get(base, base)
        yield f"{arab} {short}"
        yield f"{roman} {short}"

# Build a single alias->SBL table from BHS + English names
def _build_alias_map() -> Dict[str, str]:
    amap: Dict[str, str] = {}

    # 1) From your BHS table
    for bhs_name, sbl in BHS_TO_SBL.items():
        # humanized BHS (underscores to spaces) plus generated numbered variants
        for alias in _expand_numbered_bhs(bhs_name):
            for key in _all_alias_keys(alias):
                amap.setdefault(key, sbl)
        # also the original key forms
        for key in _all_alias_keys(bhs_name):
            amap.setdefault(key, sbl)

    # 2) From English names (often what TF gives)
    for en_name, sbl in EN_TO_SBL.items():
        for key in _all_alias_keys(en_name):
            amap.setdefault(key, sbl)

    # 3) A few extra historical/alt spellings → SBL
    extras = {
        "jesaiah":"Isa", "isaias":"Isa",
        "jeremias":"Jer", "ezechiel":"Ezek",
        "zecharias":"Zech", "sacharia":"Zech",
        "jonas":"Jonah", "jonah":"Jonah",
        "psalmi":"Ps", "psalter":"Ps", "ps":"Ps",
        "canticles":"Song", "songofsolomon":"Song", "songofsongs":"Song", "song":"Song",
        "lamentations":"Lam","threni":"Lam",
        "obadia":"Obad","obadiah":"Obad",
        "micha":"Mic","micah":"Mic",
        "nahum":"Nah","habakuk":"Hab","zephania":"Zeph","haggai":"Hag",
        "numeri":"Num","deuteronomium":"Deut","judices":"Judg","josua":"Josh",
        "regesi":"1 Kgs","regesii":"2 Kgs","chronicai":"1 Chr","chronicaii":"2 Chr",
        "samueli":"1 Sam","samuelii":"2 Sam",
    }
    for alias, sbl in extras.items():
        amap.setdefault(alias, sbl)

    return amap

_ALIAS_TO_SBL = _build_alias_map()

@lru_cache(maxsize=1024)
def to_sbl(book_like: str, *, strict: bool = False) -> str:
    """
    Convert a user/book string (any variant) into SBL abbreviation.
    - strict=False (default): fuzzy fallback with suggestions
    - strict=True: raise ValueError if not recognized
    """
    if not isinstance(book_like, str):
        raise TypeError("book_like must be a string")

    # Fast path: direct key hits
    for key in _all_alias_keys(book_like):
        if key in _ALIAS_TO_SBL:
            return _ALIAS_TO_SBL[key]

    # Fuzzy suggestion if non-strict
    if not strict:
        # Build candidates list once
        candidates = list(_ALIAS_TO_SBL.keys())
        probe = _strip_nonword(_denoise(book_like))
        hits = difflib.get_close_matches(probe, candidates, n=1, cutoff=0.80)
        if hits:
            return _ALIAS_TO_SBL[hits[0]]

    raise ValueError(f"Unknown book: {book_like!r}. (strict={strict})")

def citation(book_like: str, chapter: int | str, verse: int | str | None = None) -> str:
    """
    Produce an SBL-style citation like 'Gen 1:1' or '1 Kgs 3'.
    """
    b = to_sbl(book_like, strict=False)
    if verse is None:
        return f"{b} {chapter}"
    return f"{b} {chapter}:{verse}"