# ICIMOD Open WebUI Tools

A collection of [Open WebUI](https://github.com/open-webui/open-webui) tools for
searching and exploring [ICIMOD](https://www.icimod.org/) resources — the Regional
Database System (RDS) and the ICIMOD Knowledge Library.

## 🧰 Included Tools

| Tool | File | Description |
|---|---|---|
| **ICIMOD RDS Dataset Explorer** | `icimod_rds_explorer.py` | Browse, search, and inspect datasets in the ICIMOD Regional Database System via the public GeoAPI. |
| **ICIMOD Library Search** | `icimod_library_search.py` | Search ICIMOD publications, reports, and records through the public records API. |

## ✨ Features

### ICIMOD RDS Dataset Explorer
- 📄 List datasets with pagination
- 🔎 Keyword search across titles and abstracts
- 🏷️ Filter datasets by theme
- 🕒 Get most recently published datasets
- 📊 Summary statistics (country and data-type mentions)
- 🔗 Direct links to metadata pages and thumbnails

### ICIMOD Library Search
- 🔍 Full-text search of the ICIMOD knowledge library
- ⚙️ Configurable via **Valves** (API endpoint, result count, sort order)
- 📚 Returns titles, authors, dates, summaries, and links
- ⚡ Async with live status updates in the chat UI

## 📋 Requirements

- Open WebUI (recent version with Tools support)
- Python packages: `requests`, `pydantic` (already bundled with Open WebUI)
- Internet access to `rds.icimod.org` and `lib.icimod.org`

No API keys are required — both services are public.

## 🚀 Installation

### Option A — Import from GitHub (recommended)

1. Open Open WebUI → **Workspace** → **Tools** → **+ Create New Tool**
2. Copy the raw contents of the tool file, e.g.: