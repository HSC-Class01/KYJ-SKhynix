from __future__ import annotations
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from .dart_client import DartClient
from .normalize import load_yaml, normalize_report, compute_ratios

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config"
DATA = ROOT / "data"
RAW = DATA / "raw"
REPORTS_DIR = DATA / "reports"

REPORTS = {"annual": "11011", "half_year": "11012", "q1": "11013", "q3": "11014"}
DETAILS = {"annual": "A001", "half_year": "A002", "quarter": "A003"}

def _save_json(path: Path, payload: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

def _collect_filing_metadata(client: DartClient, corp_code: str, year: int) -> list[dict]:
    if year < 2015:
        return []
    start = f"{year}0101"
    end = f"{year}1231"
    result = []
    for category, detail in DETAILS.items():
        items = client.all_disclosures(corp_code, start, end, detail)
        for item in items:
            result.append({
                "year": year,
                "category": category,
                "report_nm": item.get("report_nm"),
                "rcept_no": item.get("rcept_no"),
                "rcept_dt": item.get("rcept_dt"),
                "viewer_url": client.viewer_url(item.get("rcept_no", "")),
            })
    return result

def run():
    settings = load_yaml(CONFIG / "settings.yml")
    metric_cfg = load_yaml(CONFIG / "metrics.yml")["metrics"]
    company = settings["company"]
    api_key = os.getenv("DART_API_KEY", "").strip()
    client = DartClient(api_key, RAW)
    start_year = int(company.get("start_year", 2010))
    api_start_year = max(start_year, 2015)  # OpenDART structured financial APIs are documented from 2015.
    end_year = datetime.now().year
    frames: list[pd.DataFrame] = []
    meta: list[dict] = []
    filings: list[dict] = []

    for year in range(api_start_year, end_year + 1):
        for label, code in REPORTS.items():
            try:
                payload = client.financials(company["corp_code"], year, code, company.get("fs_div", "CFS"))
                _save_json(RAW / f"{year}_{label}_{company['corp_code']}.json", payload)
                if payload.get("status") == "000":
                    frame = normalize_report(payload, year, code, company.get("fs_div", "CFS"), metric_cfg)
                    if not frame.empty:
                        frames.append(frame)
                    meta.append({"year": year, "category": label, "report_code": code, "status": "000"})
                else:
                    meta.append({"year": year, "category": label, "report_code": code, "status": payload.get("status"), "message": payload.get("message")})
            except Exception as exc:
                meta.append({"year": year, "category": label, "report_code": code, "status": "ERROR", "message": str(exc)})

        try:
            year_filings = _collect_filing_metadata(client, company["corp_code"], year)
            filings.extend(year_filings)
            _save_json(DATA / "filings" / f"{year}.json", {"year": year, "items": year_filings})
            if settings.get("documents", {}).get("download_original_reports", True):
                for item in year_filings:
                    rcept_no = item.get("rcept_no")
                    if not rcept_no:
                        continue
                    dest = REPORTS_DIR / str(year) / f"{rcept_no}.zip"
                    if dest.exists():
                        continue
                    try:
                        client.download_document(rcept_no, dest)
                    except Exception as exc:
                        item["download_error"] = str(exc)
        except Exception as exc:
            meta.append({"year": year, "category": "filings", "status": "ERROR", "message": str(exc)})

    df = pd.concat([x for x in frames if not x.empty], ignore_index=True) if frames else pd.DataFrame()
    if not df.empty:
        df = df.drop_duplicates(["year", "report_code", "metric"], keep="last")
        df.to_csv(DATA / "financial_metrics.csv", index=False, encoding="utf-8-sig")
        compute_ratios(df).to_csv(DATA / "financial_ratios.csv", index=False, encoding="utf-8-sig")
    else:
        pd.DataFrame(columns=["year", "report_code", "metric", "value"]).to_csv(DATA / "financial_metrics.csv", index=False, encoding="utf-8-sig")
        pd.DataFrame(columns=["year", "report_code"]).to_csv(DATA / "financial_ratios.csv", index=False, encoding="utf-8-sig")

    pd.DataFrame(meta).to_csv(DATA / "collection_log.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(filings).to_csv(DATA / "filings.csv", index=False, encoding="utf-8-sig")
    _save_json(DATA / "last_updated.json", {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "company": company["name"],
        "api_structured_financial_start_year": api_start_year,
        "requested_start_year": start_year,
        "note": "OpenDART structured financial API coverage is documented from 2015; 2010-2014 requires a separate historical backfill source.",
    })
    return df

if __name__ == "__main__":
    run()
