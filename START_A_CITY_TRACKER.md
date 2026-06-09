# Start A Tracker For Your City

This public repo is the reusable reference. It should contain enough information for another city to copy the model without exposing Oakland's private research workspace.

## Setup Pattern

- Public repo: static site, cleaned JSON, reusable docs, and build/publish scripts.
- Private repo or private folder: full CSVs, raw downloads, research notes, public-records drafts, and automation memory.
- Published data: cleaned JSON only.
- Recurring agent run: updates private data, rebuilds public JSON, validates privacy and counts, then publishes the public site.

## Starter Prompt

```text
I want to create a public homicide clearance tracker for [CITY], [STATE] for [YEAR], modeled on https://github.com/gabriellenz/oakland-clearance-tracker.

Read the public repo README and this starter guide. Set up a private working tracker plus a public static site.

Private tracker tables:
- victims_YEAR.csv, one row per homicide victim
- incidents_YEAR.csv, one row per incident
- suspects_YEAR.csv, one row per public alleged perpetrator
- sources_YEAR.csv, one row per source item
- checks_YEAR.csv, one row per recurring update run
- count_reports_YEAR.csv, published homicide-count checkpoints
- requests_YEAR.csv, public-records request tracker

Rules:
- Use stable IDs and do not renumber old records.
- Add source rows before fact rows.
- Keep public arrest, charges, official clearance, and court outcome separate.
- Do not infer race/ethnicity.
- Do not publish private notes, raw cache files, or records-request drafts.
- Keep alleged perpetrator names out of public summaries and front-page tables unless a local policy explicitly chooses otherwise.
- Do not count weapons, ammunition, accessory, or unrelated custody updates as homicide arrests unless the source directly ties the person to a homicide/death arrest or charge.
- Preserve count discrepancies until a sourced incident explains them.

First propose the city-specific scope rules, source registry, file structure, and first backfill plan.
```

## Tell Us

When your tracker is running, email Gabriel at [gabe.lenz@gmail.com](mailto:gabe.lenz@gmail.com?subject=I%20started%20a%20homicide%20clearance%20tracker) with the city/year, public repo, live URL, update cadence, and any scope differences from Oakland.
