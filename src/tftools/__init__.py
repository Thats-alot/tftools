# tftools/__init__.py
"""
tftools: helpers for Text-Fabric notebooks (BHSA / LXX / DSS / Macula / N1904)

Convenient top-level imports:
    import tftools as tt
    tt.quick_import(globals())
    tt.tfio.load_bhsa(ns=globals())
    ref = tt.ref_sbl(Tbhs, some_node)  # 'Gen 1:1'
"""

# Optional version string; harmless if package metadata isn't installed.
try:
    from importlib.metadata import version as _pkg_version
    __version__ = _pkg_version("tftools")
except Exception:  # pragma: no cover
    __version__ = "0+local"

# Expose submodules as namespaces (so you can do tt.tfio.load_bhsa, tt.refs.ref_sbl, etc.)
from . import nb as nb
from . import tfio as tfio
from . import core as core
from . import booknm as booknm
from . import refs as refs
from . import getver as getver_mod

# Top-level convenience re-exports (most-used symbols)
from .nb import quick_import

from .tfio import (
    load_dataset,
    load_bhsa,
    load_lxx_1935,
    load_dss,
    load_macula_lxx_linkp,
    load_n1904,
)

from .core import (
    getref,
    verse_node,
    words_in_verse,
    first_existing_feature,
)

from .booknm import (
    to_sbl,
    citation,
)

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

from .getver import (
    getver,
    printver,
)

# Lazily expose nbstrip utilities without making nbformat a hard import-time dependency
try:  # pragma: no cover
    from .nbstrip import strip_outputs, truncate_outputs  # needs nbformat installed
except Exception:  # pragma: no cover
    def strip_outputs(*_args, **_kwargs):
        raise RuntimeError(
            "tftools.nbstrip.strip_outputs requires 'nbformat'. "
            "Install it with: pip install nbformat"
        )
    def truncate_outputs(*_args, **_kwargs):
        raise RuntimeError(
            "tftools.nbstrip.truncate_outputs requires 'nbformat'. "
            "Install it with: pip install nbformat"
        )

__all__ = [
    # submodules
    "nb", "tfio", "core", "booknm", "refs", "getver_mod",
    # nb.py
    "quick_import",
    # tfio.py
    "load_dataset", "load_bhsa", "load_lxx_1935", "load_dss",
    "load_macula_lxx_linkp", "load_n1904",
    # core.py
    "getref", "verse_node", "words_in_verse", "first_existing_feature",
    # booknm.py
    "to_sbl", "citation",
    # refs.py
    "ref_sbl", "ref_dataset", "cite", "cite_range",
    "verse_node_from_any", "verse_words", "sbl_to_dataset_book", "nodes_from_sbl_refs",
    # getver.py
    "getver", "printver",
    # nbstrip.py (lazy)
    "strip_outputs", "truncate_outputs",
    # meta
    "__version__",
]