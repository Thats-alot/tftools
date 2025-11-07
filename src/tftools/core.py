# tftools/core.py
from __future__ import annotations
from typing import Iterable, List, Optional, Sequence, Tuple, Union, Any

Node = int

def first_existing_feature(F: Any, *names: str) -> Optional[str]:
    """Return the first feature name present on F from the given candidates, else None."""
    for n in names:
        if hasattr(F, n):
            return n
    return None

def verse_node(T: Any, node: Node) -> Optional[Node]:
    """Return the verse node that contains `node` (word/phrase/clause/…)."""
    b, c, v = T.sectionFromNode(int(node))
    if b is None or c is None or v is None:
        return None
    return T.nodeFromSection((b, c, v))

def _ensure_verse_node(T: Any, node_or_verse: Node) -> Optional[Node]:
    """If given a non-verse node, convert to its verse node; if already verse, keep it."""
    # This is robust even if caller passes a verse node: we go to (book,chap,verse) and back
    b, c, v = T.sectionFromNode(int(node_or_verse))
    if b is None or c is None or v is None:
        return None
    return T.nodeFromSection((b, c, v))

def words_in_verse(
    F: Any,
    L: Any,
    T: Any,
    node_or_verse: Node,
    features: Union[str, Sequence[str]] = "default",
) -> List[Union[str, Tuple[Optional[str], ...]]]:
    """
    Return tokens for the verse that contains `node_or_verse`.

    features:
      - "default": pick a sensible token feature automatically:
          try BHSA: g_cons_utf8 -> g_cons
              else: g_word_utf8 -> text
      - "<feat>":  single feature name (e.g., "g_word_utf8", "text")
      - ("feat1","feat2",...): returns list of tuples per word
    """
    vnode = _ensure_verse_node(T, int(node_or_verse))
    if vnode is None:
        return []

    # Decide which features to pull
    if features == "default":
        feat = (
            first_existing_feature(F, "g_cons_utf8", "g_cons")
            or first_existing_feature(F, "g_word_utf8", "text")
            or "text"
        )
        feat_names: List[str] = [feat]
    elif isinstance(features, (list, tuple)):
        feat_names = [str(x) for x in features]
    else:
        feat_names = [str(features)]

    wnodes = L.d(vnode, otype="word")

    # Single feature → list of strings
    if len(feat_names) == 1:
        name = feat_names[0]
        fobj = getattr(F, name, None)
        if fobj is None:
            return [None for _ in wnodes]  # preserve length
        return [fobj.v(w) for w in wnodes]

    # Multiple features → list of tuples
    fobjs = [getattr(F, n, None) for n in feat_names]
    out: List[Tuple[Optional[str], ...]] = []
    for w in wnodes:
        out.append(tuple(f.v(w) if f is not None else None for f in fobjs))
    return out

__all__ = [
    "first_existing_feature",
    "verse_node",
    "words_in_verse",
]