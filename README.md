# tftools

Text-Fabric research helper tools.

Currently works with ETCBC's BHSA, CenterBLC's LXX, Dead Sea Scrolls, and Clear-Bible's Macula Hebrew Dataset.

2 useful functions:

getref(), used to get retrive the reference and verse from the word node number.

getver(), used to retrive the verse from the verse's reference.

---

## Documentation
- [Manual — tftools](docs/Manual-tftools.md)

---

## Install

> This repo uses optional “extras” so you can install only what you need, or everything at once.

```bash
# clone + enter
git clone https://github.com/Thats-alot/tftools.git
cd tftools

# create & activate a venv (recommended)
python -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\Activate.ps1

# install everything (Text-Fabric + viz + nbstrip)
pip install -e '.[full]'
