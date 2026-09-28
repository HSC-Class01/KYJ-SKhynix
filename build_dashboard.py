from __future__ import annotations
import html, json
from pathlib import Path
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DATA = ROOT / "data"

def fmt(x):
    if pd.isna(x): return "-"
    x=float(x)
    return f"{x:,.0f}" if abs(x)>=100 else f"{x:,.2f}"

def ratio_fmt(x):
    if pd.isna(x): return "-"
    return f"{float(x):.2f}%"

def table(df, cols, percent_cols=()):
    if df.empty: return '<div class="empty">데이터가 없습니다.</div>'
    rows=[]
    for _,r in df.iterrows():
        cells=[]
        for c in cols:
            v=r.get(c)
            cells.append(ratio_fmt(v) if c in percent_cols else fmt(v))
        rows.append('<tr>'+''.join(f'<td>{html.escape(str(v))}</td>' for v in cells)+'</tr>')
    heads=''.join(f'<th>{html.escape(c)}</th>' for c in cols)
    return f'<div class="table-wrap"><table><thead><tr>{heads}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>'

def build():
    settings=yaml.safe_load((ROOT/'config/settings.yml').read_text(encoding='utf-8'))
    company=settings['company']; peers=settings['peers']
    f=DATA/'financial_metrics.csv'; r=DATA/'financial_ratios.csv'
    df=pd.read_csv(f) if f.exists() else pd.DataFrame()
    ratios=pd.read_csv(r) if r.exists() else pd.DataFrame()
    annual=df[df.report_code.astype(str).eq('11011')].pivot_table(index='year',columns='metric',values='value',aggfunc='first').reset_index() if not df.empty else pd.DataFrame()
    half=df[df.report_code.astype(str).eq('11012')].pivot_table(index='year',columns='metric',values='value',aggfunc='first').reset_index() if not df.empty else pd.DataFrame()
    q1=df[df.report_code.astype(str).eq('11013')].pivot_table(index='year',columns='metric',values='value',aggfunc='first').reset_index() if not df.empty else pd.DataFrame()
    q3=df[df.report_code.astype(str).eq('11014')].pivot_table(index='year',columns='metric',values='value',aggfunc='first').reset_index() if not df.empty else pd.DataFrame()
    # Derive standalone Q2/Q3/Q4 from cumulative income-statement values.
    qrows=[]
    for year in sorted(set(q1.get('year',pd.Series(dtype=int)).tolist()) | set(half.get('year',pd.Series(dtype=int)).tolist()) | set(q3.get('year',pd.Series(dtype=int)).tolist()) | set(annual.get('year',pd.Series(dtype=int)).tolist())):
        a=annual[annual.year==year].iloc[0] if not annual[annual.year.eq(year)].empty else None
        h=half[half.year==year].iloc[0] if not half[half.year.eq(year)].empty else None
        q_1=q1[q1.year==year].iloc[0] if not q1[q1.year.eq(year)].empty else None
        q_3=q3[q3.year==year].iloc[0] if not q3[q3.year.eq(year)].empty else None
        row={'year':year}
        for metric in ['revenue','operating_income','net_income']:
            v1=q_1.get(metric) if q_1 is not None else None
            vh=h.get(metric) if h is not None else None
            v9=q_3.get(metric) if q_3 is not None else None
            va=a.get(metric) if a is not None else None
            row[f'Q1_{metric}']=v1; row[f'Q2_{metric}']=vh-v1 if vh is not None and v1 is not None else None
            row[f'Q3_{metric}']=v9-vh if v9 is not None and vh is not None else None
            row[f'Q4_{metric}']=va-v9 if va is not None and v9 is not None else None
        qrows.append(row)
    q=pd.DataFrame(qrows)
    latest=annual.sort_values('year').tail(1).to_dict('records')[0] if not annual.empty else {}
    ratio_latest=ratios.sort_values(['year','report_code']).tail(1).to_dict('records')[0] if not ratios.empty else {}
    revenue_series=annual[['year','revenue']].dropna().tail(12).to_dict('records') if 'revenue' in annual else []
    op_series=annual[['year','operating_income']].dropna().tail(12).to_dict('records') if 'operating_income' in annual else []
    net_series=annual[['year','net_income']].dropna().tail(12).to_dict('records') if 'net_income' in annual else []
    payload=json.dumps({'revenue':revenue_series,'op':op_series,'net':net_series},ensure_ascii=False)
    annual_cols=[c for c in ['year','revenue','operating_income','net_income','total_assets','total_liabilities','total_equity','cash','inventory','operating_cash_flow'] if c in annual.columns]
    half_cols=[c for c in ['year','revenue','operating_income','net_income','total_assets','total_liabilities','total_equity'] if c in half.columns]
    q_cols=[c for c in ['year','Q1_revenue','Q2_revenue','Q3_revenue','Q4_revenue','Q1_operating_income','Q2_operating_income','Q3_operating_income','Q4_operating_income'] if c in q.columns]
    peers_html=''.join(f'<tr><td>{html.escape(p["name"])}</td><td>{html.escape(p["stock_code"])}</td><td>{html.escape(p["note"])}</td></tr>' for p in peers)
    last=latest.get('year','-')
    html_doc=f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(settings['dashboard']['title'])}</title><script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script><style>
