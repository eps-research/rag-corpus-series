# EPS Research Astro-RAG MCP Server v2.2.0

**Author:** David C. Flynn, EPS Research, Laurel MD  
**ORCID:** 0000-0002-2768-6650  
**Zenodo:** https://doi.org/10.5281/zenodo.20985225  
**GitHub:** https://github.com/eps-research/astro-rag-mcp-server  
**License:** MIT  

---

## What This Is

The EPS Research Astro-RAG MCP Server provides structured query access to five astrophysical RAG corpora via two complementary interfaces:

| Interface | URL | Audience |
|-----------|-----|----------|
| **User Interface** | `http://localhost:8080` | Researchers — clean, human-readable |
| **REST API / Swagger** | `http://localhost:8080/docs` | Developers — raw endpoint explorer |

Both run from the same local server. The MCP server itself runs on HuggingFace Spaces and is queried automatically when you use either interface.

---

## The Five Corpora

| Key | Name | Objects | Description |
|-----|------|---------|-------------|
| `v7` | Unified HI Rotation Curve Corpus v7.0 | ~300 | Multi-survey HI rotation curves for spiral and irregular galaxies |
| `dwarf` | Dwarf & Irregular Galaxy HI Corpus v1.0 | ~129 | Low-mass galaxy HI kinematics extending the v7 regime |
| `gc` | Milky Way Globular Cluster Corpus v1.3.1 | 174 | Unified parameter set for MW globular clusters |
| `intz` | IntZ High-z Kinematic Corpus | ~800 | KROSS + KMOS3D galaxy kinematics at z≈0.6–2.5 |
| `z1` | High-z ALPINE Kinematic Corpus Z1 | 31 | ALPINE galaxy kinematics at z=4.26–5.68 |

Corpus keys are **case-sensitive** and must be **lowercase**.

---

## Quick Start

### Requirements

- Python 3.10 or later
- Windows 11 Pro or Ubuntu 20.04+
- Internet access (to reach the HuggingFace Space on first query)

### Installation

1. Download and extract the zip:
   ```
   astro-rag-mcp-server-v2.2.0.zip
   ```

2. The extracted folder contains:
   ```
   astro-rag-mcp-server-v2.2.0/
   ├── launch.py              ← run this
   ├── launcher_config.json   ← settings
   ├── server.py              ← MCP server source
   ├── README.md
   ├── CORPUS_KEYS.md
   └── rest-wrapper/          ← REST API + UI
   ```

3. Run the launcher:

   **Windows:**
   ```powershell
   python launch.py
   ```

   **Ubuntu / Linux:**
   ```bash
   python3 launch.py
   ```

4. The launcher will:
   - Check Python version and file manifest
   - Create a virtual environment (first run only, ~60 seconds)
   - Install all dependencies
   - Stop any prior instance on port 8080
   - Check HuggingFace Space reachability
   - Start the server in a new terminal window
   - Open your browser to `http://localhost:8080`
   - Show a status panel with both URLs and a Stop button

---

## Interface 1 — User Interface

**URL:** `http://localhost:8080`

The human-readable interface for daily research use.

### How to Use

1. Open `http://localhost:8080` in your browser
2. Select a **corpus** from the left sidebar (`v7`, `dwarf`, `gc`, `intz`, `z1`)
3. Select an **operation** from the sidebar
4. Fill in any parameters in the query bar
5. Click **Run**
6. Results appear as readable text by default
7. Toggle to **JSON** view to see raw data
8. Use **Download JSON** or **Download text** to save results

### Available Operations

| Operation | Description | Key Parameters |
|-----------|-------------|----------------|
| List corpora | Show all available corpora and descriptions | none |
| Corpus schema | Show field definitions for a corpus | corpus |
| List objects | Browse objects with optional filters | corpus, survey, tier, page, limit |
| Get object | Retrieve a single object by ID | corpus, object_id |
| Search metadata | Find objects matching a field value | corpus, field, value |
| Filter objects | Filter by numeric field range | corpus, field, min, max |

### Example Queries

**Get a single galaxy:**
- Corpus: `v7`, Operation: `Get object`, Object ID: `NGC3198`

**List globular clusters:**
- Corpus: `gc`, Operation: `List objects`, Limit: `25`

**Search by survey:**
- Corpus: `v7`, Operation: `Search metadata`, Field: `survey`, Value: `THINGS`

**Filter by distance:**
- Corpus: `dwarf`, Operation: `Filter objects`, Field: `distance_mpc`, Min: `1`, Max: `10`

---

## Interface 2 — REST API / Swagger

**URL:** `http://localhost:8080/docs`

The developer interface for direct API access, integration work, and testing.

### How to Use

1. Open `http://localhost:8080/docs` in your browser
2. You will see all available endpoints grouped by category
3. Click any endpoint to expand it
4. Click **Try it out**
5. Fill in the parameters
6. Click **Execute**
7. The response body, status code, and curl command appear below

### Endpoints

#### Corpora

