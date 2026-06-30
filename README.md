# 🔭 EPS Astro Extractor

**Version:** 1.0.0  
**Author:** David C. Flynn, EPS Research (Laurel, MD)  
**ORCID:** 0000-0002-2768-6650  
**License:** MIT  
**Zenodo DOI:** *(assigned at deposit)*

---

## What It Is

EPS Astro Extractor is a portable Streamlit application that extracts structured data from astronomical databases and survey catalogues using a local large language model (LLM) via LM Studio. No API key, no internet-connected AI service, no cost per query. All inference runs on your own hardware.

You point it at any publicly accessible URL, name the entity you are looking for, and the tool crawls the page, feeds the content to your local LLM, and returns a structured JSON result with parameters, table data, and notes — ready to export as CSV or JSON.

---

## Requirements

- Python 3.10+
- [LM Studio](https://lmstudio.ai/) running locally with at least one model loaded
- A machine with enough VRAM to run your chosen model (see Model Recommendations below)
- Internet access for crawling target URLs (the LLM inference is fully local)

---

## Quick Start

### Option 1 — One-click launcher (Linux/macOS)
```bash
git clone <repo_url>
cd astro_extractor
bash run.sh
```
`run.sh` creates a virtual environment, installs dependencies, and launches the app at `http://localhost:8501`.

### Option 2 — Manual
```bash
cd astro_extractor
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py --server.port 8502
```

### LM Studio setup
1. Download and install [LM Studio](https://lmstudio.ai/)
2. Load a model (see recommendations below)
3. Start the local server (default: `http://127.0.0.1:1234`)
4. Enter the server URL in the app sidebar

---

## Interface

The sidebar contains:
- **LM Studio connection** — server URL and model selector
- **🎯 Quick Targets** — one-click access to tested astronomical databases
- **📡 Survey Catalogues** — one-click access to tested HI survey CDS entries

The main panel contains:
- **Database URL** — any publicly accessible URL
- **Target Entity** — what you are looking for (e.g. `NGC3198`, `SPARC`, `THINGS`)
- **Schema Hints** — optional comma-separated field names to guide extraction
- **Crawl depth** — 0 (single page), 1 (follow one level of links), 2 (two levels)
- **Extract Data** button
- **Results panel** — Parameters table, Table Data tab, Raw JSON tab, Export buttons

---

## Quick Targets (Tested and Working)

### 🎯 Astronomical Databases
| Target | URL Pattern | Best Entity Example | Notes |
|--------|-------------|---------------------|-------|
| **SPARC** | `astroweb.cwru.edu/SPARC/` | `database` | Landing page; use direct file URLs for data |
| **VizieR** | `cdsarc.cds.unistra.fr/viz-bin/cat/J/...` | `catalogue` | CDS readme pages work best |
| **NED** | `ned.ipac.caltech.edu/cgi-bin/objsearch?objname=...` | Object name (e.g. `NGC3198`) | Use `cgi-bin/objsearch` not the homepage |
| **HyperLeda** | `leda.univ-lyon1.fr/ledacat.cgi?o=...` | Object name (e.g. `NGC3198`) | Direct object pages return 40+ parameters |

### 📡 Survey Catalogues (via CDS)
| Target | CDS Identifier | Entity | Galaxies |
|--------|---------------|--------|----------|
| **THINGS** | `J/AJ/136/2563` | `THINGS` | 34 nearby spirals, VLA HI |
| **LITTLE THINGS** | `J/AJ/144/134` | `LITTLE THINGS` | 37 dwarf irregulars + 4 BCDs, VLA HI |
| **WHISP** | `J/A+A/390/863` | `WHISP` | 171 spirals/irregulars, WSRT HI+photometry |
| **LVHIS** | `J/MNRAS/478/1611` | `LVHIS` | 82 local volume galaxies, ATCA HI |

---

## Model Recommendations

**Best for extraction tasks:**
- `mistral-7b-instruct-v0.2` — fast, reliable JSON output, no thinking blocks
- `astrosage-8b` — domain-specific astronomy knowledge
- Any instruct-tuned model without chain-of-thought reasoning

**Avoid for extraction:**
- Thinking/reasoning models (gemma-4-31b-v2, deepseek-r1-distill-*) — these generate lengthy internal reasoning that consumes token budget before producing JSON, causing timeouts on complex pages
- Very large models (70B+) unless you have sufficient VRAM and need the accuracy

**If you must use a thinking model:**
- Set max_tokens high (8000+)
- Use simple pages with minimal repeated content
- The salvage_json fallback will attempt to recover truncated output

---

## Known Limitations

| Service | Issue | Workaround |
|---------|-------|------------|
| SIMBAD object pages | Thinking models time out on complex object pages | Use bibcode query URLs (`sim-ref?bibcode=...`) instead; these return cleaner, smaller pages |
| EDD (Extragalactic Distance Database) | Form-based interface, not crawlable via GET | Not supported in v1.0 |
| JavaScript-heavy pages | crawl4ai may return minimal content | Use depth 0 and check Raw Markdown to verify content was retrieved |
| Private/login-required pages | Not accessible | Tool only works with publicly accessible URLs |

---

## Output Format

All extractions return a JSON object:
```json
{
  "entity": "NGC3198",
  "parameters": [
    {"parameter": "RA (ICRS)", "value": "10 19 54.990", "unit": "h m s", "note": "Infrared origin"}
  ],
  "table_data": [
    {"col": "value"}
  ],
  "notes": "Description of the source and extraction.",
  "found": true
}
```

Export options: Parameters CSV, Table CSV (when table data present), Full JSON.

---

## Session Accumulator

All extractions in a session are saved to the session accumulator (bottom of page when 2+ extractions exist). The accumulator exports all results as a combined CSV or JSON for batch workflows.

---

## Citation

If you use EPS Astro Extractor in your research, please cite:

```
Flynn, D.C. (2026). EPS Astro Extractor v1.0.0 [Software].
Zenodo. https://doi.org/10.5281/zenodo.XXXXXXX
```

---

## Related Work

This tool was developed in support of the EPS Research RAG Corpus Series:

- Flynn & Cannaliato (2025). *Frontiers in Astronomy and Space Sciences.* DOI: 10.3389/fspas.2025.1680387
- Flynn (2026). *Physics of the Dark Universe.* (accepted)
- RAG Corpus Series platform: https://github.com/eps-research/rag-corpus-series
- Platform Zenodo DOI: 10.5281/zenodo.20398430

---

## License

MIT License. See LICENSE file for details.
