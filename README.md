# 2010–2014 historical backfill

OpenDART's structured financial-statement APIs document coverage from 2015 onward. Therefore the automated OpenDART financial pipeline in this repository starts structured extraction at 2015 even though the project timeline is configured from 2010.

If 2010–2014 values are required, place a CSV named `legacy_financial_metrics.csv` in this folder using these columns:

`year,report_code,metric,value`

Allowed report codes:
- `11011` annual
- `11012` half-year
- `11013` Q1
- `11014` Q3

Values should be raw KRW amounts. The dashboard can then be extended to merge this file before building.
