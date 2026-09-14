---
description: vault 경로와 폴더 체계를 설정한다 (최초 1회)
argument-hint: [vault 경로, 생략 가능]
---

knowledge-notes 초기 설정. 입력: $ARGUMENTS

1. `~/.knowledge-notes/config.json`이 이미 있으면 현재 설정을 보여주고, 바꿀지 묻는다.
2. 없으면 만든다.
   - **vault 경로**를 묻는다. 인자로 받았으면 그 값을 쓴다.
   - 경로가 실제로 존재하는지 확인한다. 없으면 만들지 여부를 묻는다.
   - 폴더 체계는 기본값을 제시하고, 다른 번호 체계를 쓰고 있으면 그에 맞춘다.
3. 설정 파일을 쓴다.

```json
{
  "vault_path": "",
  "folders": {
    "inbox": "000_inbox",
    "term": "100_terms",
    "concept": "200_concepts",
    "insight": "300_insights",
    "source": "400_sources",
    "moc": "900_maps"
  },
  "language": "ko",
  "personal_tags": []
}
```

4. 폴더가 없으면 만든다.
5. 시드 노트 설치 여부를 묻는다.
   - 설치하면 `${CLAUDE_PLUGIN_ROOT}/seeds/`의 노트를 타입별 폴더로 복사한다.
   - **이미 같은 이름의 노트가 있으면 덮어쓰지 않는다.** 건너뛰고 목록으로 보고한다.

폴더는 타입으로만 나눈다. 주제별 폴더(영업/데이터/S&OP)를 만들자는 요청이 오면
한 노트가 두 곳에 속하는 문제가 생긴다고 설명하고 `domain` 필드를 쓰도록 안내한다.
