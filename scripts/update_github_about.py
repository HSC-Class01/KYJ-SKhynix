import os, requests

OWNER = "HSC-Class01"
REPO = "KYJ-SKhynix"
PAGES = "https://hsc-class01.github.io/KYJ-SKhynix/"
token = os.getenv("GITHUB_TOKEN", "").strip()
if not token:
    raise SystemExit("GITHUB_TOKEN is required. Create a fine-grained token with repository administration/metadata permission, then run again.")
headers = {"Authorization": f"Bearer {token}", "Accept":"application/vnd.github+json", "X-GitHub-Api-Version":"2022-11-28"}
r = requests.patch(f"https://api.github.com/repos/{OWNER}/{REPO}", headers=headers, json={
    "description":"SK하이닉스 DART 재무데이터 자동 수집·분석 대시보드 | 김예준",
    "homepage": PAGES,
})
r.raise_for_status()
print("Updated repository About homepage and description.")
