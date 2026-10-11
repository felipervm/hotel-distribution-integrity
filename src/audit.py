"""Independent synthetic audit: compare each channel snapshot against a fictional central reference."""
from __future__ import annotations
import csv, json
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
FIELDS = ["stay_date","room_type","rate_plan","channel","currency","occupancy","meal_plan","tax_basis","promotion_code","nightly_rate","availability","cancel_window_hours","bookable"]
ISSUES = {
    "RATE_DIFFERENCE_REVIEW": ("MEDIUM","Revenue management / channel owner","Confirm negotiated/promotional conditions and all-in price before correcting."),
    "AVAILABILITY_DIFFERENCE_REVIEW": ("HIGH","Distribution systems / connectivity","Validate channel timestamps, allotment and connectivity before changing inventory."),
    "CANCELLATION_POLICY_REVIEW": ("MEDIUM","Distribution content / policy","Confirm cancellation text and source configuration before publishing changes."),
    "BOOKABILITY_REVIEW": ("HIGH","Distribution systems / connectivity","Verify booking path and rate mapping, then escalate with reproducible evidence."),
    "INCOMPARABLE_RATE_BASIS": ("MEDIUM","Rate configuration / channel partner","Normalize tax and promotion basis; do not call this a rate defect yet."),
    "MISSING_REFERENCE": ("HIGH","Distribution operations","Find a valid comparison baseline before interpreting this observation."),
}
KEY = ("stay_date","room_type","rate_plan")
BASIS = ("currency","occupancy","meal_plan","tax_basis","promotion_code")

def money(value):
    try:
        amount = Decimal(value)
    except InvalidOperation as error:
        raise ValueError("Invalid nightly rate") from error
    if not amount.is_finite() or amount < 0:
        raise ValueError("Nightly rate must be finite and non-negative")
    return amount

def validate(records):
    seen = set()
    for row in records:
        if any(not isinstance(row.get(k), str) or not row[k].strip() for k in FIELDS):
            raise ValueError("Missing required snapshot field")
        date.fromisoformat(row["stay_date"])
        key = tuple(row[k] for k in KEY) + (row["channel"],)
        if key in seen:
            raise ValueError("Duplicate channel snapshot: " + str(key))
        seen.add(key)
        if int(row["availability"]) < 0 or int(row["cancel_window_hours"]) < 0:
            raise ValueError("Negative inventory or cancellation window")
        if int(row["occupancy"]) < 1:
            raise ValueError("Occupancy must be positive")
        if row["bookable"] not in ("Yes", "No"):
            raise ValueError("Bookable must be Yes or No")
        money(row["nightly_rate"])

def read_snapshot(path=DATA/"channel_snapshot.csv"):
    with open(path,newline="",encoding="utf-8") as file:
        records=list(csv.DictReader(file))
    validate(records)
    return records

def audit(records):
    validate(records)
    baseline={tuple(row[k] for k in KEY):row for row in records if row["channel"]=="CENTRAL_REFERENCE"}
    results=[]
    for row in records:
        if row["channel"]=="CENTRAL_REFERENCE": continue
        ref=baseline.get(tuple(row[k] for k in KEY))
        issues=[]
        if ref is None: issues.append("MISSING_REFERENCE")
        else:
            same_basis=all(row[k]==ref[k] for k in BASIS)
            if not same_basis: issues.append("INCOMPARABLE_RATE_BASIS")
            elif money(row["nightly_rate"])!=money(ref["nightly_rate"]): issues.append("RATE_DIFFERENCE_REVIEW")
            if int(row["availability"])!=int(ref["availability"]): issues.append("AVAILABILITY_DIFFERENCE_REVIEW")
            if int(row["cancel_window_hours"])!=int(ref["cancel_window_hours"]): issues.append("CANCELLATION_POLICY_REVIEW")
            if row["bookable"]!=ref["bookable"]: issues.append("BOOKABILITY_REVIEW")
        severity={"HIGH":3,"MEDIUM":2,"LOW":1}
        chosen=max(issues,key=lambda i:severity[ISSUES[i][0]]) if issues else None
        priority,team,action=ISSUES[chosen] if chosen else ("NONE","","")
        results.append({**row,"issues":" | ".join(issues) if issues else "ALIGNED","priority":priority,
                        "issue_count":len(issues),"assigned_team":team,"next_action":action,
                        "review_status":"OPEN" if issues else "NOT_REQUIRED"})
    return results

def build_report(records, results):
    baseline = {tuple(row[k] for k in KEY): row for row in records if row["channel"] == "CENTRAL_REFERENCE"}
    findings = []
    for row in results:
        if not row["issue_count"]:
            continue
        ref = baseline.get(tuple(row[k] for k in KEY))
        differences = [k for k in BASIS if ref and row[k] != ref[k]]
        findings.append({**row, "reference": ref, "basis_differences": differences,
            "rate_delta": str(money(row["nightly_rate"]) - money(ref["nightly_rate"])) if ref and not differences else None,
            "evidence_required": ["Timestamped central and channel captures for the same stay and occupancy", "Validated room and rate-plan mapping; tax, meal and promotion terms", "Channel allotment and restrictions; reproducible booking path; published policy text"]})
    return {"synthetic": True, "metrics": {"source_records": len(records), "comparisons": len(results),
        "aligned": sum(r["issues"] == "ALIGNED" for r in results), "review_cases": len(findings),
        "incomparable": sum("INCOMPARABLE_RATE_BASIS" in r["issues"] for r in results),
        "high_priority": sum(r["priority"] == "HIGH" for r in results)}, "findings": findings}

def write_outputs(results):
    with open(DATA/"audit_results.csv","w",newline="",encoding="utf-8") as file:
        writer=csv.DictWriter(file,fieldnames=FIELDS+["issues","priority","issue_count","assigned_team","next_action","review_status"])
        writer.writeheader();writer.writerows(results)
    findings=[r for r in results if r["issue_count"]]
    (DATA/"findings.json").write_text(json.dumps(findings,indent=2)+"\n",encoding="utf-8")
    return findings

if __name__=="__main__":
    rows=read_snapshot()
    results=audit(rows)
    findings=write_outputs(results)
    (DATA/"report.json").write_text(json.dumps(build_report(rows, results), indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"synthetic":True,"snapshot_rows":len(rows),"comparisons":len(results),"review_cases":len(findings)},indent=2))
