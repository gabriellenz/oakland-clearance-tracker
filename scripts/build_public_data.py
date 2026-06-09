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
import re


REPO_DIR = Path(__file__).resolve().parents[1]
TRACKER_DIR = REPO_DIR.parents[1] / "Oakland"
OUT_PATH = REPO_DIR / "data" / "oakland-2026.json"
UPDATE_LOG_START = "2026-05-18"
GENERATED_AT_PATH = ("metadata", "generatedAt")


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


def split_names(value: str) -> list[str]:
    if not value or value == "unknown":
        return []
    return [name.strip() for name in re.split(r";|,", value) if name.strip() and name.strip() != "unknown"]


def charge_summary(row: dict[str, str]) -> str:
    charges = row["charges_filed"] or "unknown"
    lead = row["lead_charge_public"].strip()
    if row["arrest_made"] == "yes":
        if charges == "yes" and lead:
            return f"Charge: {lead}"
        if charges == "yes":
            return "Charges"
        return "Public arrest reported"
    if row["arrest_made"] == "no":
        return "None reported"
    return "Unknown"


def public_summary(summary: str, suspect_names: set[str], incident_victims: list[dict[str, str]]) -> str:
    if not summary:
        return ""

    protected = summary.strip().replace("Jr.", "Jr<DOT>").replace("Sr.", "Sr<DOT>")
    sentences = [sentence.replace("Jr<DOT>", "Jr.").replace("Sr<DOT>", "Sr.") for sentence in re.split(r"(?<=[.!?])\s+", protected)]
    kept = [
        sentence
        for sentence in sentences
        if not any(name and name in sentence for name in suspect_names)
    ]

    if len(kept) == len(sentences):
        return summary

    arrest_values = {row["arrest_made"] for row in incident_victims}
    charges = "; ".join(row["lead_charge_public"] for row in incident_victims if row["lead_charge_public"])
    extra = ""
    if "yes" in arrest_values:
        if "accessory" in charges and "murder" in charges:
            extra = "Later reporting said prosecutors filed murder charges and an accessory-after-the-fact charge."
        elif "murder" in charges:
            extra = "Later reporting said prosecutors filed murder charges in the case."
        elif any(row["charges_filed"] == "yes" for row in incident_victims):
            extra = "Later reporting said prosecutors filed charges in the case."
        else:
            extra = "Public sources later reported an arrest in the case."

    return " ".join([*kept, extra]).strip()


def source_link(source: dict[str, str]) -> dict[str, str]:
    return {
        "sourceId": source.get("source_id", ""),
        "title": source.get("title", ""),
        "publisher": source.get("publisher", ""),
        "url": source.get("url", ""),
        "sourceDate": source.get("source_date", ""),
    }


def without_generated_at(data: dict) -> dict:
    copy = json.loads(json.dumps(data))
    node = copy
    for key in GENERATED_AT_PATH[:-1]:
        node = node.get(key, {})
    node.pop(GENERATED_AT_PATH[-1], None)
    return copy


