# Commute Advisor (Gentbrugge ↔ Schuman)

A mobile-friendly web app to help decide each morning between:
- **Car**
- **Train + metro** (Gentbrugge → Brussel-Centraal + metro to Schuman)

## What it does
When you open the app, it asks what time you expect to leave the office in the evening. After you tap **Update dashboard**, it first shows a **live morning overview**, then gives the analysis, score and recommendation for the full day commute.

The comparison includes:
- All current Gentbrugge → Brussel-Centraal train options leaving between **07:30 and 08:30**
- Estimated train departure and arrival times, delay/cancellation status and the train used for scoring
- A current car-time estimate for Gentbrugge → Berlaymont based on the app traffic model
- An embedded Google Maps driving route plus a one-tap link to open live traffic in Google Maps
- Typical weekday and evening traffic effects
- School holiday effect
- Current weather (comfort impact)

## Morning overview and analysis dashboard
The app is ordered so the practical information appears first:
1. **Train board**: scheduled departure, estimated departure, scheduled arrival, estimated arrival, trip duration, status and platform for trains between 07:30 and 08:30.
2. **Car + map panel**: the current model estimate by car and a Google Maps route section. Open the map link for Google’s live traffic details and delay locations.
3. **Recommendation**: the suggested mode with confidence and score advantage.
4. **Analysis dashboard**: bar comparisons for total time, morning time, evening time and score, plus a summary table showing which mode wins each metric.

This makes the trade-offs much easier to read at a glance on phone.

## Run locally
Just open `index.html` in your browser.

For best API compatibility, run a simple local server:

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000`.

## Deploy on GitHub Pages (best for phone use)
1. Push this repository to GitHub.
2. In GitHub: **Settings → Pages**.
3. Under **Build and deployment**, choose:
   - **Source**: Deploy from a branch
   - **Branch**: `main` (or your default branch), `/ (root)`
4. Save and wait for deployment.
5. Open the generated URL from your phone and add it to your home screen if desired.

## Recommended: GitHub Actions Pages deployment
For more predictable updates, use the included workflow at `.github/workflows/pages.yml`.

1. In GitHub, go to **Settings → Pages**.
2. Under **Build and deployment**, set **Source** to **GitHub Actions**.
3. Push to `main` or `master`; the workflow will deploy automatically on either default branch.

This avoids many branch-source mismatch issues and makes deployments easier to trace in the Actions tab.

## Avoiding merge conflicts
If GitHub reports conflicts after you merge another PR first, update this branch from your default branch and keep the latest `index.html`, `README.md`, and `.github/workflows/pages.yml` from this branch. This PR intentionally keeps the app as a single static `index.html` file so the GitHub Pages deployment has very few moving parts.

## If GitHub Pages seems not updated
If you merged a PR but still see the old app, this is usually a deployment or cache issue:

1. **Check the branch Pages is publishing from** in `Settings → Pages` (it must match the branch you merged into, often `main`).
2. **Wait for Pages rebuild** (usually 1–5 minutes).
3. Open the site in a **private/incognito tab** or force refresh on phone.
4. Add a cache-busting suffix to the URL once, e.g. `?v=2026-05-29-1`.
5. Confirm you can see `Web app version 2026-05-29-1` at the top of the page.

If that version is visible, the new HTML is deployed. The current HTML also includes no-cache metadata to reduce stale browser caching.

## Notes
- If live APIs are temporarily unavailable, the app still produces a recommendation with fallback assumptions.
- Google Maps live traffic is shown through the Maps route/link; the app does not require a paid Google Maps API key.
- `commute_advisor.py` remains available as the CLI prototype; `index.html` is the recommended app for daily use.
