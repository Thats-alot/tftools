# tftools/tfio.py
from __future__ import annotations
from typing import Optional, Tuple, Any

def load_dataset(
    spec: str,
    *,
    version: Optional[str] = None,
    mod: Optional[str] = None,
    ns: Optional[dict] = None,
    aliases: Tuple[str, ...] | None = None,
    include_S: bool = True,
    verbose: bool = True,
):
    """
    Load a Text-Fabric dataset via tf.app.use and return (A, F, L, T, S?).
    If ns=globals() and aliases are provided, hoist those names into the caller's namespace.

    aliases:
      - 3 names -> F, L, T
      - 4 names -> F, L, T, S   (S will be None if not present)
    """
    from tf.app import use

    if verbose:
        print(f"📦 use('{spec}', version={version!r}, mod={mod!r})")

    A = use(spec, version=version, mod=mod, hoist=False)
    F, L, T = A.api.F, A.api.L, A.api.T
    S = getattr(A.api, "S", None) if include_S else None

    if ns is not None and aliases:
        vals = (F, L, T, S)[: len(aliases)]
        ns.update(dict(zip(aliases, vals)))

    return (A, F, L, T, S)

# --- Convenience wrappers matching your preferred names ----------------------

def load_bhsa(ns=None, version: str = "2021", mod: str = "CenterBLC/BHSaddons/tf", verbose: bool = True):
    """
    Loads BHSA (BHS) and hoists: Fbhs, Lbhs, Tbhs, Sbhs
    """
    return load_dataset(
        "etcbc/bhsa",
        version=version,
        mod=mod,
        ns=ns,
        aliases=("Fbhs", "Lbhs", "Tbhs", "Sbhs"),
        include_S=True,
        verbose=verbose,
    )

def load_lxx_1935(ns=None, version: str = "1935", verbose: bool = True):
    """
    Loads CenterBLC LXX (1935) and hoists: Flxx, Llxx, Tlxx, Slxx
    """
    return load_dataset(
        "CenterBLC/LXX",
        version=version,
        mod=None,
        ns=ns,
        aliases=("Flxx", "Llxx", "Tlxx", "Slxx"),
        include_S=True,
        verbose=verbose,
    )

def load_dss(ns=None, version: str = "1.9", verbose: bool = True):
    """
    Loads ETCBC DSS and hoists: Fdss, Ldss, Tdss, Sdss
    """
    return load_dataset(
        "etcbc/dss",
        version=version,
        mod=None,
        ns=ns,
        aliases=("Fdss", "Ldss", "Tdss", "Sdss"),
        include_S=True,
        verbose=verbose,
    )

def load_macula_lxx_linkp(ns=None, version: str = "0.0.8", verbose: bool = True):
    """
    Loads Macula LXX-Link-P and hoists: Fhb, Lhb, Thb
    (no S in this app)
    """
    A, F, L, T, S = load_dataset(
        "sergpanf/LXX-Link-P",
        version=version,
        mod=None,
        ns=ns,
        aliases=("Fhb", "Lhb", "Thb"),
        include_S=False,
        verbose=verbose,
    )
    return (A, F, L, T, S)

def load_n1904(ns=None, version: str = "1.0.0", mod: str = "CenterBLC/N1904/BOLcomplement/tf/", verbose: bool = True):
    """
    Loads CenterBLC N1904 (+ BOLcomplement) and hoists: Fgnt, Lgnt, Tgnt, Sgnt
    """
    return load_dataset(
        "CenterBLC/N1904",
        version=version,
        mod=mod,
        ns=ns,
        aliases=("Fgnt", "Lgnt", "Tgnt", "Sgnt"),
        include_S=True,
        verbose=verbose,
    )