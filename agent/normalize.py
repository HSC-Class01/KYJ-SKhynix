from __future__ import annotations
import re
import pandas as pd
import yaml
from pathlib import Path

NUM_RE = re.compile(r"[^0-9.-]")

def load_yaml(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def to_number(value):
    if value is None or str(value).strip() == "":
        return None
    s = str(value).strip().replace(",", "")
    if s in {"-", "–", "-0"}:
        return 0.0
    s = NUM_RE.sub("", s)
    try:
        return float(s)
    except ValueError:
        return None

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
        if not candidates:
            continue
        aliases = {clean_name(a) for a in cfg.get("aliases", [])}
        candidates.sort(key=lambda r: (
            0 if clean_name(r.get("account_nm", "")) in aliases else 1,
            0 if str(r.get("fs_nm", "")).startswith("연결") else 1,
            0 if str(r.get("sj_div", "")) == cfg.get("statement") else 1,
        ))
        r = candidates[0]
        out.append({
            "year": int(year),
            "report_code": report_code,
            "fs_div": fs_div,
            "metric": metric_key,
            "label": cfg.get("label", metric_key),
            "statement": cfg.get("statement", ""),
            "account_nm": r.get("account_nm"),
            "value": to_number(r.get("thstrm_amount")),
            "unit": "KRW",
            "period_nm": r.get("thstrm_nm"),
            "bsns_year": r.get("bsns_year"),
            "sj_div": r.get("sj_div"),
        })
    return pd.DataFrame(out)

def compute_ratios(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["year", "report_code"])
    piv = df.pivot_table(index=["year", "report_code"], columns="metric", values="value", aggfunc="first").reset_index()

    def div(num, den):
        if num not in piv.columns or den not in piv.columns:
            return pd.Series([float("nan")] * len(piv), index=piv.index)
        return piv[num] / piv[den].replace({0: pd.NA})

    piv["operating_margin"] = div("operating_income", "revenue") * 100
    piv["net_margin"] = div("net_income", "revenue") * 100
    piv["roe"] = div("net_income", "total_equity") * 100
    piv["roa"] = div("net_income", "total_assets") * 100
    piv["debt_ratio"] = div("total_liabilities", "total_equity") * 100
    piv["current_ratio"] = div("current_assets", "current_liabilities") * 100
    piv["asset_turnover"] = div("revenue", "total_assets")

    piv = piv.sort_values(["year", "report_code"]).reset_index(drop=True)
    annual = piv[piv["report_code"].astype(str).eq("11011")].copy()
    for key in ["revenue", "operating_income", "net_income"]:
        if key in annual.columns:
            annual[f"{key}_yoy"] = annual[key].pct_change() * 100
    yoy = annual.set_index("year")[[c for c in annual.columns if c.endswith("_yoy")]] if not annual.empty else pd.DataFrame()
    if not yoy.empty:
        piv = piv.merge(yoy.reset_index(), on="year", how="left")
    return piv
