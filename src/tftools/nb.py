# tftools/nb.py
from __future__ import annotations
from typing import Dict, Any, Optional
import importlib

def _user_ns_or_none():
    try:
        from IPython import get_ipython
        ip = get_ipython()
        if ip is not None and hasattr(ip, "user_ns"):
            return ip.user_ns
    except Exception:
        pass
    return None

def quick_import(
    ns: Optional[dict] = None,
    *,
    seaborn: bool = True,
    excel: bool = True,
    strict: bool = True,
) -> Dict[str, Any]:
    """
    Import common libs. In Jupyter, auto-injects into the notebook's namespace by default.
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
            missing.add(spec.split(":", 1)[0])

    if "plt" in out:
        out["plt"].rcdefaults()

    if missing and strict:
        pkgs = " ".join(sorted(missing))
        raise RuntimeError(
            "Missing packages: " + ", ".join(sorted(missing)) + "\n"
            "Install with:\n"
            "  pip install -e '.[full]'\n"
            "or minimally:\n"
            f"  pip install {pkgs}\n"
        )

    # 🔑 Auto-inject into Jupyter notebook globals by default
    target_ns = ns if ns is not None else _user_ns_or_none()
    if target_ns is not None:
        target_ns.update(out)
    return out