# CLAUDE.md — Tyler Medical Records Dashboard

Static dashboard that visualizes medical-records data, **plus a read-only MCP server at `/mcp`**. Pure **static HTML/CSS + one dependency-free Worker module** — no package.json, no build step. Deployed to Cloudflare Workers with static assets. Repo `git@github.com:tylerbishopdev/tyler-medical.git`, branch `main`.

**Live:** https://helptyler.live (public, no auth). URLs are served **extensionless** (`/reports/<id>`, not `.html`).
The `square-smoke-9144.bishopbjj.workers.dev` URL is gated behind Cloudflare Access — do not use it to verify deploys; test `helptyler.live`.

## Commands
```bash
npx wrangler dev --port 8791 --local   # Worker + assets locally (tests /mcp)
python3 -m http.server 8000 --directory public   # static-only preview
npx wrangler deploy                    # deploy Worker + ./public (project square-smoke-9144)
```

## MCP server
`src/index.js` implements JSON-RPC 2.0 over HTTP POST (MCP Streamable HTTP) at `/mcp`, stateless and read-only. No SDK, deliberately — the repo has no build step. Negotiates protocol `2025-11-25` / `2025-06-18` / `2025-03-26`. Tools: `list_records`, `get_record` (`full:true` fetches the page through the ASSETS binding and strips HTML), `search_records`, `get_summary` (returns `public/llms.txt`).

`src/records.js` is the record index. **Every `id` must match a real `public/reports/<id>.html` stem** — a mismatch hands clinicians a dead link. Verify after adding records.

Static assets are matched *before* the Worker runs, so `_headers`, `_redirects` and extensionless-HTML handling are unchanged; the Worker only sees `/mcp` and 404 fallthrough.

## Data flow
`extracted_records.txt` (raw text pulled from the records PDF) → `parse_medical_records.py` → `normalized_medical_data.json` → loaded by `dashboard.html`. The parser **requires `extracted_records.txt`** to exist. Change field extraction in the parser, then re-run it; don't hand-edit the JSON.

## Key files
- `public/index.html` — **the deployed dashboard** (what helptyler.live serves at `/`). Hand-authored; it does *not* read `normalized_medical_data.json`. Chart.js data is inlined.
- `public/reports/*.html` — one page per record. Newer pages link `reports/report.css`; older ones still inline their CSS.
- `public/llms.txt` — clinical overview for AI agents; also returned by the MCP `get_summary` tool.
- `src/index.js`, `src/records.js` — the MCP server and its record index.
- `wrangler.jsonc` — `name: square-smoke-9144`, `main: src/index.js`, `assets: { directory: ./public, binding: ASSETS }`.
- `dashboard.html`, `Medical Records Dashboard.html`, `parse_medical_records.py`, `normalized_medical_data.json` — **legacy, not deployed.** The parser pipeline (`extracted_records.txt` → JSON → `dashboard.html`) is not what the live site uses. Don't edit these expecting the site to change.

## Gotchas
- **`webDash/` is a duplicate, not a second app.** `webDash/` and `webDash/public/` are a byte-identical copy of the root `public/`, kept in sync (commit `9d4203c`). The Cloudflare deploy targets the **root** `./public`. Do all work in the root `public/` — never edit or add files under `webDash/` (it has no build, no config of its own).
- Contains real medical PDFs and PHI-adjacent data. Keep this repo out of any shared, public, or external context (don't paste record contents into web tools).
- The exact `wrangler` subcommand isn't captured in a script — `wrangler.jsonc` is a static-assets config (no `main`), so `wrangler deploy` is the expected path; confirm on first run.
