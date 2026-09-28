from __future__ import annotations
import io
import json
import time
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

import requests

BASE = "https://opendart.fss.or.kr/api"

class DartError(RuntimeError):
    pass

class DartClient:
    def __init__(self, api_key: str, raw_dir: Path, sleep_seconds: float = 0.35):
        api_key = (api_key or "").strip()
        if not api_key:
            raise DartError("DART_API_KEY is missing.")
        self.api_key = api_key
        self.raw_dir = raw_dir
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.sleep_seconds = sleep_seconds
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "KYJ-SKhynix-DART-Agent/2.0"})

    def _request_json(self, endpoint: str, params: dict[str, Any], retries: int = 4) -> dict:
        q = dict(params)
        q["crtfc_key"] = self.api_key
        url = f"{BASE}/{endpoint}.json"
        last: Exception | None = None
        for attempt in range(retries):
            try:
                r = self.session.get(url, params=q, timeout=60)
                r.raise_for_status()
                data = r.json()
                status = str(data.get("status", ""))
                if status == "000" or status == "013":
                    return data
                raise DartError(f"DART {status}: {data.get('message', 'Unknown error')}")
            except Exception as exc:
                last = exc
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
        raise DartError(str(last))

    def get_json(self, endpoint: str, params: dict[str, Any]) -> dict:
        time.sleep(self.sleep_seconds)
        return self._request_json(endpoint, params)

    def corp_codes(self) -> list[dict]:
        time.sleep(self.sleep_seconds)
        r = self.session.get(f"{BASE}/corpCode.xml", params={"crtfc_key": self.api_key}, timeout=60)
        r.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(r.content)) as zf:
            xml = zf.read("CORPCODE.xml")
        root = ET.fromstring(xml)
        return [{
            "corp_code": (node.findtext("corp_code") or "").strip(),
            "corp_name": (node.findtext("corp_name") or "").strip(),
            "stock_code": (node.findtext("stock_code") or "").strip(),
            "modify_date": (node.findtext("modify_date") or "").strip(),
        } for node in root.findall("list")]

    def financials(self, corp_code: str, year: int, report_code: str, fs_div: str = "CFS") -> dict:
        return self.get_json("fnlttSinglAcntAll", {
            "corp_code": corp_code,
            "bsns_year": str(year),
            "reprt_code": report_code,
            "fs_div": fs_div,
        })

    def disclosure_list(self, corp_code: str, start_date: str, end_date: str,
                        detail_type: str | None = None, page_no: int = 1,
                        page_count: int = 100) -> dict:
        params = {
            "corp_code": corp_code,
            "bgn_de": start_date,
            "end_de": end_date,
            "pblntf_ty": "A",
            "sort": "date",
            "sort_mth": "asc",
            "page_no": page_no,
            "page_count": page_count,
            "last_reprt_at": "Y",
        }
        if detail_type:
            params["pblntf_detail_ty"] = detail_type
        return self.get_json("list", params)

    def all_disclosures(self, corp_code: str, start_date: str, end_date: str,
                        detail_type: str) -> list[dict]:
        first = self.disclosure_list(corp_code, start_date, end_date, detail_type, 1, 100)
        if first.get("status") == "013":
            return []
        items = list(first.get("list", []))
        total_page = int(first.get("total_page", 1) or 1)
        for page in range(2, total_page + 1):
            data = self.disclosure_list(corp_code, start_date, end_date, detail_type, page, 100)
            items.extend(data.get("list", []))
        return items

    def download_document(self, rcept_no: str, destination: Path) -> Path:
        """Download OpenDART's original filing archive for a receipt number."""
        time.sleep(self.sleep_seconds)
        r = self.session.get(
            f"{BASE}/document.xml",
            params={"crtfc_key": self.api_key, "rcept_no": rcept_no},
            timeout=120,
        )
        r.raise_for_status()
        content_type = (r.headers.get("content-type") or "").lower()
        if "zip" not in content_type and not r.content.startswith(b"PK"):
            try:
                data = r.json()
                raise DartError(f"DART {data.get('status')}: {data.get('message')}")
            except ValueError:
                raise DartError("DART document API returned a non-ZIP response.")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(r.content)
        return destination

    @staticmethod
    def viewer_url(rcept_no: str) -> str:
        return f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcept_no}"
