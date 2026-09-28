from __future__ import annotations
import html, json
from pathlib import Path
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DATA = ROOT / "data"

LABELS = {
    "year": "연도", "revenue": "매출액", "operating_income": "영업이익", "net_income": "순이익",
    "total_assets": "자산총계", "total_liabilities": "부채총계", "total_equity": "자본총계",
    "cash": "현금및현금성자산", "inventory": "재고자산", "operating_cash_flow": "영업활동현금흐름",
    "Q1_revenue":"Q1 매출", "Q2_revenue":"Q2 매출", "Q3_revenue":"Q3 매출", "Q4_revenue":"Q4 매출",
    "Q1_operating_income":"Q1 영업이익", "Q2_operating_income":"Q2 영업이익", "Q3_operating_income":"Q3 영업이익", "Q4_operating_income":"Q4 영업이익",
}

def money(x):
    if pd.isna(x): return "-"
    return f"{float(x)/1e12:,.2f}조"

def pct(x):
    if pd.isna(x): return "-"
    return f"{float(x):,.2f}%"

def table(df, cols):
    if df.empty:
        return '<div class="empty">아직 수집된 데이터가 없습니다. GitHub Actions에서 <b>Update DART data and deploy dashboard</b>를 실행하세요.</div>'
    rows=[]
    for _, row in df.iterrows():
        cells=[]
        for c in cols:
            v=row.get(c)
            cells.append(str(int(v)) if c == "year" and pd.notna(v) else money(v))
        rows.append("<tr>" + "".join(f"<td>{html.escape(v)}</td>" for v in cells) + "</tr>")
    heads="".join(f"<th>{html.escape(LABELS.get(c,c))}</th>" for c in cols)
    return f'<div class="table-wrap"><table><thead><tr>{heads}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>'

def build():
    settings=yaml.safe_load((ROOT/"config/settings.yml").read_text(encoding="utf-8"))
    company=settings["company"]; peers=settings["peers"]
    metrics_file=DATA/"financial_metrics.csv"; ratios_file=DATA/"financial_ratios.csv"
    df=pd.read_csv(metrics_file) if metrics_file.exists() else pd.DataFrame()
    ratios=pd.read_csv(ratios_file) if ratios_file.exists() else pd.DataFrame()
    if not df.empty:
        df["report_code"]=df["report_code"].astype(str)
        annual=df[df.report_code.eq("11011")].pivot_table(index="year",columns="metric",values="value",aggfunc="first").reset_index()
        half=df[df.report_code.eq("11012")].pivot_table(index="year",columns="metric",values="value",aggfunc="first").reset_index()
        q1=df[df.report_code.eq("11013")].pivot_table(index="year",columns="metric",values="value",aggfunc="first").reset_index()
        q3=df[df.report_code.eq("11014")].pivot_table(index="year",columns="metric",values="value",aggfunc="first").reset_index()
    else:
        annual=half=q1=q3=pd.DataFrame()

    qrows=[]
    years=sorted(set(annual.get("year",pd.Series(dtype=int))) | set(half.get("year",pd.Series(dtype=int))) | set(q1.get("year",pd.Series(dtype=int))) | set(q3.get("year",pd.Series(dtype=int))))
    for year in years:
        get=lambda x: x[x.year.eq(year)].iloc[0] if not x.empty and not x[x.year.eq(year)].empty else None
        a,h,one,nine=get(annual),get(half),get(q1),get(q3)
        row={"year":year}
        for metric in ["revenue","operating_income","net_income"]:
            v1=one.get(metric) if one is not None and metric in one else None
            vh=h.get(metric) if h is not None and metric in h else None
            v9=nine.get(metric) if nine is not None and metric in nine else None
            va=a.get(metric) if a is not None and metric in a else None
            row[f"Q1_{metric}"]=v1
            row[f"Q2_{metric}"]=vh-v1 if pd.notna(vh) and pd.notna(v1) else None
            row[f"Q3_{metric}"]=v9-vh if pd.notna(v9) and pd.notna(vh) else None
            row[f"Q4_{metric}"]=va-v9 if pd.notna(va) and pd.notna(v9) else None
        qrows.append(row)
    q=pd.DataFrame(qrows)

    latest=annual.sort_values("year").tail(1).to_dict("records")[0] if not annual.empty else {}
    if not ratios.empty and "report_code" in ratios:
        ratios["report_code"]=ratios["report_code"].astype(str)
    annual_ratio=ratios[ratios.report_code.eq("11011")].sort_values("year") if not ratios.empty and "report_code" in ratios else pd.DataFrame()
    rlatest=annual_ratio.tail(1).to_dict("records")[0] if not annual_ratio.empty else {}

    chart_records=annual[[c for c in ["year","revenue","operating_income","net_income"] if c in annual.columns]].sort_values("year").tail(15).to_dict("records") if not annual.empty else []
    margin_records=annual_ratio[[c for c in ["year","operating_margin","net_margin","debt_ratio"] if c in annual_ratio.columns]].tail(15).to_dict("records") if not annual_ratio.empty else []
    payload=json.dumps({"annual":chart_records,"ratios":margin_records},ensure_ascii=False)

    annual_cols=[c for c in ["year","revenue","operating_income","net_income","total_assets","total_liabilities","total_equity","cash","inventory","operating_cash_flow"] if c in annual.columns]
    half_cols=[c for c in ["year","revenue","operating_income","net_income","total_assets","total_liabilities","total_equity"] if c in half.columns]
    q_cols=[c for c in ["year","Q1_revenue","Q2_revenue","Q3_revenue","Q4_revenue","Q1_operating_income","Q2_operating_income","Q3_operating_income","Q4_operating_income"] if c in q.columns]
    peers_html="".join(f'<tr><td>{html.escape(p["name"])}</td><td>{html.escape(p["stock_code"])}</td><td>{html.escape(p["note"])}</td></tr>' for p in peers)
    latest_year=latest.get("year","-")
    updated="-"
    lu=DATA/"last_updated.json"
    if lu.exists():
        try: updated=json.loads(lu.read_text(encoding="utf-8")).get("updated_at","-")[:10]
        except Exception: pass

    html_doc=f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SK하이닉스 | 김예준 DART Dashboard</title><script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script><style>
