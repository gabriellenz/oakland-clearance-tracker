#!/usr/bin/env python3
"""Build the public JSON dataset for the Oakland clearance site.

This script intentionally exports a cleaned subset of the working tracker.
It excludes cache files, research notes, private workflow files, and verbose
internal notes that are not needed for the public page.
"""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path


REPO_DIR = Path(__file__).resolve().parents[1]
TRACKER_DIR = REPO_DIR.parents[1] / "Oakland"
OUT_PATH = REPO_DIR / "data" / "oakland-2026.json"


def read_csv(name: str) -> list[dict[str, str]]:
    with (TRACKER_DIR / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def parse_date(value: str) -> date | None:
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


def pct(numerator: int, denominator: int) -> float:
    return round((numerator / denominator) * 100, 1) if denominator else 0.0


def public_value(value: str) -> str:
    return value if value else "unknown"


def main() -> None:
    victims = read_csv("victims_2026.csv")
    incidents = read_csv("incidents_2026.csv")
    sources = read_csv("sources_2026.csv")
    count_reports = read_csv("count_reports_2026.csv")

    victims = sorted(victims, key=lambda r: (r["incident_date"], r["incident_time"], r["victim_id"]))
    incidents_by_id = {r["incident_id"]: r for r in incidents}
    sources_by_id = {r["source_id"]: r for r in sources}

    status_counts = Counter(r["arrest_made"] or "unknown" for r in victims)
    month_counts: dict[str, Counter[str]] = defaultdict(Counter)
    cumulative = []
    running_victims = 0
    running_arrests = 0
    for victim in victims:
        month_counts[victim["incident_date"][:7]][victim["arrest_made"] or "unknown"] += 1
        running_victims += 1
        if victim["arrest_made"] == "yes":
            running_arrests += 1
        cumulative.append(
            {
                "date": victim["incident_date"],
                "victims": running_victims,
                "arrestReportedVictims": running_arrests,
            }
        )

    public_victims = []
    for row in victims:
        incident = incidents_by_id.get(row["incident_id"], {})
        arrest_source = sources_by_id.get(row["arrest_source_id"], {})
        public_victims.append(
            {
                "victimId": row["victim_id"],
                "incidentId": row["incident_id"],
                "name": public_value(row["victim_name"]),
                "age": row["victim_age"],
                "gender": row["victim_gender"],
                "raceEthnicity": row["victim_race_ethnicity_public"],
                "incidentDate": row["incident_date"],
                "incidentTime": row["incident_time"],
                "location": row["location_block"],
                "neighborhood": row["neighborhood"],
                "method": row["manner_or_method"],
                "circumstancesSummary": incident.get("circumstances_summary", ""),
                "caseNumber": row["opd_case_number"] or incident.get("official_case_number", ""),
                "arrestMade": row["arrest_made"] or "unknown",
                "arrestDate": row["arrest_date"],
                "arrestSourceId": row["arrest_source_id"],
                "arrestSourceUrl": arrest_source.get("url", ""),
                "arrestSourceTitle": arrest_source.get("title", ""),
                "arrestSourcePublisher": arrest_source.get("publisher", ""),
                "arrestSourceDate": arrest_source.get("source_date", ""),
                "suspectsPublic": row["suspect_names_public"],
                "chargesFiled": row["charges_filed"],
                "leadCharge": row["lead_charge_public"],
                "caseStatus": row["case_status_public"],
                "clearanceStatus": row["clearance_status_public"],
                "confidence": row["confidence"],
            }
        )

    public_incidents = [
        {
            "incidentId": row["incident_id"],
            "date": row["incident_date"],
            "time": row["incident_time"],
            "location": row["location_block"],
            "neighborhood": row["neighborhood"],
            "method": row["manner_or_method"],
            "circumstancesSummary": row.get("circumstances_summary", ""),
            "victimCount": row["victim_count_public"],
            "caseNumber": row["official_case_number"],
            "confidence": row["confidence"],
        }
        for row in sorted(incidents, key=lambda r: (r["incident_date"], r["incident_time"], r["incident_id"]))
    ]

    public_counts = []
    for row in count_reports:
        if not row["reported_total_homicides"]:
            continue
        public_counts.append(
            {
                "sourceDate": row["source_date"],
                "publisher": row["publisher"],
                "title": row["title"],
                "url": row["url"],
                "periodEnd": row["reported_period_end"],
                "reportedTotal": int(row["reported_total_homicides"]),
                "unit": row["count_unit"],
                "trackerVictimCount": int(row["tracker_victim_count_as_of_entry"] or 0),
                "discrepancy": row["discrepancy"],
            }
        )

    by_month = [
        {
            "month": month,
            "yes": counts.get("yes", 0),
            "no": counts.get("no", 0),
            "unknown": counts.get("unknown", 0),
            "total": sum(counts.values()),
        }
        for month, counts in sorted(month_counts.items())
    ]

    total_victims = len(victims)
    arrest_yes = status_counts.get("yes", 0)
    arrest_no = status_counts.get("no", 0)
    arrest_unknown = status_counts.get("unknown", 0)
    incident_count = len({r["incident_id"] for r in victims})
    named_victims = sum(1 for r in victims if r["victim_name"] and r["victim_name"] != "unknown")
    last_checked = max((r["last_checked"] for r in victims if r["last_checked"]), default="")

    data = {
        "metadata": {
            "city": "Oakland",
            "state": "CA",
            "year": 2026,
            "generatedAt": datetime.now().astimezone().isoformat(timespec="seconds"),
            "lastChecked": last_checked,
            "scopeNote": "Officer-involved fatal shootings are excluded from the main tracker. Arrest reported is a public-source proxy, not an official clearance determination.",
            "q1ReconciliationNote": "Published OPD/news count reports indicate 14 homicides through March 31, while the current coded tracker has 13 victims through that date. One pre-February-22 case or classification mismatch remains unresolved.",
        },
        "summary": {
            "victims": total_victims,
            "incidents": incident_count,
            "arrestReportedVictims": arrest_yes,
            "noPublicArrestVictims": arrest_no,
            "unknownArrestStatusVictims": arrest_unknown,
            "publicArrestRateVictimLevel": pct(arrest_yes, total_victims),
            "namedVictims": named_victims,
            "raceEthnicityKnownVictims": sum(1 for r in victims if r["victim_race_ethnicity_public"]),
        },
        "statusCounts": dict(status_counts),
        "byMonth": by_month,
        "cumulative": cumulative,
        "victims": public_victims,
        "incidents": public_incidents,
        "countReports": public_counts,
    }

    OUT_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
