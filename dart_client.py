from __future__ import annotations
import io, time, zipfile, xml.etree.ElementTree as ET
from pathlib import Path
import requests

BASE = "https://opendart.fss.or.kr/api"

class DartError(RuntimeError):
    pass

class DartClient:
    def __init__(self, api_key: str, raw_dir: Path, sleep_seconds: float = 0.35):
        if not api_key:
            raise DartError("DART_API_KEY is missing.")
        self.api_key = api_key
        self.raw_dir = raw_dir
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.sleep_seconds = sleep_seconds
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "KYJ-SKhynix-DART-Agent/1.0"})

    def get_json(self, endpoint: str, params: dict, retries: int = 3) -> dict:
        q = dict(params)
        q["crtfc_key"] = self.api_key
        url = f"{BASE}/{endpoint}.json"
        last = None
        for attempt in range(retries):
            try:
                r = self.session.get(url, params=q, timeout=45)
                r.raise_for_status()
                data = r.json()
                if data.get("status") != "000":
                    # 013 means no data; the caller can treat it as an empty report.
                    if data.get("status") == "013":
                        return data
                    raise DartError(f"DART {data.get('status')}: {data.get('message')}")
                return data
            except Exception as exc:
                last = exc
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
        raise DartError(str(last))

    def corp_codes(self) -> list[dict]:
        url = f"{BASE}/corpCode.xml"
        r = self.session.get(url, params={"crtfc_key": self.api_key}, timeout=60)
        r.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(r.content)) as zf:
            xml = zf.read("CORPCODE.xml")
        root = ET.fromstring(xml)
        out = []
        for node in root.findall("list"):
            out.append({
                "corp_code": (node.findtext("corp_code") or "").strip(),
                "corp_name": (node.findtext("corp_name") or "").strip(),
                "stock_code": (node.findtext("stock_code") or "").strip(),
                "modify_date": (node.findtext("modify_date") or "").strip(),
            })
        return out

    def financials(self, corp_code: str, year: int, report_code: str, fs_div: str = "CFS") -> dict:
        time.sleep(self.sleep_seconds)
        return self.get_json("fnlttSinglAcntAll", {
            "corp_code": corp_code,
            "bsns_year": str(year),
            "reprt_code": report_code,
            "fs_div": fs_div,
        })

    def filings(self, corp_code: str, start_date: str, end_date: str) -> dict:
        time.sleep(self.sleep_seconds)
        return self.get_json("list", {
            "corp_code": corp_code,
            "bgn_de": start_date,
            "end_de": end_date,
            "page_no": 1,
            "page_count": 100,
        })