def preserve_generated_at_if_unchanged(data: dict) -> dict:
    if not OUT_PATH.exists():
        return data

    try:
        existing = json.loads(OUT_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return data

    if without_generated_at(existing) == without_generated_at(data):
        data["metadata"]["generatedAt"] = existing.get("metadata", {}).get("generatedAt", data["metadata"]["generatedAt"])
    return data


def main() -> None:
    victims = read_csv("victims_2026.csv")
    incidents = read_csv("incidents_2026.csv")
    sources = read_csv("sources_2026.csv")
    count_reports = read_csv("count_reports_2026.csv")
    checks = read_csv("checks_2026.csv")

    victims = sorted(victims, key=lambda r: (r["incident_date"], r["incident_time"], r["victim_id"]))
    incidents_by_id = {r["incident_id"]: r for r in incidents}
    sources_by_id = {r["source_id"]: r for r in sources}
    victims_by_incident: dict[str, list[dict[str, str]]] = defaultdict(list)
    suspect_names_by_incident: dict[str, set[str]] = defaultdict(set)
    for row in victims:
        victims_by_incident[row["incident_id"]].append(row)
        suspect_names_by_incident[row["incident_id"]].update(split_names(row["suspect_names_public"]))

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
        summary = public_summary(
            incident.get("circumstances_summary", ""),
            suspect_names_by_incident[row["incident_id"]],
            victims_by_incident[row["incident_id"]],
        )
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
                "circumstancesSummary": summary,
                "caseNumber": row["opd_case_number"] or incident.get("official_case_number", ""),
                "arrestMade": row["arrest_made"] or "unknown",
                "arrestDate": row["arrest_date"],
                "arrestSourceId": row["arrest_source_id"],
                "arrestSourceUrl": arrest_source.get("url", ""),
                "arrestSourceTitle": arrest_source.get("title", ""),
                "arrestSourcePublisher": arrest_source.get("publisher", ""),
                "arrestSourceDate": arrest_source.get("source_date", ""),
                "allegedPerpetratorsPublic": row["suspect_names_public"],
                "allegedPerpetratorLanguage": "Names are public allegations from cited sources and are not findings of guilt.",
                "chargesFiled": row["charges_filed"],
                "leadCharge": row["lead_charge_public"],
                "publicChargeSummary": charge_summary(row),
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
            "circumstancesSummary": public_summary(
                row.get("circumstances_summary", ""),
                suspect_names_by_incident[row["incident_id"]],
                victims_by_incident[row["incident_id"]],
            ),
            "victimCount": row["victim_count_public"],
            "caseNumber": row["official_case_number"],
            "confidence": row["confidence"],
        }
        for row in sorted(incidents, key=lambda r: (r["incident_date"], r["incident_time"], r["incident_id"]))
    ]

    update_log = []
    seen_log_keys = set()
    for row in victims:
        primary = sources_by_id.get(row["primary_source_id"], {})
        primary_found = primary.get("date_found", "")
        if primary_found >= UPDATE_LOG_START:
            key = ("homicide_found", row["victim_id"], primary_found)
            if key not in seen_log_keys:
                update_log.append(
                    {
                        "dateFound": primary_found,
                        "type": "homicide_found",
                        "label": "Homicide added to tracker",
                        "victimId": row["victim_id"],
                        "incidentId": row["incident_id"],
                        "incidentDate": row["incident_date"],
                        "victimName": public_value(row["victim_name"]),
                        "location": row["location_block"],
                        "source": source_link(primary),
                    }
                )
                seen_log_keys.add(key)

        arrest = sources_by_id.get(row["arrest_source_id"], {})
        arrest_found = arrest.get("date_found", "")
        if row["arrest_made"] == "yes" and arrest_found >= UPDATE_LOG_START:
            key = ("arrest_found", row["victim_id"], arrest_found)
            if key not in seen_log_keys:
                update_log.append(
                    {
                        "dateFound": arrest_found,
                        "type": "arrest_found",
                        "label": "Arrest or charges found",
                        "victimId": row["victim_id"],
                        "incidentId": row["incident_id"],
                        "incidentDate": row["incident_date"],
                        "victimName": public_value(row["victim_name"]),
                        "location": row["location_block"],
                        "source": source_link(arrest),
                    }
                )
                seen_log_keys.add(key)
    update_log = sorted(update_log, key=lambda r: (r["dateFound"], r["incidentDate"], r["victimId"], r["type"]), reverse=True)

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
    last_checked = max(
        (
            r["checked_at"][:10]
            for r in checks
            if r.get("checked_at") and r.get("scope", "").startswith("daily automation")
        ),
        default=max((r["last_checked"] for r in victims if r["last_checked"]), default=""),
    )

    data = {
        "metadata": {
            "city": "Oakland",
            "state": "CA",
            "year": 2026,
            "generatedAt": datetime.now().astimezone().isoformat(timespec="seconds"),
            "lastChecked": last_checked,
            "scopeNote": "Officer-involved fatal shootings are excluded from the main tracker. Arrest reported is a public-source proxy, not an official clearance determination.",
            "q1ReconciliationNote": "Published OPD/news count reports indicate 14 homicides through March 31. A May 18 audit found a Feb. 11 fatal shooting near International Boulevard and 98th Avenue, bringing the coded tracker to 14 victims through March 31.",
            "allegedPerpetratorNote": "Public datasets may include names of alleged perpetrators from cited sources. The website does not display those names in summaries or the front-page table, and names should be read as allegations, not findings of guilt.",
            "updateLogStartDate": UPDATE_LOG_START,
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
        "updateLog": update_log,
    }

    data = preserve_generated_at_if_unchanged(data)
    OUT_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
