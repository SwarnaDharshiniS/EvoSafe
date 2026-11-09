# Running and deploying the demo website

The demo is a small web app: a browser UI (`public/`) that sends Python source to an analysis API (`api/index.py`, FastAPI) and shows the results. The API only **parses and analyses** the source with EvoSafe. It never imports or runs submitted code, and it does not expose the sandbox / execution modules.

```
browser (public/index.html, app.js, style.css)
   │  POST /api/analyze  { source, analyses: [...] }
   ▼
api/index.py  ──►  webapp/service.py  ──►  analysis/, cfg/, parser/
```

## Run it locally

```bash
python3 -m pip install -r requirements.txt uvicorn
python3 dev_server.py            # open http://127.0.0.1:8000
```

`dev_server.py` serves the UI and the API on one port. Interactive API docs are at `/api/docs`.

## Why GitHub Pages alone is not enough

GitHub Pages serves static files only. The analysis is Python, so it needs somewhere to run. Two ways to use Pages anyway:

1. **Recommended: host everything on Vercel** (below). One deployment, same origin, no CORS.
2. **UI on GitHub Pages, API on Vercel.** Deploy the API to Vercel, set `EVOSAFE_CORS_ORIGINS=https://<user>.github.io` in the Vercel project, set `window.EVOSAFE_API = "https://<project>.vercel.app"` in `public/config.js`, and publish `public/` to Pages. This adds moving parts without adding anything, so use it only if you specifically want a `github.io` address.

## Deploy to Vercel (free Hobby plan is enough)

1. Push this repository to GitHub (already done).
2. Sign in at <https://vercel.com> with your GitHub account and choose **Add New → Project**.
3. Import `SwarnaDharshiniS/EvoSafe`. Leave **Framework Preset** as *Other* and the build/output settings empty.
4. Select **Deploy**. Vercel reads `vercel.json` (routes `/api/*` to `api/index.py`), installs `requirements.txt`, serves `public/` as the site, and runs `api/index.py` as a Python serverless function. `.vercelignore` keeps the 70 MB dataset out of the bundle.
5. Every push to `main` redeploys automatically. Add a custom domain under **Settings → Domains** if you want one.

Check it: open `/api/health` (should return `{"status":"ok",…}`), then the home page.

## Limits and safety of the public demo

- Input is capped at 60,000 characters and 2,000 lines (`webapp/service.py`). Syntax errors come back with their line number.
- Vercel enforces its own function timeout and platform rate limits. There is no authentication; do not put anything secret in the analysed examples.
- The demo does not store submitted code.
- Analysis is static and approximate; see the Known limitations section of the README.

## Updating the Evaluation page

The Evaluation page reads `public/data/review2.json`, generated from the frozen metrics:

```bash
python3 scripts/build_demo_data.py
```
