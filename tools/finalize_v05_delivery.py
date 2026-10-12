from pathlib import Path
import shutil

root = Path.cwd()
folder = Path((root / 'output/latest-heat-draft.txt').read_text(encoding='utf-8-sig').strip())
readme = '''# Heat 오거나이저 — 현재 V0.5

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
& 'C:\\Program Files\\FreeCAD 1.1\\bin\\FreeCADCmd.exe' tools\\headless_compact_draft.py
```

GUI 저장은 FreeCAD에서 `MakeHeatCompactReview.FCMacro`를 실행합니다. 이 단계가 직접 열리는 FCStd의 화면 정보를 저장합니다. `VerifyHeatCompactReview.FCMacro`는 저장한 전체·조립·분해 파일을 다시 열어 확인합니다. 미리보기는 번들 Python으로 `tools/render_heat_v05.py 출력폴더`를 실행합니다.

재생성 직후 `HeatOrganizerDraft.FCStd`는 headless 생성 파일입니다. GUI 저장을 완료한 `HeatOrganizerReview.FCStd`를 사용하세요. 현재 배포 폴더의 Draft는 Review 복사본이며, headless 원본은 `HeatOrganizerDraft-headless.FCStd`로 보존했습니다.

이전 V0.4 및 V0.3 폴더는 이전 설계 참고용으로 남겨 두었습니다. 현재 자동차 모듈은 위 V0.5 파일을 사용하세요.
'''
(root / 'README.md').write_text(readme, encoding='utf-8')

