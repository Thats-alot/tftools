# tftools/nb.py
from __future__ import annotations
from typing import Dict, Any, Optional
import importlib

def quick_import(
    ns: Optional[dict] = None,
    *,
    seaborn: bool = True,
    excel: bool = False,
) -> Dict[str, Any]:
    """
    Import common libs used in TF notebooks.
    If ns=globals() is provided, injects the names there. Returns a dict in any case.

    Args:
      seaborn: include seaborn as 'sns'
      excel:   include openpyxl helpers (load_workbook, Font, Alignment, PatternFill)
    """
    wanted = {
        "sys": "sys",
        "os": "os",
        "collections": "collections",
        "pd": "pandas",
        "np": "numpy",
        "re": "re",
        "csv": "csv",
        "difflib": "difflib",
        "json": "json",
        "unicodedata": "unicodedata",
        "Path": "pathlib:Path",
        "Counter": "collections:Counter",
        "defaultdict": "collections:defaultdict",
        "tqdm": "tqdm",
        "HTML": "IPython.display:HTML",
        "display": "IPython.display:display",
        "plt": "matplotlib.pyplot",
        "figure": "matplotlib.pyplot:figure",
        "SequenceMatcher": "difflib:SequenceMatcher",
    }
    if seaborn:
        wanted["sns"] = "seaborn"
    if excel:
        wanted["load_workbook"] = "openpyxl:load_workbook"
        wanted["Font"] = "openpyxl.styles:Font"
        wanted["Alignment"] = "openpyxl.styles:Alignment"
        wanted["PatternFill"] = "openpyxl.styles:PatternFill"

    out: Dict[str, Any] = {}
    for alias, spec in wanted.items():
        if ":" in spec:
            modname, attr = spec.split(":", 1)
            module = importlib.import_module(modname)
            obj = getattr(module, attr)
        else:
            obj = importlib.import_module(spec)
        out[alias] = obj

    # sensible matplotlib default
    out["plt"].rcdefaults()

    if ns is not None:
        ns.update(out)
    return out