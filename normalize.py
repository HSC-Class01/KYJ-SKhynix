from __future__ import annotations
import re
from pathlib import Path
import pandas as pd
import yaml

NUM_RE = re.compile(r"[^0-9.-]")

def load_yaml(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def to_number(value):
    if value is None or value == "": return None
    s = str(value).strip().replace(",", "")
    if s in {"-", "–", "-0"}: return 0.0
    s = NUM_RE.sub("", s)
    try: return float(s)
    except ValueError: return None

def clean_name(name: str) -> str:
    return re.sub(r"\s+", "", str(name)).replace("(손실)", "(손실)")

def match_metric(account_name: str, aliases: list[str]) -> bool:
    a = clean_name(account_name)
    return any(clean_name(alias) == a or clean_name(alias) in a for alias in aliases)

def normalize_report(payload: dict, year: int, report_code: str, fs_div: str, metrics_cfg: dict) -> pd.DataFrame:
    rows = payload.get("list", [])
    out = []
    for metric_key, cfg in metrics_cfg.items():
        candidates = [r for r in rows if match_metric(r.get("account_nm", ""), cfg.get("aliases", []))]
        if not candidates: continue
        # Prefer exact-ish account name, then consolidated/parent rows.
        candidates.sort(key=lambda r: (0 if clean_name(r.get("account_nm", "")) in [clean_name(a) for a in cfg.get("aliases", [])] else 1,
                                       0 if r.get("fs_nm", "").startswith("연결") else 1))
        r = candidates[0]
        out.append({
            "year": int(year), "report_code": report_code, "fs_div": fs_div,
            "metric": metric_key, "label": cfg.get("label", metric_key),
            "statement": cfg.get("statement", ""),
            "account_nm": r.get("account_nm"),
            "value": to_number(r.get("thstrm_amount")),
            "unit": r.get("currency") or "KRW",
            "period_nm": r.get("thstrm_nm"),
            "bsns_year": r.get("bsns_year"),
            "sj_div": r.get("sj_div"),
        })
    return pd.DataFrame(out)

def compute_ratios(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty: return df
    piv = df.pivot_table(index=["year","report_code"], columns="metric", values="value", aggfunc="first").reset_index()
    def ratio(num, den):
        if num not in piv or den not in piv: return pd.Series([None]*len(piv))
        return piv[num] / piv[den].replace({0: pd.NA})
    piv["operating_margin"] = ratio("operating_income", "revenue") * 100
    piv["net_margin"] = ratio("net_income", "revenue") * 100
    piv["roe"] = ratio("net_income", "total_equity") * 100
    piv["roa"] = ratio("net_income", "total_assets") * 100
    piv["debt_ratio"] = ratio("total_liabilities", "total_equity") * 100
    piv["current_ratio"] = ratio("current_assets", "current_liabilities") * 100
    piv["asset_turnover"] = ratio("revenue", "total_assets")
    piv = piv.sort_values(["year","report_code"]).reset_index(drop=True)
    for key in ["revenue", "operating_income", "net_income"]:
        if key in piv:
            piv[f"{key}_yoy"] = piv[key].pct_change() * 100
    return piv
