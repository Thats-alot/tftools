# tftools/getver.py
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any

@dataclass(frozen=True)
class TFVersionInfo:
    text_fabric: Optional[str]
    dataset: Optional[str]
    repo_url: Optional[str]
    released: Optional[str]
    app_name: Optional[str]

def getver(A=None) -> TFVersionInfo:
    import tf as textfabric
    tf_ver = getattr(textfabric, "__version__", None)
    dataset = repo = released = app = None
    if A is not None:
        TF = getattr(A.api, "TF", None)
        meta: Dict[str, Any] = {}
        if TF is not None:
            meta = getattr(TF, "_meta", None) or getattr(TF, "metaData", lambda: {})()
        dataset  = meta.get("dataset")
        repo     = meta.get("repo")
        released = meta.get("released")
        app      = getattr(A, "appName", None)
    return TFVersionInfo(tf_ver, dataset, repo, released, app)

def printver(A=None) -> None:
    info = asdict(getver(A))
    for k, v in info.items():
        print(f"{k:>12}: {v}")