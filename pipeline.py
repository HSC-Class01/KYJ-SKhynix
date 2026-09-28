from __future__ import annotations
import json, os
from pathlib import Path
from datetime import datetime, timezone
import pandas as pd
from .dart_client import DartClient
from .normalize import load_yaml, normalize_report, compute_ratios

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config"
DATA = ROOT / "data"
RAW = DATA / "raw"

REPORTS = {"annual":"11011", "half_year":"11012", "q1":"11013", "q3":"11014"}

def run():
    settings = load_yaml(CONFIG / "settings.yml")
    metric_cfg = load_yaml(CONFIG / "metrics.yml")["metrics"]
    company = settings["company"]
    api_key = os.getenv("DART_API_KEY", "").strip()
    client = DartClient(api_key, RAW)
    start_year = int(company.get("start_year", 2010))
    end_year = datetime.now().year
    frames = []
    meta = []
    for year in range(start_year, end_year + 1):
        for label, code in REPORTS.items():
            try:
                payload = client.financials(company["corp_code"], year, code, company.get("fs_div","CFS"))
                out_file = RAW / f"{year}_{label}_{company['corp_code']}.json"
                out_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
                if payload.get("status") == "000":
                    frames.append(normalize_report(payload, year, code, company.get("fs_div","CFS"), metric_cfg))
                    meta.append({"year":year,"category":label,"report_code":code,"status":"000"})
                else:
                    meta.append({"year":year,"category":label,"report_code":code,"status":payload.get("status"),"message":payload.get("message")})
            except Exception as exc:
                meta.append({"year":year,"category":label,"report_code":code,"status":"ERROR","message":str(exc)})
    df = pd.concat([x for x in frames if not x.empty], ignore_index=True) if frames else pd.DataFrame()
    if not df.empty:
        df.to_csv(DATA / "financial_metrics.csv", index=False, encoding="utf-8-sig")
        ratios = compute_ratios(df)
        ratios.to_csv(DATA / "financial_ratios.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(meta).to_csv(DATA / "collection_log.csv", index=False, encoding="utf-8-sig")
    (DATA / "last_updated.json").write_text(json.dumps({"updated_at":datetime.now(timezone.utc).isoformat(),"company":company["name"]}, ensure_ascii=False, indent=2), encoding="utf-8")
    return df

if __name__ == "__main__":
    run()
