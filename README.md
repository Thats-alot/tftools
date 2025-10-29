# tftools

Helpers for **Text-Fabric** notebooks across BHSA (BHS), CenterBLC LXX (1935), DSS, Macula LXX-Link-P, and N1904 (GNT).  
Features include:

- One-liners to load your standard corpora with your **preferred variable names** (`Fbhs`, `Lbhs`, `Tbhs`, …)
- Robust **book-name normalizer** → SBL abbreviations (e.g., `Reges II` → `2 Kgs`)
- Easy **SBL citations** from TF nodes (`"Gen 1:1"`), verse word dumps with sensible feature fallbacks
- A tiny **notebook importer** to pull your usual libs into `globals()`
- Optional notebook **output stripper/truncater**

---

## Documentation
- [Manual — tftools](docs/Manual-tftools.md)

---

## Install

> This repo uses optional “extras” so you can install only what you need, or everything at once.

```bash
# clone + enter
git clone https://github.com/<your-username>/tftools.git
cd tftools

# create & activate a venv (recommended)
python -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\Activate.ps1

# install everything (Text-Fabric + viz + nbstrip)
pip install -e '.[full]'