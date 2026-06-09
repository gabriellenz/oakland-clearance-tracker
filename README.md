# Oakland Homicide Clearance Tracker

This is the public reference implementation for a homicide clearance tracker. It contains the static website, cleaned public JSON, and general replication guidance. Oakland is the first example city.

The public repo is the canonical home for the reusable model. Private working trackers should keep raw research, cache files, records-request drafts, and full CSVs outside the public repo.

## How The Model Works

- Track one row per homicide victim.
- Keep incident, suspect, source, check, records-request, and count-report tables privately.
- Publish only a cleaned JSON export plus public-facing pages.
- Use stable local IDs and sort by dates; do not renumber old rows.
- Add source rows before changing fact rows.
- Reconcile against published count checkpoints, but do not create placeholder victims just to match a count.
- Treat public arrest status as a source-backed public proxy, not final clearance or conviction.
- Code race/ethnicity only from explicit credible sources.
- Keep alleged perpetrator names out of public summaries and front-page tables unless your local rules explicitly choose otherwise.
- Automate mechanical audits, but keep source judgment human/agent-reviewed.

## Repo Split

Use two repos:

- Public repo: static site, cleaned JSON, reusable docs, and build/publish scripts.
- Private repo: working CSVs, raw downloads, source cache, research notes, and automation memory.

For Oakland, the private repo keeps this public repo as a submodule. Daily automation runs from the private workspace, updates private data, runs `scripts/publish_update.sh` in the public repo, and backs up the private repo with the current public-site pointer.

Oakland's private repo includes `Oakland/scripts/audit_public_data.py`, which checks IDs, source references, status math, public JSON parity, and public-summary name leaks before publishing.

## Start One For Your City

You can use this repo as a template for a homicide clearance tracker in another city. Point Codex, Claude Code, or another agentic coding system to this repo and ask it to read [`START_A_CITY_TRACKER.md`](START_A_CITY_TRACKER.md), inspect the Oakland structure, and scaffold a private tracker plus public site for your city.

When your city is running, email the site owner, Gabriel, at [gabe.lenz@gmail.com](mailto:gabe.lenz@gmail.com?subject=I%20started%20a%20homicide%20clearance%20tracker) with your public GitHub repo and live URL. It can be added to the Clear the Murders network at `yourcity.clearthemurders.org`.

## Public Language

Use plain public-facing language such as "solving homicides" in headlines and calls to action. Keep "homicide clearance" in the page title, metadata, documentation, and explanatory copy so search engines and technical readers can still find the project by the standard term.

## Files

- `index.html` - static page
- `updates.html` - forward-looking log of homicide and arrest/charging discoveries
- `styles.css` - responsive visual design
- `app.js` - dashboard rendering and filters
- `updates.js` - update-log rendering
- `data/oakland-2026.json` - public derived dataset
- `scripts/build_public_data.py` - regenerates the public JSON from the local working tracker
- `START_A_CITY_TRACKER.md` - guide and starter prompt for adapting this workflow to another city

## Local Development

From this folder, when the matching private tracker exists at the expected path, use the build script for local preview only:

```bash
python3 scripts/build_public_data.py
python3 -m http.server 4173
```

Then open `http://localhost:4173`.

For actual publishing, use `scripts/publish_update.sh`.

## Update Path

For Oakland, the intended daily workflow is:

1. Update the private tracker in `/Users/canardcanardy/Clearance/Oakland`.
2. Run the publish script from this public repo.
3. Let the script rebuild and validate public JSON, push public data if changed, and back up the private tracker pointer.

```bash
bash scripts/publish_update.sh
```

The public page loads only `data/oakland-2026.json`; it does not fetch private tracker files or private notes.

## Publication Safety Checklist

Before pushing:

- Confirm `data/oakland-2026.json` contains only public-facing fields.
- Confirm the homepage and public narrative summaries do not display alleged perpetrator names.
- If alleged perpetrator names are present in structured JSON fields, confirm they are labeled as allegations and not findings of guilt.
- Confirm non-homicide updates, such as weapons or ammunition charges, are not presented as alleged homicide-perpetrator fields.
- Do not copy `_cache/`, draft request text, private notes, or the full working CSVs into this repo unless intentionally public.
- Run `node --check app.js` and `node --check updates.js`.
- Verify the generated JSON matches private tracker totals.

## Related Repos

- Public website repo: `gabriellenz/oakland-clearance-tracker`
- Private backup repo for the broader working folder: `gabriellenz/clearance-private`
