# Manual — tftools

Helpers for **Text‑Fabric** notebooks across BHSA (BHS), CenterBLC LXX (1935), DSS, Macula LXX‑Link‑P, and N1904 (GNT).  
This manual covers install options, quick start, and the public API.

---

## Contents
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Dataset Loaders & Aliases](#dataset-loaders--aliases)
- [Book Names (SBL Normalizer)](#book-names-sbl-normalizer)
- [Core Helpers](#core-helpers)
- [Reference Helpers](#reference-helpers)
- [Notebook Utilities](#notebook-utilities)
- [Notebook Output Stripper (optional)](#notebook-output-stripper-optional)
- [Version / Metadata](#version--metadata)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Installation

`tftools` uses **optional extras** so you can install only what you need, or everything at once.

```bash
# Clone and enter the repo
git clone https://github.com/<your-username>/tftools.git
cd tftools

# Create & activate a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate    # Windows: .\.venv\Scripts\Activate.ps1

# Install EVERYTHING (Text‑Fabric + pandas/numpy/matplotlib/seaborn + nbformat)
pip install -e '.[full]'
```

Other choices:

```bash
pip install -e '.[tf]'        # only Text‑Fabric
pip install -e '.[full,dev]'  # everything + dev tools (ruff, pytest, pre-commit)
```

> If you plan to use the `tft-nbstrip` CLI, make sure you installed the `nb` extra (included in `full`).

---

## Quick Start

In a Jupyter notebook or VS Code:

## Quick Start

In a Jupyter notebook or VS Code:

```python
%load_ext autoreload
%autoreload 2

import tftools as tt

# Pull your usual libs (pd/np/plt/…)
tt.quick_import(globals())

# Load ALL datasets & hoist your usual names (Fbhs/Lbhs/Tbhs/…, Flxx/…, etc.)
tt.load_dataset()          # or: tt.ld()

# Examples for subsets (optional):
# tt.load_dataset(tt.B)          # BHSA only
# tt.load_dataset(tt.L, tt.N)    # LXX (1935) + GNT (N1904)
# tt.ld(tt.M, "D")               # Macula LXX-Link-P + DSS

# Example: first BHSA verse
v = next(iter(Tbhs.otype.s("verse")))
print(tt.ref_sbl(Tbhs, v))       # -> 'Gen 1:1' (SBL)
print(tt.ref_dataset(Tbhs, v))   # -> 'Genesis 1:1' (dataset label)

# Words of the verse (auto feature fallback: BHSA g_cons_utf8, LXX g_word_utf8, else text)
tt.verse_words(Fbhs, Lbhs, Tbhs, v, feature="default")
```

---

## Dataset Loaders & Aliases

Convenience wrappers around `tf.app.use(...)` that **hoist** your preferred variable names into the calling namespace (usually `globals()`):

| Function | Loads | Hoists (names you get) |
|---|---|---|
| `tt.tfio.load_bhsa(ns=globals(), version='2021', mod='CenterBLC/BHSaddons/tf')` | ETCBC BHSA | `Fbhs, Lbhs, Tbhs, Sbhs` |
| `tt.tfio.load_lxx_1935(ns=globals(), version='1935')` | CenterBLC LXX (1935) | `Flxx, Llxx, Tlxx, Slxx` |
| `tt.tfio.load_dss(ns=globals(), version='1.9')` | ETCBC DSS | `Fdss, Ldss, Tdss, Sdss` |
| `tt.tfio.load_macula_lxx_linkp(ns=globals(), version='0.0.8')` | Macula LXX‑Link‑P | `Fhb, Lhb, Thb` |
| `tt.tfio.load_n1904(ns=globals(), version='1.0.0', mod='CenterBLC/N1904/BOLcomplement/tf/')` | CenterBLC N1904 (+BOL) | `Fgnt, Lgnt, Tgnt, Sgnt` |

Generic loader (if you need a custom dataset):
```python
A, F, L, T, S = tt.load_dataset('org/repo', version='X', mod=None, ns=globals(),
                                aliases=('Fxxx','Lxxx','Txxx','Sxxx'))
```

---

## Book Names (SBL Normalizer)

`tftools.booknm` converts messy dataset labels (e.g., `Jesaia`, `Reges II`, `Samuel_I`, `Song of Solomon`) into **SBL abbreviations** (`Isa`, `2 Kgs`, `1 Sam`, `Song`).

```python
from tftools.booknm import to_sbl, citation

to_sbl('Genesis')          # 'Gen'
to_sbl('Jesaia')           # 'Isa'
to_sbl('Reges II')         # '2 Kgs'
to_sbl('Song of Solomon')  # 'Song'

citation('Genesis', 1, 1)  # 'Gen 1:1'
```

> Internally, this includes your BHS→SBL table plus robust aliasing (English names, roman↔arabic numerals, alt spellings).

---

## Core Helpers

Module: `tftools.core`

```python
tt.getref(Tbhs, v, style='dataset')   # 'Genesis 1:1' (dataset label)
tt.getref(Tbhs, v, style='sbl')       # 'Gen 1:1'     (SBL)

tt.verse_node(Tbhs, some_word_node)   # -> verse node or None

# Words of the verse containing `node`
tt.words_in_verse(Fbhs, Lbhs, Tbhs, node=v, features='default')
# Multiple features → list of tuples:
tt.words_in_verse(Fbhs, Lbhs, Tbhs, v, features=('g_cons_utf8','lex'))
```

- `first_existing_feature(F, *names)`: returns first feature name present on `F`.

---

## Reference Helpers

Module: `tftools.refs`

```python
tt.ref_dataset(Tbhs, v)              # 'Genesis 1:1'
tt.ref_sbl(Tbhs, v)                  # 'Gen 1:1'

tt.cite('Reges II', 2, 1)           # '2 Kgs 2:1'
tt.cite_range('Ezekiel', 1, 1, 3)   # 'Ezek 1:1–3'

# Words with automatic feature fallback (BHSA/LXX/GNT-safe)
tt.verse_words(Fbhs, Lbhs, Tbhs, v, feature='default')

# Map SBL abbrev -> dataset's canonical book label
tt.sbl_to_dataset_book(Fbhs, Tbhs, 'Ezek')   # e.g., 'Ezechiel' (BHSA)

# Parse SBL refs to verse nodes for this dataset
nodes = tt.nodes_from_sbl_refs(Fbhs, Tbhs, 'Ezek 1:1-3; 2:1')
[tt.ref_sbl(Tbhs, n) for n in nodes]         # ['Ezek 1:1','Ezek 1:2','Ezek 1:3','Ezek 2:1']
```

---

## Notebook Utilities

Module: `tftools.nb`

```python
# Pull common libraries into your notebook (optionally into globals())
env = tt.quick_import(globals(), seaborn=True, excel=False)
```

Args:
- `seaborn=True` to include `sns`
- `excel=True` to include `openpyxl` helpers (`load_workbook`, `Font`, `Alignment`, `PatternFill`)

---

## Notebook Output Stripper (optional)

Module/CLI: `tftools.nbstrip` (requires `nbformat`, included in `.[nb]` and `.[full]`).

From the CLI:
```bash
tft-nbstrip path/to/notebook.ipynb --strip
tft-nbstrip path/to/notebook.ipynb --truncate 4000
```

From Python:
```python
from tftools.nbstrip import strip_outputs, truncate_outputs
strip_outputs('my.ipynb')
truncate_outputs('my.ipynb', max_len=4000)
```

---

## Version / Metadata

Module: `tftools.getver`

```python
tt.printver(bags['B']['A'])   # pretty print TF + dataset info
info = tt.getver(bags['B']['A'])
```

Returns: `TFVersionInfo(text_fabric, dataset, repo_url, released, app_name)`

---

## Troubleshooting

**GitHub API rate limit while `use(...)` fetches corpora**  
Set a personal access token (PAT) in your shell and try again:
```bash
export GHPERS=<your-github-token>
```
Add that line to your `~/.zshrc` / `~/.bashrc`.  
Keep Text‑Fabric data outside this repo (default is `~/text-fabric-data`).

**`nbformat` not installed** (when using `nbstrip`)  
Install the extra:
```bash
pip install -e '.[nb]'
```

**Missing word feature**  
If `g_cons_utf8` / `g_word_utf8` aren’t present in a dataset, `feature='default'` falls back to `text`.

---

## Contributing

- Edit code in `src/tftools/…` (installed in **editable** mode).
- In notebooks, `%autoreload 2` picks up saved changes on next cell run.
- Share changes with Git: `git add -A && git commit -m "message" && git push`.

Dev tools:
```bash
pip install -e '.[dev]'
ruff check .
pytest
```

---

## License

MIT (see `LICENSE`).
