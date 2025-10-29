from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple, Iterable

# ---- Dataset specs & hoisted names -----------------------------------------

@dataclass(frozen=True)
class DatasetSpec:
    spec: str
    version: Optional[str] = None
    mod: Optional[str] = None
    hoist_names: Tuple[str, ...] = ()  # names to inject into ns in this order: F, L, T, (S)

DEFAULT_SPECS: Dict[str, DatasetSpec] = {
    "B": DatasetSpec("etcbc/bhsa", "2021", "CenterBLC/BHSaddons/tf",
                     ("Fbhs","Lbhs","Tbhs","Sbhs")),
    "L": DatasetSpec("CenterBLC/LXX", "1935", None,
                     ("Flxx","Llxx","Tlxx","Slxx")),
    "D": DatasetSpec("etcbc/dss", "1.9", None,
                     ("Fdss","Ldss","Tdss","Sdss")),
    "M": DatasetSpec("sergpanf/LXX-Link-P", "0.0.8", None,
                     ("Fhb","Lhb","Thb")),  # no S
    "N": DatasetSpec("CenterBLC/N1904", "1.0.0", "CenterBLC/N1904/BOLcomplement/tf/",
                     ("Fgnt","Lgnt","Tgnt","Sgnt")),
}

# ---- Tiny sentinels so you can call load_dataset(B) etc. -------------------

class _Key(str): pass
B = _Key("B"); BHSA = B
L = _Key("L"); LXX  = L
D = _Key("D"); DSS  = D
M = _Key("M"); MACULA = M
N = _Key("N"); GNT  = N

# Accept many spellings
_ALIASES: Dict[str, str] = {
    "b":"B","bhsa":"B","bhsa2021":"B",
    "l":"L","lxx":"L","centerblc/lxx":"L","lxx1935":"L",
    "d":"D","dss":"D",
    "m":"M","macula":"M","lxx-link-p":"M","linkp":"M","lxxlinkp":"M",
    "n":"N","gnt":"N","n1904":"N",
}

def _resolve_ns(ns):
    if ns is not None:
        return ns
    # Prefer IPython's notebook namespace when present (Jupyter/VS Code)
    try:
        from IPython import get_ipython
        ip = get_ipython()
        if ip is not None and hasattr(ip, "user_ns"):
            return ip.user_ns
    except Exception:
        pass
    # Fallback: caller's globals
    import inspect
    fr = inspect.currentframe()
    try:
        return fr.f_back.f_globals if fr and fr.f_back else globals()
    finally:
        del fr

def _normalize_keys(which: Iterable[Any]) -> Tuple[str, ...]:
    out: list[str] = []
    for w in which:
        if isinstance(w, _Key):
            key = str(w)
        elif isinstance(w, str):
            key = _ALIASES.get(w.strip().lower(), None)
            if key is None:
                # allow exact canonical names too
                key = w.strip().upper()
        else:
            raise TypeError(f"Unsupported dataset selector: {w!r}")
        if key not in DEFAULT_SPECS:
            raise ValueError(f"Unknown dataset key/name: {w!r}")
        if key not in out:
            out.append(key)
    return tuple(out)

# ---- The one function you call ---------------------------------------------

def load_dataset(*which: Any, ns: dict | None = None, verbose: bool = True):
    """
    Minimal-typing loader.

    Usage:
      load_dataset()                -> loads ALL (B,L,D,M,N) and hoists names into caller globals
      load_dataset(B)               -> BHSA only
      load_dataset("BHSA")          -> BHSA only
      load_dataset(L, "GNT")        -> LXX (1935) + N1904
      load_dataset("macula", "dss") -> Macula LXX-Link-P + DSS

    Hoisted names:
      B: Fbhs, Lbhs, Tbhs, Sbhs
      L: Flxx, Llxx, Tlxx, Slxx
      D: Fdss, Ldss, Tdss, Sdss
      M: Fhb,  Lhb,  Thb
      N: Fgnt, Lgnt, Tgnt, Sgnt

    Returns a dict like:
      {"B":{"A":A,"F":F,"L":L,"T":T,"S":S}, "L":{...}, ...}
    """
    from tf.app import use

    ns = _resolve_ns(ns)
    keys: Tuple[str, ...] = _normalize_keys(which) if which else ("B","L","D","M","N")

    bag: Dict[str, Dict[str, Any]] = {}

    for k in keys:
        spec = DEFAULT_SPECS[k]
        if verbose:
            print(f"📦 Loading {k}: {spec.spec} (version={spec.version}, mod={spec.mod})")
        try:
            A = use(spec.spec, version=spec.version, mod=spec.mod, hoist=False)
        except Exception as e:
            msg = str(e)
            if "rate limit" in msg.lower() or "403" in msg:
                print("⚠️ GitHub rate-limit while fetching TF data. "
                      "Export GHPERS=<your-token> in your shell and retry.")
            raise
        F, Lx, T = A.api.F, A.api.L, A.api.T
        S = getattr(A.api, "S", None)

        # Hoist with your preferred names
        if spec.hoist_names:
            vals = (F, Lx, T, S)[:len(spec.hoist_names)]
            ns.update(dict(zip(spec.hoist_names, vals)))

        bag[k] = {"A": A, "F": F, "L": Lx, "T": T, "S": S}

    return bag

# ultra-short alias if you want: tt.ld(...)
ld = load_dataset