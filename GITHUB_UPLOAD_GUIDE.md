# GitHub 업로드 안내

이 프로젝트에는 GitHub Actions가 필요합니다. `.github/workflows/update-and-deploy.yml`은 GitHub에서 자동 실행되는 표준 위치라서 숨김 폴더처럼 보일 수 있습니다.

## 방법 A — GitHub 연결이 가능한 경우
GitHub 저장소에 프로젝트 파일을 업로드한 뒤 Actions workflow를 확인합니다.

## 방법 B — 웹 업로드에서 숨김 폴더가 보이지 않는 경우
1. 나머지 파일/폴더를 먼저 업로드합니다.
2. GitHub에서 **Add file → Create new file**을 선택합니다.
3. 파일 경로를 정확히 `/.github/workflows/update-and-deploy.yml`로 입력합니다.
4. `GITHUB_ACTIONS_WORKFLOW_COPY/update-and-deploy.yml`의 내용을 복사합니다.
5. Commit합니다.

`.github`은 자동화 실행에 필요한 폴더이며 `.git` 같은 Git 내부 파일은 패키지에 포함하지 않았습니다.