:root{{--bg:#f3eee5;--card:#fbf8f2;--ink:#141414;--muted:#6d6a63;--line:#ddd6ca;--accent:#b7c99a}}*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font-family:Inter,system-ui,-apple-system,BlinkMacSystemFont,"Noto Sans KR",sans-serif}}header{{background:#111;color:#fff;padding:44px 6vw 52px;position:relative;overflow:hidden}}header:after{{content:"";position:absolute;width:520px;height:520px;border-radius:50%;right:-170px;bottom:-360px;background:#31452b;opacity:.9}}.eyebrow{{font-size:12px;letter-spacing:.2em;text-transform:uppercase;color:#c6c1b8}}h1{{font-size:clamp(34px,5vw,72px);margin:12px 0 8px;letter-spacing:-.04em}}header p{{color:#d4d0c8;max-width:760px;font-size:16px;line-height:1.7}}main{{width:min(1240px,92vw);margin:34px auto 80px}}.cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:28px}}.card{{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:22px}}.label{{color:var(--muted);font-size:12px}}.value{{font-size:28px;font-weight:750;margin-top:8px}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}section{{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:24px;margin-top:18px}}section h2{{font-size:22px;margin:0 0 4px}}section .desc{{color:var(--muted);font-size:13px;margin-bottom:16px}}#chart,#marginChart{{height:360px}}.table-wrap{{overflow:auto;border:1px solid var(--line);border-radius:14px}}table{{width:100%;border-collapse:collapse;font-size:13px;background:#fffdf9}}th,td{{padding:12px 14px;border-bottom:1px solid #eee8de;text-align:right;white-space:nowrap}}th:first-child,td:first-child{{text-align:left}}th{{background:#eee8dc;font-weight:700;position:sticky;top:0}}tr:last-child td{{border-bottom:0}}.peer td{{text-align:left}}a{{color:inherit}}.note{{font-size:12px;color:var(--muted);line-height:1.7}}@media(max-width:900px){{.cards,.grid{{grid-template-columns:1fr 1fr}}}}@media(max-width:600px){{.cards,.grid{{grid-template-columns:1fr}}header{{padding:32px 5vw}}}}
</style></head><body><header><div class="eyebrow">DART FINANCIAL INTELLIGENCE</div><h1>SK하이닉스 Financial Dashboard</h1><p>김예준의 OpenDART 기반 재무데이터 자동 수집·정규화·비율분석 프로젝트. 2010년부터 사업보고서·반기보고서·분기보고서를 누적하고 매월 1일 자동 갱신합니다.</p></header><main>
<div class="cards"><div class="card"><div class="label">최근 연간 매출액</div><div class="value">{fmt(latest.get('revenue'))}</div></div><div class="card"><div class="label">최근 연간 영업이익</div><div class="value">{fmt(latest.get('operating_income'))}</div></div><div class="card"><div class="label">영업이익률</div><div class="value">{ratio_fmt(ratio_latest.get('operating_margin'))}</div></div><div class="card"><div class="label">부채비율</div><div class="value">{ratio_fmt(ratio_latest.get('debt_ratio'))}</div></div></div>
<div class="grid"><section><h2>Annual Trend</h2><div class="desc">연간 매출·영업이익·순이익 추이 · 단위: 조원</div><div id="chart"></div></section><section><h2>Profitability</h2><div class="desc">영업이익률 / 순이익률</div><div id="marginChart"></div></section></div>
<section><h2>Annual</h2><div class="desc">사업보고서 기준 주요 재무수치</div>{table(annual.sort_values('year',ascending=False),annual_cols)}</section>
<section><h2>Half-year</h2><div class="desc">반기보고서 기준 주요 재무수치</div>{table(half.sort_values('year',ascending=False),half_cols)}</section>
<section><h2>Quarterly</h2><div class="desc">분기 누적수치를 이용해 Q1/Q2/Q3/Q4 standalone으로 환산한 손익계산서 핵심 수치</div>{table(q.sort_values('year',ascending=False),q_cols)}</section>
<section><h2>Peer Firms</h2><div class="desc">국내 반도체 산업에서 비교 맥락을 볼 수 있도록 설정한 기업 목록입니다. 사업영역은 서로 완전히 동일하지 않을 수 있습니다.</div><div class="table-wrap"><table class="peer"><thead><tr><th>기업</th><th>종목코드</th><th>비교 맥락</th></tr></thead><tbody>{peers_html}</tbody></table></div></section>
<p class="note">Data source: Financial Supervisory Service OpenDART. Unit is the unit returned by the DART financial statement API; dashboard calculations use consolidated statements (CFS). Missing values are shown as “-”. Last configured fiscal year: {last}. <a href="https://opendart.fss.or.kr/">OpenDART</a> · <a href="https://github.com/HSC-Class01/KYJ-SKhynix">GitHub repository</a></p></main>
<script>const d={payload};const years=d.revenue.map(x=>x.year);const series=(arr)=>arr.map(x=>x.revenue/1e12);Plotly.newPlot('chart',[{{x:years,y:d.revenue.map(x=>x.revenue/1e6),name:'매출액',type:'scatter',mode:'lines+markers'}},{{x:d.op.map(x=>x.year),y:d.op.map(x=>x.operating_income/1e6),name:'영업이익',type:'scatter',mode:'lines+markers'}},{{x:d.net.map(x=>x.year),y:d.net.map(x=>x.net_income/1e6),name:'순이익',type:'scatter',mode:'lines+markers'}}],{{margin:{{l:48,r:20,t:10,b:42}},paper_bgcolor:'transparent',plot_bgcolor:'transparent',yaxis:{{title:'조원'}},xaxis:{{dtick:2}},legend:{{orientation:'h'}}}});const rr={json.dumps(ratios.sort_values(['year','report_code']).tail(20)[['year','operating_margin','net_margin']].to_dict('records'),ensure_ascii=False)};Plotly.newPlot('marginChart',[{{x:rr.map(x=>x.year),y:rr.map(x=>x.operating_margin),name:'영업이익률',type:'scatter',mode:'lines+markers'}},{{x:rr.map(x=>x.year),y:rr.map(x=>x.net_margin),name:'순이익률',type:'scatter',mode:'lines+markers'}}],{{margin:{{l:48,r:20,t:10,b:42}},paper_bgcolor:'transparent',plot_bgcolor:'transparent',yaxis:{{title:'%'}},xaxis:{{dtick:2}},legend:{{orientation:'h'}}}});</script></body></html>'''
    DOCS.mkdir(exist_ok=True)
    (DOCS/'index.html').write_text(html_doc,encoding='utf-8')

if __name__=='__main__': build()