```
GET /api/list_corpora
```
Returns all available corpora with descriptions.

```
GET /api/get_corpus_schema?corpus=v7
```
Returns the field schema for the specified corpus.

#### Objects

```
GET /api/list_objects?corpus=v7&page=1&limit=50
GET /api/list_objects?corpus=v7&survey=THINGS&limit=25
```
Lists objects in a corpus with optional survey/tier filters and pagination.

```
GET /api/get_object?corpus=v7&object_id=NGC3198
```
Returns full data for a single object.

#### Search & Filter

```
GET /api/search_metadata?corpus=v7&field=survey&value=THINGS
```
Finds all objects where the specified field matches the value.

```
GET /api/filter_objects?corpus=dwarf&field=distance_mpc&min=1&max=10
GET /api/filter_objects?corpus=v7&field=n_points&min=30&omega_ready_only=true
```
Filters objects by numeric field range. Optional `omega_ready_only=true` restricts to omega-eligible objects.

### Response Format

All endpoints return:

```json
{
  "success": true,
  "tool": "get_object",
  "data": { ... },
  "human_text": "Galaxy NGC3198 from Unified HI Rotation Curve Corpus v7.0. Survey: THINGS, distance 13.8 Mpc, 49 data points, omega-ready: True.",
  "error": null
}
```

The `human_text` field contains a ready-to-read plain English summary of the result.

### curl Examples

```bash
# List all corpora
curl -X GET "http://localhost:8080/api/list_corpora"

# Get a single galaxy
curl -X GET "http://localhost:8080/api/get_object?corpus=v7&object_id=NGC3198"

# Search by survey
curl -X GET "http://localhost:8080/api/search_metadata?corpus=v7&field=survey&value=THINGS"

# Filter by distance
curl -X GET "http://localhost:8080/api/filter_objects?corpus=dwarf&field=distance_mpc&min=1&max=10"
```

---

## MCP Server (HuggingFace Space)

The underlying MCP server runs at:

```
https://dflynn5656-astro-rag-mcp.hf.space/mcp
```

This server implements the Model Context Protocol (MCP) and is queried automatically by the REST wrapper. It is not intended for direct browser access.

**Direct MCP integration** (for AI assistants and Claude Desktop):

```json
{
  "mcpServers": {
    "astro-rag": {
      "type": "streamable-http",
      "url": "https://dflynn5656-astro-rag-mcp.hf.space/mcp"
    }
  }
}
```

The MCP server exposes six tools: `list_corpora`, `get_corpus_schema`, `list_objects`, `get_object`, `search_metadata`, `filter_objects`.

**Note:** The HuggingFace Space may sleep after inactivity. The first query after a sleep period will take 15–30 seconds to wake it. Subsequent queries are fast.

---

## Launcher Options

```
python launch.py [options]

Options:
  --port N          Port to run on (default: 8080)
  --host ADDR       Host address (default: 0.0.0.0)
  --skip-ping       Skip HuggingFace Space reachability check
  --no-browser      Do not auto-open browser on startup
  --no-gui          Terminal-only mode — no popup windows (use for SSH/headless)
  --skip-manifest   Bypass file manifest check (dev/test use only)
```

**Ubuntu headless / SSH / Node1:**
```bash
python3 launch.py --no-gui --no-browser
```

**Custom port:**
```bash
python3 launch.py --port 9000
```

---

## Configuration

Edit `launcher_config.json` to customize instance settings:

```json
{
    "hf_space_url" : "https://dflynn5656-astro-rag-mcp.hf.space/mcp",
    "corpus_keys"  : ["v7", "dwarf", "gc", "intz", "z1"],
    "default_port" : 8080,
    "default_host" : "0.0.0.0",
    "app_module"   : "app:app",
    "version"      : "2.2.0"
}
```

---

## Stopping the Server

- **GUI mode:** Click the **Stop Server** button in the status panel, or close the uvicorn terminal window
- **Terminal mode:** Press `Ctrl+C` in the launcher terminal
- **Re-launching:** The launcher automatically kills any prior instance on the same port

---

## Citing This Software

If you use this server in published research, please cite:

```bibtex
@software{flynn_astro_rag_mcp_2026,
  author    = {Flynn, David C.},
  title     = {{EPS Research Astro-RAG MCP Server v2.2.0}},
  year      = {2026},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.20985225},
  url       = {https://doi.org/10.5281/zenodo.20985225}
}
```

---

## Related Corpora

| Corpus | Zenodo DOI | arXiv |
|--------|-----------|-------|
| Unified HI Rotation Curve Corpus v7 | TBD | TBD |
| Dwarf/Irregular HI Corpus v1.0 | TBD | TBD |
| Globular Cluster Corpus v1.3.1 | TBD | TBD |
| IntZ Kinematic Corpus | TBD | TBD |
| High-z Z1 Kinematic Corpus | TBD | TBD |

---

*EPS Research — independent, self-funded astrophysics research, Laurel MD*  
*Contact: davidflynn@eps-research.com*