notes = '''# Heat V0.5 작업본 안내

## 이번 수정

자동차·기어 8쌍은 4열×2행으로 수납합니다. 기어를 눕혀 높이를 줄이고, 별도 서랍 프레임 없이 하부 점수판 트레이 위에 자동차 트레이를 올립니다. 덮개를 포함한 외곽은 **110.8×64.8×30.2 mm**입니다. 이전 모듈 93.6×190.8×38 mm 대비 외곽 부피 약 68% 감소입니다. 전역 최소 부피를 증명한 결과는 아닙니다.

점수판은 **전체 묶음이 100×60×7 mm**라는 실측값을 반영했습니다. 요청한 최대 두께 10 mm까지 수납할 수 있도록 설계했으며, 7 mm를 개수만큼 곱하지 않습니다. 상단 맵·설명서 적층 예약에서 점수판을 제외했습니다.

## FreeCAD 확인 파일

| 파일 | 용도 |
| --- | --- |
| CarGearTray-Compact.FCStd | 자동차 모듈 조립본, 외곽 110.8×64.8×30.2 mm |
| CarGearTray-Compact-Exploded.FCStd | 상부를 표시용으로 20 mm 띄운 분해 보기 |
| HeatOrganizerReview.FCStd | 전체 배치 및 매개변수 편집 원본 |
| HeatOrganizerDraft.FCStd | GUI 표시 정보를 포함한 Review와 동일한 복사본 |
| HeatOrganizerDraft-headless.FCStd | GUI 저장 이전 원본 보관용 |

조립본과 분해 보기는 형상을 복사한 확인용 파일입니다. 매개변수 수정은 전체 작업본의 `CompactParameters`와 `Parameters`에서 합니다. `ComponentSamples`는 수납 범위 확인용이며 출력 대상이 아닙니다. 덮개는 초기 보기에서 숨겨져 있으며 모델 트리에서 선택하고 Space로 표시할 수 있습니다. 분해 보기의 상부 20 mm 이동은 실제 조립 간격이 아닙니다.

## 자동차 모듈 치수

| 항목 | 치수 또는 기준 |
| --- | --- |
| 차량 실측 | 11×23×7 mm, 8개 |
| 차량칸 | 25×13 mm, 길이 방향을 25 mm에 배치 |
| 기어 실측 | 밑판 Ø15 mm, 높이 25 mm, 8개 |
| 기어칸 | 눕힌 기어용 26×16 mm 사각 바닥 홈 |
| 기어 상단과 덮개 밑면 사이 | 1 mm |
| 점수판 전체 실측 | 100×60×7 mm |
| 점수판 설계 최대 수납 | 100×60×10 mm |
| 하부 트레이 내부 | 107.6×61.6 mm, 내부 높이 10.6 mm |
| 10 mm 점수판 위 높이 여유 | 0.6 mm |
| 외벽 / 바닥 / 칸막이 / 덮개 | 1.6 / 1.2 / 1.2 / 1.2 mm |
| 상하 트레이 위치결정 턱 | 4곳, 높이 1 mm, 측면 여유 0.2 mm |

차량칸 주변 벽의 일부를 낮춰 손으로 집기 쉽게 했습니다. 상부를 들어서 하부 점수판에 접근합니다. 출력 부품은 `CarScoreTray`, `CarGearBody`, `CarGearLid` 3개입니다. 상하 트레이는 위치결정 턱으로 맞춰 올려놓으며 잠금 기능은 없습니다.

화면의 차량 직육면체와 기어 원통은 사용자 치수를 기준으로 만든 수납 범위 검사 모형입니다. 실제 부품 형상을 복제한 것이 아닙니다. 기어 전체가 Ø15×25 mm 원통 안에 들어간다고 가정했으므로, 상부가 밑판보다 넓다면 해당 칸을 조정해야 합니다.

## 전체 오거나이저 구성

| 수납 | 수량 및 분류 |
| --- | --- |
| 플레이어 카드 | 8벌, 각 24장: 기본 12 + 시작 업그레이드 3 + 스트레스 3 + 열 6 |
| 남은 스트레스·열 | 스트레스 24 + 열 24 = 48장, 한 벌 |
| 차고 모듈 | 기본 34+62 + 확장 12+12 = 120장, 한 트레이에 60장씩 2묶음 |
| 전설·이벤트·트랙 | 10+18+8 = 36장, 한 벌 |
| 후원 카드 | 49장, 별도 트레이 |
| 기상·노면 | 기상 6개, 노면 12개 |
| 취재진 코너 | 말 2개 및 받침, 실물 치수 미확인 |
| 자동차·기어 | 각 8개, 공용 트레이 |
| 점수판 | 전체 묶음 100×60×7 mm, 최대 10 mm 수납 |

Heavy Rain + Tunnel Vision 두 확장 구성 기준입니다. 이전 카드·기상·취재진 배치를 유지하며 자동차 모듈만 줄였습니다. 전체 배치에서는 자동차 모듈을 90° 회전해 64.8×110.8 mm 공간에 놓습니다. 전체 트레이 배치 외곽은 288×288×38 mm입니다.

슬리브 58×89 mm, 24장 두께 9 mm를 기준으로 카드 수납을 확인했습니다. 많은 장수의 카드 두께는 24장 표본의 비례 추정이므로 실제 묶음 두께는 추가 확인이 필요합니다. 힘을 주어 압축한 8.8 mm는 설계 기준으로 사용하지 않았습니다.

## 상단 적층과 박스

박스 내부 290×290×100 mm를 기준으로 하며 높이는 사용자 실측입니다. 가로·세로는 검색 자료 기준입니다. 양면 맵 총 4장 약 50 mm는 기본 맵 2장 25 mm에서 추정했습니다. 기본 개인판·레전드판·챔피언십판·설명서 합계 실측 4 mm를 한 번 더합니다. 확장 개인판 2개와 설명서 2권의 두께는 미측정입니다.

맵·개인판·공용 판·설명서 전체에 60 mm를 예약했습니다. 실제 상단 전체 적층이 60 mm 이하여야 현재 38 mm 트레이 높이 및 2 mm 여유와 함께 100 mm 안에 들어갑니다. 하부 점수판을 상단 적층에 다시 더하지 않습니다.

## 출력과 검증

STL은 16종이며 필요한 수량 합계는 30개입니다. 각 파일명의 `_x수량`과 `manifest.json`을 따릅니다. 자동차·점수판 트레이는 바닥을 아래로, 덮개는 평평한 면을 아래로 두고 위치결정 테두리가 위로 향하도록 출력합니다. FreeCAD 표시에서 기어·차량·점수판 모형은 출력하지 않습니다. STEP은 출력 대상 30개 솔리드를 포함합니다.

- 출력 부품 30개가 모두 유효한 솔리드입니다.
- 출력 부품 사이의 체적 간섭이 없었습니다.
- 카드 묶음 검사 모형 13개, 차량 8개, 눕힌 기어 범위 8개, 최대 10 mm 점수판 범위가 수납 검사를 통과했습니다.
- 상부 트레이를 들어 올리는 동작에서 하부 트레이와의 간섭이 없었습니다.
- STL의 닫힌 메시 및 STEP 솔리드를 확인했습니다.
- 매개변수 변경 후 재계산을 확인했습니다.
- 전체 작업본·모듈 조립본·분해 보기를 GUI에서 저장하고, 별도 꾸미기 없이 다시 열어 화면 표시와 형상을 확인했습니다.

검사 기록은 `draft-verification.json`과 `review-reopen-status.json`입니다. 이는 CAD 검사 결과이며 실물 출력 끼움, 기어 상부 형상, 덮개 고정력, 이동 중 구성품 유지력 및 미측정 토큰 수납까지 확인한 결과는 아닙니다.
'''
(folder / 'Draft-notes.md').write_text(notes, encoding='utf-8')

