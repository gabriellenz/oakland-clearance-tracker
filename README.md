# Oakland Homicide Clearance Tracker

Static public website for tracking publicly reported Oakland homicide clearance indicators in 2026.

This public repo contains only the website and the cleaned public JSON data needed to render it. The private working tracker, source cache, and research notes live outside this repo.

## Files

- `index.html` - static page
- `updates.html` - forward-looking log of homicide and arrest/charging discoveries
- `styles.css` - responsive visual design
- `app.js` - dashboard rendering and filters
- `updates.js` - update-log rendering
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

## Publication Safety Checklist

Before pushing:

- Confirm `data/oakland-2026.json` contains only public-facing fields.
- Confirm the homepage and public narrative summaries do not display alleged perpetrator names.
- If alleged perpetrator names are present in structured JSON fields, confirm they are labeled as allegations and not findings of guilt.
- Do not copy `_cache/`, draft request text, private notes, or the full working CSVs into this repo unless intentionally public.
- Run `node --check app.js` and `node --check updates.js`.
- Serve locally with `python3 -m http.server 4173` and verify the page renders.
- After push, confirm the GitHub Pages workflow succeeded.

## Related Repos

- Public website repo: `gabriellenz/oakland-clearance-tracker`
- Private backup repo for the broader working folder: `gabriellenz/clearance-private`