:root{{--bg:#f1ede5;--paper:#fbf9f4;--ink:#171717;--muted:#77736b;--line:#ded8cd;--dark:#111;--green:#a8bf86;--green2:#dce8cb}}*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font-family:Inter,"Noto Sans KR",system-ui,sans-serif}}header{{background:var(--dark);color:#fff;padding:54px max(5vw,28px) 60px;position:relative;overflow:hidden}}header:before,header:after{{content:"";position:absolute;border-radius:50%;background:#52683e;opacity:.48}}header:before{{width:480px;height:480px;right:-130px;bottom:-350px}}header:after{{width:330px;height:330px;right:220px;bottom:-270px}}.top{{position:relative;z-index:1;max-width:1200px;margin:auto}}.eyebrow{{letter-spacing:.22em;font-size:11px;color:#bdb9b0}}h1{{font-size:clamp(38px,6vw,76px);letter-spacing:-.055em;margin:14px 0 8px}}.subtitle{{font-size:16px;line-height:1.8;color:#d9d5cd;max-width:760px}}.meta{{display:flex;gap:18px;flex-wrap:wrap;margin-top:22px;font-size:12px;color:#c6c1b8}}main{{width:min(1240px,92vw);margin:30px auto 80px}}.hero-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:-24px;position:relative;z-index:2}}.kpi{{background:rgba(251,249,244,.97);border:1px solid var(--line);border-radius:18px;padding:20px;box-shadow:0 8px 25px rgba(0,0,0,.05)}}.kpi .label{{font-size:12px;color:var(--muted)}}.kpi .num{{font-size:25px;font-weight:800;margin-top:8px}}.section{{background:var(--paper);border:1px solid var(--line);border-radius:20px;padding:24px;margin-top:18px}}.section h2{{margin:0;font-size:22px;letter-spacing:-.03em}}.section .desc{{color:var(--muted);font-size:13px;margin:7px 0 18px;line-height:1.7}}.charts{{display:grid;grid-template-columns:1.4fr 1fr;gap:18px}}.chartbox{{background:#fffdf9;border:1px solid var(--line);border-radius:16px;padding:10px}}#trend,#margin{{height:340px}}.table-wrap{{overflow:auto;border:1px solid var(--line);border-radius:14px;background:#fffdf9}}table{{width:100%;border-collapse:collapse;font-size:13px}}th,td{{padding:12px 14px;border-bottom:1px solid #eee9df;white-space:nowrap;text-align:right}}th:first-child,td:first-child{{text-align:left}}th{{background:#eee9de;position:sticky;top:0;font-weight:750}}tr:last-child td{{border-bottom:0}}.peers td{{text-align:left}}.empty{{padding:28px;color:var(--muted);background:#fffdf9;border:1px dashed var(--line);border-radius:14px;line-height:1.7}}.foot{{font-size:12px;color:var(--muted);line-height:1.8;margin-top:22px}}a{{color:inherit}}@media(max-width:900px){{.hero-grid,.charts{{grid-template-columns:1fr 1fr}}}}@media(max-width:620px){{.hero-grid,.charts{{grid-template-columns:1fr}}header{{padding-top:36px}}}}
</style></head><body><header><div class="top"><div class="eyebrow">KIM YEJUN · OPEN DART FINANCIAL INTELLIGENCE</div><h1>SK hynix<br>Financial Dashboard</h1><div class="subtitle">김예준의 SK하이닉스 기업분석 프로젝트입니다. OpenDART의 연결재무제표를 기반으로 사업보고서·반기보고서·분기보고서의 주요 수치를 수집하고 재무비율을 계산합니다.</div><div class="meta"><span>2015+ OpenDART structured data</span><span>매월 1일 자동 업데이트</span><span>Consolidated · CFS</span></div></div></header><main>
<div class="hero-grid"><div class="kpi"><div class="label">최근 연간 매출액</div><div class="num">{money(latest.get('revenue'))}</div></div><div class="kpi"><div class="label">최근 연간 영업이익</div><div class="num">{money(latest.get('operating_income'))}</div></div><div class="kpi"><div class="label">영업이익률</div><div class="num">{pct(rlatest.get('operating_margin'))}</div></div><div class="kpi"><div class="label">부채비율</div><div class="num">{pct(rlatest.get('debt_ratio'))}</div></div></div>
<div class="section"><h2>Figures</h2><div class="desc">최근 연간 추세를 한눈에 확인할 수 있도록 매출·영업이익·순이익과 수익성 지표를 시각화했습니다.</div><div class="charts"><div class="chartbox"><div id="trend"></div></div><div class="chartbox"><div id="margin"></div></div></div></div>
<div class="section"><h2>Annual</h2><div class="desc">사업보고서 기준. 금액 단위는 조원입니다.</div>{table(annual.sort_values('year',ascending=False) if 'year' in annual.columns else annual,annual_cols)}</div>
<div class="section"><h2>Half-year</h2><div class="desc">반기보고서 기준. 금액 단위는 조원입니다.</div>{table(half.sort_values('year',ascending=False) if 'year' in half.columns else half,half_cols)}</div>
<div class="section"><h2>Quarterly</h2><div class="desc">Q1/Q2/Q3/Q4는 DART의 누적 수치를 차감해 standalone 기준으로 계산합니다. 금액 단위는 조원입니다.</div>{table(q.sort_values('year',ascending=False) if 'year' in q.columns else q,q_cols)}</div>
<div class="section"><h2>Peer Firms</h2><div class="desc">국내 반도체 산업에서 비교 맥락을 확인하기 위한 참고 기업입니다. 동일 사업모델이라는 의미는 아닙니다.</div><div class="table-wrap"><table class="peers"><thead><tr><th>기업</th><th>종목코드</th><th>비교 맥락</th></tr></thead><tbody>{peers_html}</tbody></table></div></div>
<div class="foot">요청 시작연도: {company.get('start_year',2010)} · OpenDART 구조화 재무 API 자동수집 시작연도: 2015 · 최근 데이터: {latest_year} · 마지막 업데이트: {updated}<br>OpenDART 원문은 접수번호 기준으로 GitHub의 <code>data/reports/</code>에 저장하도록 구성되어 있습니다. 2010~2014 데이터는 OpenDART 구조화 재무 API의 공식 제공 범위 밖이므로 별도 historical backfill이 필요합니다. <a href="https://opendart.fss.or.kr/" target="_blank">OpenDART</a> · <a href="https://github.com/HSC-Class01/KYJ-SKhynix" target="_blank">GitHub Repository</a></div>
</main><script>const payload={payload};const a=payload.annual;const rr=payload.ratios;Plotly.newPlot('trend',[{{x:a.map(d=>d.year),y:a.map(d=>d.revenue/1e12),name:'매출액',mode:'lines+markers'}},{{x:a.map(d=>d.year),y:a.map(d=>d.operating_income/1e12),name:'영업이익',mode:'lines+markers'}},{{x:a.map(d=>d.year),y:a.map(d=>d.net_income/1e12),name:'순이익',mode:'lines+markers'}}],{{margin:{{l:45,r:15,t:12,b:40}},paper_bgcolor:'transparent',plot_bgcolor:'transparent',yaxis:{{title:'조원'}},xaxis:{{title:'연도'}},legend:{{orientation:'h'}}}},{{responsive:true,displayModeBar:false}});Plotly.newPlot('margin',[{{x:rr.map(d=>d.year),y:rr.map(d=>d.operating_margin),name:'영업이익률',mode:'lines+markers'}},{{x:rr.map(d=>d.year),y:rr.map(d=>d.net_margin),name:'순이익률',mode:'lines+markers'}}],{{margin:{{l:45,r:15,t:12,b:40}},paper_bgcolor:'transparent',plot_bgcolor:'transparent',yaxis:{{title:'%'}},xaxis:{{title:'연도'}},legend:{{orientation:'h'}}}},{{responsive:true,displayModeBar:false}});</script></body></html>'''
    DOCS.mkdir(exist_ok=True)
    (DOCS/"index.html").write_text(html_doc,encoding="utf-8")

if __name__ == "__main__": build()