constraints_path = root / 'Heat-design-constraints.md'
constraints = constraints_path.read_text(encoding='utf-8-sig')
constraints = constraints.replace('확장팩 이름은 아직 확정되지 않았으며, 사용자가 알려준 구성에 따라 확장팩마다 양면 맵 1장·개인판 1개·설명서 1권을 추가합니다.', '현재 작업본은 Heavy Rain과 Tunnel Vision 조합을 기준으로 하며, 확장팩마다 양면 맵 1장·개인판 1개·설명서 1권을 추가합니다.')
old_heading = '\n## V0.4 자동차/기어 실측 반영'
if old_heading in constraints:
    constraints = constraints.split(old_heading)[0].rstrip() + '\n'
constraints += '''

## V0.5 자동차·기어·점수판 실측 반영

차량 11×23×7 mm와 기어 밑판 Ø15 mm·높이 25 mm는 사용자 실측입니다. 자동차·기어 8쌍을 4열×2행으로 배치하며 기어를 눕혀 보관합니다. 차량칸은 25×13 mm, 기어칸은 26×16 mm의 사각 바닥 홈입니다. 전체 기어가 Ø15×25 mm 원통 안에 들어간다는 가정으로 검사했으며 상부 최대 폭은 미측정입니다. 기어 위에 덮개까지 1 mm 여유를 확보했습니다.

점수판 전체 묶음은 100×60×7 mm 실측이며, 요청한 최대 두께 10 mm 수납을 기준으로 하부 트레이를 설계했습니다. 하부 내부 평면은 107.6×61.6 mm이고 내부 높이는 10.6 mm입니다. 7 mm를 낱개 두께로 해석하거나 개수만큼 곱하지 않습니다. 점수판은 상단 60 mm 적층 예약에서 제외하며 자동차 트레이 하부에 보관합니다.

자동차 트레이·점수판 트레이·덮개를 3개로 분리 출력합니다. 상하 트레이는 위치결정 턱 4곳으로 맞춰 놓고, 상부를 들어 점수판에 접근합니다. 모듈 조립 외곽은 110.8×64.8×30.2 mm이며 이전 V0.4 모듈 외곽 부피보다 약 68% 작습니다. 전역 최소 부피를 증명한 설계는 아닙니다. 전체 배치에서는 90° 회전하여 64.8×110.8 mm 면적에 넣습니다.

CAD 수납·체적 간섭·STL/STEP·매개변수 재계산과 저장한 FCStd 직접 재열기를 확인했습니다. 실물 출력 끼움과 덮개 고정력은 아직 검증하지 않았습니다. 실제 상단 맵·개인판·설명서 전체 적층 60 mm 이하 조건은 유지합니다.
'''
constraints_path.write_text(constraints, encoding='utf-8')

headless = folder / 'HeatOrganizerDraft-headless.FCStd'
if not headless.exists():
    shutil.copy2(folder / 'HeatOrganizerDraft.FCStd', headless)
shutil.copy2(folder / 'HeatOrganizerReview.FCStd', folder / 'HeatOrganizerDraft.FCStd')
print('Updated README, constraints and Draft-notes; GUI-saved full file copied to Draft.')
