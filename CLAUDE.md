# CLAUDE.md

이 저장소의 작업 지침은 [`AGENTS.md`](AGENTS.md)에 있다. **작업 시작 전에 읽는다.**

특히 자주 놓치는 두 가지:

- **개인 환경 의존에는 반드시 폴백을 둔다** — 로컬 MCP·사내망·절대경로에 기대는 기능은
  그것이 없는 사용자를 위한 대체 경로를 함께 만든다. 없으면 추정으로 메우지 말고 빈칸 + TODO로 남긴다. (AGENTS.md 2장)
- **버전은 사용자 경험 기준으로 올린다** — 하던 대로 해도 결과가 같으면 patch다.
  단순 튜닝·문구 수정·임계값 미세조정은 분량과 무관하게 patch.
  올릴 때는 plugin.json · marketplace.json · README 표 **세 곳을 함께** 올린다. (AGENTS.md 3장)

설계 근거는 `docs/design-decisions.md`, 미결 사항은 `docs/open-issues.md`에 있다.
