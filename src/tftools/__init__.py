# tftools/__init__.py
"""
tftools: helpers for Text-Fabric notebooks (BHSA / LXX / DSS / Macula / N1904)

Typical use:
    import tftools as tt

    %load_ext autoreload
    %autoreload 2

    tt.quick_import(globals())    # pull pd/np/plt/... into the notebook
    tt.load_dataset()             # load ALL datasets (B, L, D, M, N) & hoist names
    # or subsets:
    tt.load_dataset(tt.B)         # BHSA only
    tt.ld(tt.M, "D")              # Macula + DSS

    v = next(iter(Tbhs.otype.s("verse")))
    tt.ref_sbl(Tbhs, v)           # 'Gen 1:1'
"""

# Optional version (fine if package metadata is absent)
try:
    from importlib.metadata import version as _pkg_version
    __version__ = _pkg_version("tftools")
except Exception:  # pragma: no cover
    __version__ = "0+local"

# Submodules as namespaces
from . import nb as nb
from . import tfio as tfio
from . import core as core
from . import booknm as booknm
from . import refs as refs
from . import getver as getver_mod

# Top-level conveniences
from .nb import quick_import

# Minimal-typing dataset loader (+ alias) and selector constants
from .tfio import load_dataset, ld, B, BHSA, L, LXX, D, DSS, M, MACULA, N, GNT

# Core helpers
from .core import (
    getref,
    verse_node,
    words_in_verse,
    first_existing_feature,
)

# Book-name normalizer (SBL)
from .booknm import (
    to_sbl,
    citation,
)

# Reference helpers
from .refs import (
    ref_sbl,
    ref_dataset,
    cite,
    cite_range,
    verse_node_from_any,
    verse_words,
    sbl_to_dataset_book,
    nodes_from_sbl_refs,
)

# Version/metadata
from .getver import (
    getver,
    printver,
)

# Lazily expose nbstrip utilities (no hard nbformat dep at import time)
try:  # pragma: no cover
    from .nbstrip import strip_outputs, truncate_outputs  # requires nbformat extra
except Exception:  # pragma: no cover
    def strip_outputs(*_args, **_kwargs):
        raise RuntimeError(
            "tftools.nbstrip.strip_outputs requires 'nbformat'. "
            "Install with: pip install -e '.[nb]'"
        )
    def truncate_outputs(*_args, **_kwargs):
        raise RuntimeError(
            "tftools.nbstrip.truncate_outputs requires 'nbformat'. "
            "Install with: pip install -e '.[nb]'"
        )

__all__ = [
    # submodules
    "nb", "tfio", "core", "booknm", "refs", "getver_mod",
    # quick import
    "quick_import",
    # dataset loading (minimal typing)
    "load_dataset", "ld", "B", "BHSA", "L", "LXX", "D", "DSS", "M", "MACULA", "N", "GNT",
    # core
    "getref", "verse_node", "words_in_verse", "first_existing_feature",
    # book names (SBL)
    "to_sbl", "citation",
    # refs
    "ref_sbl", "ref_dataset", "cite", "cite_range",
    "verse_node_from_any", "verse_words", "sbl_to_dataset_book", "nodes_from_sbl_refs",
    # version/metadata
    "getver", "printver",
    # nbstrip (lazy)
    "strip_outputs", "truncate_outputs",
    # meta
    "__version__",
]