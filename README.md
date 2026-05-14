# Oakland Homicide Clearance Tracker

Static public website for tracking publicly reported Oakland homicide clearance indicators in 2026.

This public repo contains only the website and the cleaned public JSON data needed to render it. The private working tracker, source cache, and research notes live outside this repo.

## Files

- `index.html` - static page
- `styles.css` - responsive visual design
- `app.js` - dashboard rendering and filters
- `data/oakland-2026.json` - public derived dataset
- `scripts/build_public_data.py` - regenerates the public JSON from the local working tracker

## Local Development

From this folder:

```bash
python3 scripts/build_public_data.py
python3 -m http.server 4173
```

Then open `http://localhost:4173`.

## Update Path

The intended daily workflow is:

1. Update the private tracker in `/Users/canardcanardy/Clearance/Oakland`.
2. Run `python3 scripts/build_public_data.py`.
3. Review the local site.
4. Commit and push changed public files.

For data-only updates after the private tracker is already current:

```bash
bash scripts/publish_update.sh
```

The public page loads only `data/oakland-2026.json`; it does not fetch private tracker files.
