# SK하이닉스 DART Financial Dashboard — 김예준

[![Dashboard](assets/dashboard-badge.svg)](https://hsc-class01.github.io/KYJ-SKhynix/)

## 🔗 대시보드 바로가기

[![대시보드 바로가기](assets/dashboard-badge.svg)](https://hsc-class01.github.io/KYJ-SKhynix/)

OpenDART의 정기보고서 재무정보를 이용해 SK하이닉스의 **2010년 이후 사업보고서·반기보고서·분기보고서**를 수집하고, 주요 재무수치와 재무비율을 자동 계산하여 GitHub Pages 대시보드로 공개하는 프로젝트입니다.

> 데이터 기준: 금융감독원 OpenDART. 연결재무제표(CFS)를 기본으로 사용합니다.

## 자동화

- 매월 1일 01:00 UTC에 GitHub Actions 실행
- `DART_API_KEY` GitHub Secret으로 OpenDART 호출
- 새/변경 재무데이터를 `data/`에 저장
- 재무비율 재계산
- `docs/index.html` 대시보드 재생성
- GitHub Pages 자동 배포
- 수동 실행: Actions → **Update DART data and deploy dashboard** → Run workflow

OpenDART 보고서 코드: 사업보고서 `11011`, 반기보고서 `11012`, 1분기보고서 `11013`, 3분기보고서 `11014`.

## 주요 분석 항목

매출액, 매출원가, 매출총이익, 영업이익, 당기순이익, 자산총계, 유동자산, 현금및현금성자산, 재고자산, 부채총계, 유동부채, 자본총계, 유형자산, 영업활동현금흐름을 수집합니다.

재무비율: 영업이익률, 순이익률, ROE, ROA, 부채비율, 유동비율, 총자산회전율.

분기 표는 DART의 누적 분기 데이터에서 Q2/Q3/Q4 standalone 값을 계산합니다.

## 설치 및 API 키 입력

1. OpenDART에서 API 인증키를 발급합니다: https://opendart.fss.or.kr/
2. GitHub 저장소 **Settings → Secrets and variables → Actions → New repository secret**에서 아래를 등록합니다.

```text
Name: DART_API_KEY
Value: 발급받은 40자리 OpenDART API 키
```

3. Actions에서 workflow를 수동 실행해 첫 수집을 확인합니다.

로컬 실행이 필요하다면 `.env.example`을 `.env`로 복사하고 `DART_API_KEY`를 입력한 뒤:

```bash
python -m pip install -r requirements.txt
python scripts/update_data.py
python scripts/build_dashboard.py
```

**API 키는 코드, README, commit에 직접 입력하지 마세요.**

## GitHub Pages

이 저장소는 `docs/`를 GitHub Pages에 배포하도록 설계되어 있습니다. Repository → Settings → Pages에서 **GitHub Actions**를 배포 소스로 선택하세요. 첫 workflow 실행 후 대시보드가 생성됩니다.

예정 주소:

`https://hsc-class01.github.io/KYJ-SKhynix/`

## Repository About 링크

저장소 오른쪽 **About → Website**에 위 Pages 주소를 등록하면 됩니다. API로 자동 등록하려면 로컬에서 `scripts/update_github_about.py`를 실행하세요. 이 스크립트에는 토큰을 하드코딩하지 않습니다.

## 국내 Peer Firms

| 기업 | 종목코드 | 비교 맥락 |
|---|---:|---|
| 삼성전자 | 005930 | 메모리/반도체 종합 기업 |
| DB하이텍 | 000990 | 국내 반도체 제조 기업 |
| 한미반도체 | 042700 | 반도체 후공정 장비 기업 |
| LX세미콘 | 108320 | 반도체 설계 기업 |

비교기업은 사업영역이 완전히 동일하다는 의미가 아니라, 국내 반도체 산업 맥락에서 참고할 수 있도록 구성했습니다.

## 폴더 구조

```text
.
├── .github/workflows/update-and-deploy.yml
├── agent/
│   ├── dart_client.py
│   ├── normalize.py
│   └── pipeline.py
├── config/
│   ├── metrics.yml
│   └── settings.yml
├── data/
│   └── raw/
├── docs/
│   └── index.html
├── scripts/
│   ├── build_dashboard.py
│   ├── update_data.py
│   └── update_github_about.py
├── assets/dashboard-badge.svg
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```
