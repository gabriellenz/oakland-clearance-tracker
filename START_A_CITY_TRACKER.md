# Start a Homicide Clearance Tracker for Your City

This repo is the public Oakland example. It contains a static website, cleaned public JSON, and the build script that turns private tracker CSVs into public data.

The goal is not to accuse individuals or replace official records. The goal is to track whether homicide cases have a public arrest or charging update, show the source links, and make it easier for residents to hold local government accountable for solving serious violence.

## What You Need

- A city, year, police agency, prosecutor, and court system to track.
- A private working folder for research notes, raw downloads, public-records drafts, and full CSVs.
- A public repo for the static site and cleaned derived data only.
- A daily or weekly agent run using Codex, Claude Code, or another agentic coding/research system.

## Core Data Model

Keep these tables privately:

- `victims_YEAR.csv`: one row per homicide victim.
- `incidents_YEAR.csv`: one row per incident, with short public-facing summaries.
- `suspects_YEAR.csv`: one row per public alleged perpetrator.
- `sources_YEAR.csv`: one row per article, official release, court item, or public-data extract.
- `checks_YEAR.csv`: one row per recurring update run.
- `count_reports_YEAR.csv`: published homicide-count claims used for reconciliation.

Publish only a cleaned JSON export. Do not publish raw cache files, draft records requests, private notes, or anything that is not intended for the public site.

## Scope Rules to Decide First

- Which deaths count as in-scope homicides.
- How to handle officer-involved fatal shootings.
- How to handle vehicular homicides, delayed deaths, self-defense claims, and remains cases.
- How to code race/ethnicity. The Oakland rule is source-only: leave it blank unless a credible source explicitly reports it.
- How to display alleged perpetrator names. The Oakland public site does not render alleged names in summaries or front-page tables.

## Suggested Agent Prompt

Use this as a starting prompt in Codex, Claude Code, or a similar coding agent:

```text
I want to create a public homicide clearance tracker for [CITY], [STATE] for [YEAR], modeled on https://github.com/gabriellenz/oakland-clearance-tracker.

Set up a private working tracker with victim, incident, suspect, source, check, request, and count-report CSVs. Then create a public static site that publishes only cleaned JSON and public-facing pages.

Rules:
- One row per homicide victim.
- Keep incident and suspect side tables for dedupe and arrest tracking.
- Separate public arrest reported, charges filed, official clearance, and court outcome.
- Do not infer race or ethnicity from names, photos, or context.
- Do not render alleged perpetrator names in public summaries or front-page tables.
- Save source links and discovery dates so a public update log can show when new homicides and arrest updates were found.
- Draft public-records emails for review; do not send automatically.

First read the Oakland repo structure and README. Then propose the local file structure, scope rules, source list, and first backfill plan for my city.
```

## Recurring Run Checklist

1. Read the local instructions, tracker docs, and previous automation memory.
2. Check official police releases, open data, weekly or monthly crime reports, prosecutor releases, court portals, and local news.
3. Search for new homicide incidents, victim identifications, arrest updates, charging updates, and published count reports.
4. Add source rows first, then update victims, incidents, suspects, count reports, and check logs.
5. Keep count discrepancies visible. Do not add placeholder victims just to match a published total.
6. Rebuild public JSON and verify it contains no private paths, raw notes, or draft request text.
7. Verify public summaries and homepage tables do not display alleged perpetrator names.
8. Run the site locally, inspect it in a browser, commit, push, and confirm the Pages deploy.

## Tell Us About Your Tracker

When your city tracker is running, email Gabriel Lenz at [gabe.lenz@gmail.com](mailto:gabe.lenz@gmail.com?subject=I%20started%20a%20homicide%20clearance%20tracker) with:

- the city and year covered
- the public GitHub repo
- the live site URL
- the recurring update cadence
- any important scope differences from Oakland

If it is ready for public use, it can be linked from `yourcity.clearthemurders.org`.
