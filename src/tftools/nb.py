# tftools/nb.py
from __future__ import annotations
from typing import Dict, Any, Optional
import importlib

def quick_import(
    ns: Optional[dict] = None,
    *,
    seaborn: bool = True,
    excel: bool = True,
    strict: bool = True,
) -> Dict[str, Any]:
    """
    Import common libs for TF notebooks.

    Call with no args for the full set:
        quick_import()  # seaborn + openpyxl included

    If a package is missing and strict=True (default), a friendly error is raised
    with an exact pip command ('pip install -e ".[full]"' or minimal package list).
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
    missing = set()

    for alias, spec in wanted.items():
        try:
            if ":" in spec:
                modname, attr = spec.split(":", 1)
                module = importlib.import_module(modname)
                obj = getattr(module, attr)
            else:
                obj = importlib.import_module(spec)
            out[alias] = obj
        except ModuleNotFoundError:
            # record the base module name that failed
            base = spec.split(":", 1)[0]
            missing.add(base)

    # sensible matplotlib default if present
    if "plt" in out:
        out["plt"].rcdefaults()

    if missing and strict:
        # Suggest a single command that fixes everything
        pkgs = " ".join(sorted(missing))
        raise RuntimeError(
            f"Missing packages: {', '.join(sorted(missing))}.\n"
            f"Install with:\n"
            f"  pip install -e '.[full]'\n"
            f"or minimally:\n"
            f"  pip install {pkgs}\n"
        )

    if ns is not None:
        ns.update(out)
    return out