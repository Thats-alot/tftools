# tftools/nbstrip.py
from __future__ import annotations
import nbformat
import argparse
from typing import Optional

def strip_outputs(path: str) -> bool:
    """
    Remove all cell outputs and execution counts. Returns True if changes were written.
    """
    nb = nbformat.read(path, as_version=nbformat.NO_CONVERT)
    changed = False
    for cell in nb.cells:
        if cell.get("outputs"):
            cell["outputs"] = []
            changed = True
        if cell.get("execution_count") is not None:
            cell["execution_count"] = None
            changed = True
    if changed:
        nbformat.write(nb, path)
    return changed

def truncate_outputs(path: str, max_len: int = 2000) -> bool:
    """
    Truncate long text outputs to 'max_len' characters per output.
    Leaves non-text outputs as-is. Returns True if changes were written.
    """
    nb = nbformat.read(path, as_version=nbformat.NO_CONVERT)
    changed = False
    for cell in nb.cells:
        if not cell.get("outputs"):
            continue
        for out in cell["outputs"]:
            txt = out.get("text")
            if isinstance(txt, str) and len(txt) > max_len:
                out["text"] = txt[:max_len] + "\n… [truncated]\n"
                changed = True
        if cell.get("execution_count") is not None:
            cell["execution_count"] = None
            changed = True
    if changed:
        nbformat.write(nb, path)
    return changed

def main(argv=None):
    ap = argparse.ArgumentParser(description="Strip or truncate Jupyter notebook outputs.")
    ap.add_argument("notebook", help="Path to .ipynb")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--strip", action="store_true", help="Remove all outputs")
    mode.add_argument("--truncate", type=int, metavar="N", help="Truncate text outputs to N chars")
    args = ap.parse_args(argv)

    if args.strip:
        ok = strip_outputs(args.notebook)
        print("No changes needed." if not ok else "Outputs stripped.")
    else:
        ok = truncate_outputs(args.notebook, max_len=args.truncate)
        print("No changes needed." if not ok else f"Outputs truncated to {args.truncate} chars.")

if __name__ == "__main__":
    main()