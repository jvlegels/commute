# Commute Advisor (Gentbrugge ↔ Schuman)

A mobile-friendly web app to help decide each morning between:
- **Car**
- **Train + metro** (Gentbrugge → Brussel-Centraal + metro to Schuman)

## What it does
When you open the app, it asks what time you expect to leave the office in the evening. It then compares both options for the **full day commute** (morning + evening), adds a **visual dashboard**, and gives a recommendation.

The comparison includes:
- Typical weekday and evening traffic effects
- School holiday effect
- Current weather (comfort impact)
- Live check of your regular **07:50 Gentbrugge** train (delay/cancellation)

## Visual dashboard
After you tap **Get recommendation**, the app renders:
- Bar comparisons for total time, morning time, and evening time
- Bar comparisons for comfort, reliability, and overall score
- A summary table showing which mode wins each metric

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

## Notes
- If live APIs are temporarily unavailable, the app still produces a recommendation with fallback assumptions.
- `commute_advisor.py` remains available as the CLI prototype; `index.html` is the recommended app for daily use.
