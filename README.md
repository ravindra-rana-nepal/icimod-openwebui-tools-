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

https://raw.githubusercontent.com/<your-user>/icimod-openwebui-tools/main/icimod_rds_explorer.py

3. Paste into the editor, give it a **Name** and **Description**, then **Save**.
4. Repeat for `icimod_library_search.py`.

### Option B — Manual paste

1. Open the `.py` file on GitHub, click **Raw**, and copy everything.
2. In Open WebUI, go to **Workspace → Tools → + Create New Tool**.
3. Paste the code, save, and enable the tool for your model.

### Enabling the tools

After saving, attach them to a model:
- **Workspace → Models → [your model] → Edit → Tools** → toggle both tools on.

> ⚠️ Tool calling works best with capable models (GPT-4o, Claude 3.5 Sonnet,
> Llama 3.1 70B+, Qwen 2.5 32B+). Small models may not call tools reliably.

## ⚙️ Configuration

**ICIMOD Library Search** exposes a `Valves` panel. After saving the tool, click
the ⚙️ gear icon to change:

| Valve | Default | Description |
|---|---|---|
| `API_URL` | `https://lib.icimod.org/api/records` | Records API endpoint |
| `MAX_RESULTS` | `10` | Results per search (1–50) |
| `SORT` | `bestmatch` | `bestmatch`, `newest`, `oldest`, `mostrecent` |

**ICIMOD RDS Dataset Explorer** uses the constant `BASE_URL` at the top of the
file — edit it in the tool editor if the endpoint changes.

## 💬 Usage Examples

Once enabled, just ask your model naturally:

- *"List 10 recent datasets from ICIMOD RDS about glaciers."*
- *"Search ICIMOD library for 'SERVIR flood mapping'."*
- *"Show me datasets tagged with the theme 'water'."*
- *"What are the newest ICIMOD publications on cryosphere?"*

## 🔗 API References

- ICIMOD RDS GeoAPI: `https://rds.icimod.org/geoapi/public`
- ICIMOD Library Records API: `https://lib.icimod.org/api/records`

## 🤝 Contributing

Issues and pull requests are welcome. If you add a new tool:

1. Place it at the repo root as `icimod_<name>.py` (or under `tools/`).
2. Include the required Open WebUI docstring header (`title`, `author`, `version`, `description`, `requirements`).
3. Update the table in this README.
4. Add a short usage example.

## 📄 License

MIT — see [LICENSE](LICENSE).

## 👤 Author

- **Ravindra Rana** ([@ravindra-rana-nepal](https://github.com/ravindra-rana-nepal))

## 🙏 Acknowledgements

- [ICIMOD](https://www.icimod.org/) for the public RDS and Library APIs
- [Open WebUI](https://github.com/open-webui/open-webui) for the tools framework