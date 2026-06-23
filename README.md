# PaperBullet

PaperBullet is a lightweight biomedical literature digest web app. It collects papers from preprint servers, PubMed, and selected official journal feeds, then organizes them into a readable daily or date-range brief.

The project is designed for small labs, reading groups, students, clinicians, and biomedical AI researchers who want a simple self-hosted paper radar.

## Features

- Biomedical field tabs:
  - Biomedical Overview
  - Drug Discovery
  - Medical Imaging
  - Clinical AI & Medical Language Models
  - Genomics & Multi-omics
  - Proteins & Biomolecules
- Multi-source collection:
  - arXiv
  - bioRxiv
  - medRxiv
  - PubMed
  - Nature / Science / Cell official feeds
- Paper metadata extraction:
  - authors
  - affiliations
  - funders
  - DOI
  - journal or server
  - original link and PDF link when available
- Chinese and English interface.
- Date-range reading, source filtering, pagination, archive page, and recommendation cards.
- No required third-party Python packages for the default rule-based mode.
- Optional OpenAI-powered summarization if you install `openai` and provide an API key.

## Quick Start

Requirements:

- Python 3.10 or newer
- Git

Clone the repository:

```bash
git clone https://github.com/tornado2047/PaperBullet.git
cd PaperBullet
```

Create your local environment file:

```bash
copy .env.example .env
```

On macOS or Linux:

```bash
cp .env.example .env
```

Start the app:

```bash
python run.py
```

Open:

```text
http://127.0.0.1:8000
```

The app can be used without an OpenAI API key. In that mode, it uses rule-based paper analysis and displays original abstracts when available.

## First Use Tutorial

1. Open the home page.
2. Choose a biomedical field tab, such as `Medical Imaging` or `Drug Discovery`.
3. Select a date range.
4. Click `Load range` to read papers already stored locally.
5. Click `Refresh range` to collect fresh papers from remote sources and rebuild the digest.
6. Use source chips, such as `PubMed`, `bioRxiv`, or `Science`, to narrow the current issue.
7. Switch `中文 / EN` in the top-right corner if you prefer another interface language.
8. Open `Archive` to revisit previously generated digests.

For a first test, choose a short date range such as the last 7 days. A long range may take noticeably longer because the app queries multiple remote services.

## Configuration

All runtime settings live in `.env`. Do not commit your real `.env` file.

| Variable | Default | Description |
| --- | --- | --- |
| `APP_HOST` | `127.0.0.1` | Server bind address. Use `0.0.0.0` for LAN access. |
| `APP_PORT` | `8000` | Server port. |
| `OPENAI_API_KEY` | empty | Optional OpenAI API key. |
| `OPENAI_MODEL` | `gpt-4o-mini` | Model used when OpenAI summarization is enabled. |
| `OPENAI_ENABLED` | `false` | Set to `true` to use OpenAI-powered summaries. |
| `CROSSREF_MAILTO` | `your-email@example.com` | Recommended by Crossref for polite API usage. |
| `DEFAULT_DOMAINS` | `biomed_all,drug_discovery,medical_imaging` | Domains used by the optional scheduler. |
| `SCHEDULER_ENABLED` | `false` | Set to `true` to run daily collection inside the app process. |
| `SCHEDULER_HOUR` | `8` | Scheduler hour. |
| `SCHEDULER_MINUTE` | `0` | Scheduler minute. |
| `COLLECT_MAX_RESULTS` | `24` | Per-source collection cap. |

## Optional OpenAI Summaries

Install the optional package:

```bash
python -m pip install openai
```

Update `.env`:

```env
OPENAI_ENABLED=true
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

Restart the app.

## LAN Deployment

To let other users in the same local network access PaperBullet:

1. Choose one machine as the server.
2. Set `.env`:

```env
APP_HOST=0.0.0.0
APP_PORT=8000
```

3. Start the app:

```bash
python run.py
```

4. Find the server IP.

On Windows:

```powershell
ipconfig
```

On macOS or Linux:

```bash
ifconfig
```

5. Other users open:

```text
http://SERVER_IP:8000
```

6. If the page cannot be reached, allow inbound traffic for port `8000` in the server firewall.

Recommended LAN usage:

- Let normal users read and filter papers.
- Let one maintainer click `Refresh range` or run scheduled refreshes.
- Use a fixed LAN IP for the server.

## Public Deployment Notes

PaperBullet currently uses SQLite and a simple Python HTTP server. This is practical for personal use, group demos, lab LANs, and small internal deployments.

For a public internet-facing service, consider adding:

- a production reverse proxy such as Caddy or Nginx
- HTTPS
- authentication for refresh endpoints
- a background worker for long refresh jobs
- PostgreSQL instead of SQLite
- rate limits for remote collection actions
- monitoring and backups

## API

| Endpoint | Description |
| --- | --- |
| `GET /api/domains` | List biomedical field presets. |
| `GET /api/digest?domain=biomed_all&date_from=2026-01-01&date_to=2026-01-07&page=1&page_size=10` | Read a digest for a date range. |
| `POST /api/digest/refresh` | Collect remote papers and rebuild a digest. |
| `GET /api/archive?domain=biomed_all&limit=12` | Read archive cards. |
| `GET /api/papers?domain=biomed_all&date=2026-01-01&limit=20` | Debug endpoint for stored papers. |

Example refresh request:

```bash
curl -X POST http://127.0.0.1:8000/api/digest/refresh \
  -H "Content-Type: application/json" \
  -d "{\"domain\":\"biomed_all\",\"date_from\":\"2026-01-01\",\"date_to\":\"2026-01-07\",\"limit\":18,\"page\":1,\"page_size\":10}"
```

## Data Sources

PaperBullet uses public metadata services and feeds:

- arXiv export API
- bioRxiv API
- medRxiv API
- NCBI PubMed E-utilities
- Crossref REST API
- selected official RSS feeds from Nature, Science, and Cell Press

Metadata availability varies by source. Affiliations, funders, abstracts, PDFs, and citation counts may be missing for some papers.

## Project Structure

```text
PaperBullet/
  app/
    main.py                 HTTP server and API routes
    config.py               domain presets and runtime settings
    db.py                   SQLite persistence
    services/
      arxiv_client.py
      biorxiv_client.py
      pubmed_client.py
      journal_client.py
      crossref_client.py
      paper_service.py
      summarizer.py
    static/
      index.html
      archive.html
      app.js
      archive.js
      styles.css
  run.py
  .env.example
  README.md
```

## Troubleshooting

### The page opens but has no papers

Click `Refresh range`. `Load range` only reads data already stored locally.

### Refresh is slow

Use a shorter date range first. PaperBullet queries several remote sources and enriches metadata.

### PubMed or Crossref returns incomplete metadata

This is normal. Some records do not include full affiliations, funders, abstracts, or DOI metadata.

### Other LAN users cannot open the page

Check that `APP_HOST=0.0.0.0`, the server firewall allows the port, and users are visiting `http://SERVER_IP:APP_PORT`.

### OpenAI summaries are not appearing

Make sure `openai` is installed, `OPENAI_ENABLED=true`, and `OPENAI_API_KEY` is set in `.env`.

## Contributing

Issues and pull requests are welcome. Useful contribution areas include:

- more biomedical data sources
- better paper ranking
- export to Markdown, CSV, or Excel
- user accounts and saved reading lists
- production deployment templates
- better multilingual summarization

## License

MIT License. See [LICENSE](LICENSE).
