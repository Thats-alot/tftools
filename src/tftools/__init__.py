# tftools/__init__.py
"""
tftools: helpers for Text-Fabric notebooks (BHSA / LXX / DSS / Macula / N1904)

Typical use:
    import tftools as tt

    %load_ext autoreload
    %autoreload 2

    tt.quick_import()              # pull pd/np/plt/sns/openpyxl/tqdm into the notebook
    tt.load_dataset()              # load ALL datasets (B, L, D, M, N) & hoist names
    # or subsets:
    tt.load_dataset(tt.B)          # BHSA only
    tt.ld(tt.M, "D")               # Macula + DSS

High-level helpers:
    tt.getref(65, "B")                     # -> prints 'Gen 1:1', returns 'Gen 1:1'
    tt.getref(65, "B", words=True)         # -> prints ref + returns list of tokens for the verse
    tt.getref(65, "B", otherFeatures={"vt","ps"})  # -> DataFrame of word rows for that verse

    tt.getver("Gen 2:1-4", "B", words=True)        # same behavior, starting from verse refs

Version/metadata (legacy):
    tt.printver(B)                  # pretty print TF/dataset metadata
    tt.getver_meta(B)               # return TFVersionInfo
"""

# --- package version ---------------------------------------------------------
try:
    from importlib.metadata import version as _pkg_version
    __version__ = _pkg_version("tftools")
except Exception:  # pragma: no cover
    __version__ = "0+local"

# --- submodules as namespaces ------------------------------------------------
from . import nb as nb
from . import tfio as tfio
from . import core as core
from . import booknm as booknm
from . import refs as refs
from . import api as api           # NEW: high-level API (getref/getver)
from . import getver as getver_mod # legacy metadata module

# --- top-level conveniences --------------------------------------------------
from .nb import quick_import

# dataset loading (minimal typing) and selector constants
from .tfio import load_dataset, ld, B, BHSA, L, LXX, D, DSS, M, MACULA, N, GNT

# NEW: high-level verse helpers
from .api import getref, getver

# core lower-level helpers (keep available)
from .core import (
    verse_node,
    words_in_verse,
    first_existing_feature,
)

# book-name normalizer (SBL)
from .booknm import (
    to_sbl,
    citation,
)

# reference helpers (lower-level utilities)
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

# legacy version/metadata helpers (renamed to avoid clash with new getver)
from .getver import (
    getver as getver_meta,
    printver,
)

# Lazily expose nbstrip utilities (no hard nbformat dep at import time)
try:  # pragma: no cover
    from .nbstrip import strip_outputs, truncate_outputs  # requires nb extra
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
    "nb", "tfio", "core", "booknm", "refs", "api", "getver_mod",
    # quick import
    "quick_import",
    # dataset loading (minimal typing)
    "load_dataset", "ld", "B", "BHSA", "L", "LXX", "D", "DSS", "M", "MACULA", "N", "GNT",
    # high-level API
    "getref", "getver",
    # core utilities
    "verse_node", "words_in_verse", "first_existing_feature",
    # book names (SBL)
    "to_sbl", "citation",
    # refs utilities
    "ref_sbl", "ref_dataset", "cite", "cite_range",
    "verse_node_from_any", "verse_words", "sbl_to_dataset_book", "nodes_from_sbl_refs",
    # metadata (legacy)
    "getver_meta", "printver",
    # nbstrip (lazy)
    "strip_outputs", "truncate_outputs",
    # meta
    "__version__",
]