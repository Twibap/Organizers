# Heat 오거나이저 — 현재 V0.5

자동차·기어 8쌍을 4열×2행으로 배치하고 기어를 눕혀, 점수판 트레이까지 포함한 외곽을 **110.8×64.8×30.2 mm**로 줄였습니다. 이전 V0.4 자동차 모듈 93.6×190.8×38 mm와 비교해 외곽 부피가 약 68% 감소했습니다. 전역 최소 부피를 증명한 설계는 아니며, 8쌍을 각자 꺼낼 수 있는 간결한 배치입니다.

점수판 **전체 묶음**은 사용자 실측 100×60×7 mm입니다. 최대 10 mm 수납을 기준으로 하부 트레이를 설계했습니다. 상부 자동차·기어 트레이를 들어 올리면 점수판에 접근합니다. 자동차 트레이, 점수판 트레이, 덮개를 분리 출력합니다.

최신 폴더는 `output/latest-heat-draft.txt`에 있습니다.

- **CarGearTray-Compact.FCStd**: 자동차 모듈 조립본. 실제 조립 외곽 110.8×64.8×30.2 mm. 덮개는 처음 열 때 숨겨집니다.
- **CarGearTray-Compact-Exploded.FCStd**: 점수판 수납을 보여 주는 분해 보기. 상부를 표시용으로 20 mm 띄웠으므로 이 파일의 표시 높이는 조립 높이가 아닙니다.
- **HeatOrganizerReview.FCStd**: 전체 배치와 매개변수 편집 원본. `CompactParameters`에서 자동차 모듈 치수를, `Parameters`에서 전체 배치 치수를 확인합니다.
- **HeatOrganizerDraft.FCStd**: GUI 화면 정보를 포함한 전체 작업본 복사본. Review와 같은 내용입니다.
- `Draft-notes.md`: 수량, 치수, 조립 및 출력 안내, 검증 결과.
- `HeatOrganizerDraft-preview.png`: 한글 전체 배치 미리보기.
- `stl/`: 출력 파일 16종, 수량 합계 30개. 차량·기어·점수판 참고 모형은 출력 제외입니다.

조립본과 분해 보기 FCStd는 모듈 확인을 위한 형상 복사본입니다. 매개변수 변경은 전체 작업본에서 합니다. FCStd 파일은 매크로 없이 직접 열 수 있으며, 저장 후 직접 재열기를 확인했습니다.

## 설계 소스와 입력

- `HeatOrganizerCompactDraft.FCMacro`: V0.5 전체 생성 소스.
- `tools/compact_car_tray.py`: 자동차·기어·점수판 모듈 생성 소스.
- `heat-measurements.json`: 실측값과 가정 구분.
- `heat-component-allocation.json`: Heavy Rain + Tunnel Vision 기준 최대 8인 구성 분류.
- `Heat-design-constraints.md`: 박스 내부 치수 출처와 평판 적층 조건.

박스 내부는 290×290×100 mm를 기준으로 합니다. 높이 100 mm는 사용자 실측이며, 가로·세로는 검색값입니다. 전체 트레이 배치 외곽은 288×288×38 mm, 상단 맵·개인판·공용 판·설명서 예약은 60 mm, 높이 여유는 2 mm입니다. 점수판은 자동차 모듈 하부로 옮겨 상단 적층에서 제외했습니다. 확장 개인판·설명서 두께는 아직 미측정이므로 실제 전체 상단 적층이 60 mm 이하여야 합니다.

기어는 밑판 Ø15 mm, 높이 25 mm를 기준으로 전체가 Ø15×25 mm 원통 안에 들어간다고 가정했습니다. 화면의 원통과 차량 직육면체는 수납 범위 검사 모형입니다. 기어 상부 최대 폭과 실제 출력 끼움은 아직 검증하지 않았습니다.

## 재생성

```powershell
$env:ORGANIZER_PROJECT_ROOT=(Get-Location).Path
& 'C:\Program Files\FreeCAD 1.1\bin\FreeCADCmd.exe' tools\headless_compact_draft.py
```

GUI 저장은 FreeCAD에서 `MakeHeatCompactReview.FCMacro`를 실행합니다. 이 단계가 직접 열리는 FCStd의 화면 정보를 저장합니다. `VerifyHeatCompactReview.FCMacro`는 저장한 전체·조립·분해 파일을 다시 열어 확인합니다. 미리보기는 번들 Python으로 `tools/render_heat_v05.py 출력폴더`를 실행합니다.

재생성 직후 `HeatOrganizerDraft.FCStd`는 headless 생성 파일입니다. GUI 저장을 완료한 `HeatOrganizerReview.FCStd`를 사용하세요. 현재 배포 폴더의 Draft는 Review 복사본이며, headless 원본은 `HeatOrganizerDraft-headless.FCStd`로 보존했습니다.

이전 V0.4 및 V0.3 폴더는 이전 설계 참고용으로 남겨 두었습니다. 현재 자동차 모듈은 위 V0.5 파일을 사용하세요.
