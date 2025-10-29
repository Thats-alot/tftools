# tftools/datasets.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple

@dataclass(frozen=True)
class DatasetSpec:
    spec: str
    version: Optional[str] = None
    mod: Optional[str] = None
    hoist_names: Tuple[str, ...] = ()  # variables to export to ns

DEFAULT_SPECS: Dict[str, DatasetSpec] = {
    # BHS (BHSA 2021 + CenterBLC addons)
    "B": DatasetSpec(
        spec="etcbc/bhsa",
        version="2021",
        mod="CenterBLC/BHSaddons/tf",
        hoist_names=("Fbhs","Lbhs","Tbhs","Sbhs"),
    ),
    # LXX (CenterBLC 1935)
    "L": DatasetSpec(
        spec="CenterBLC/LXX",
        version="1935",
        mod=None,
        hoist_names=("Flxx","Llxx","Tlxx","Slxx"),
    ),
    # DSS (ETCBC)
    "D": DatasetSpec(
        spec="etcbc/dss",
        version="1.9",
        mod=None,
        hoist_names=("Fdss","Ldss","Tdss","Sdss"),
    ),
    # Macula LXX-Link-P (Hebrew↔Greek links)
    "M": DatasetSpec(
        spec="sergpanf/LXX-Link-P",
        version="0.0.8",
        mod=None,
        hoist_names=("Fhb","Lhb","Thb"),  # as you use them
    ),
    # GNT N1904 with BOL complement
    "N": DatasetSpec(
        spec="CenterBLC/N1904",
        version="1.0.0",
        mod="CenterBLC/N1904/BOLcomplement/tf/",
        hoist_names=("Fgnt","Lgnt","Tgnt","Sgnt"),
    ),
}

def _resolve_ns(ns):
    if ns is not None:
        return ns
    import inspect
    fr = inspect.currentframe()
    try:
        return fr.f_back.f_globals if fr and fr.f_back else globals()
    finally:
        del fr

def load_one(key: str, ns=None, *, spec: DatasetSpec | None = None, verbose=True):
    """
    Load a single dataset by key (B,L,D,M,N). Returns dict with A,F,L,T,S (S optional).
    Hoists your chosen variable names into ns (globals), matching your style.
    """
    from tf.app import use
    ns = _resolve_ns(ns)
    ds = spec or DEFAULT_SPECS[key]
    if verbose:
        print(f"📦 Loading {key}: {ds.spec} (version={ds.version}, mod={ds.mod})")
    A = use(ds.spec, version=ds.version, mod=ds.mod, hoist=False)
    api = A.api
    # Some datasets have S, some may not—guard it.
    F, L, T = api.F, api.L, api.T
    S = getattr(api, "S", None)

    # Hoist with your preferred names
    if ds.hoist_names:
        names = ds.hoist_names
        values = (F, L, T, S)[:len(names)]
        ns.update(dict(zip(names, values)))

    return {"A": A, "F": F, "L": L, "T": T, "S": S}

def load_defaults(ns=None, which=("B","L","D","M","N"), overrides: Dict[str, Dict[str, Any]] | None = None, verbose=True):
    """
    Load your standard set. Example:
        load_defaults(globals())                   # loads all B,L,D,M,N
        load_defaults(globals(), which=("B","M"))  # just BHSA + Macula
        load_defaults(globals(), overrides={"B": {"version":"2023"}})
    """
    bag = {}
    for k in which:
        spec = DEFAULT_SPECS[k]
        if overrides and k in overrides:
            spec = DatasetSpec(
                spec=overrides[k].get("spec", spec.spec),
                version=overrides[k].get("version", spec.version),
                mod=overrides[k].get("mod", spec.mod),
                hoist_names=spec.hoist_names,
            )
        bag[k] = load_one(k, ns=ns, spec=spec, verbose=verbose)
    return bag