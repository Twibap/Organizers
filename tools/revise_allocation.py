from pathlib import Path
import json
root=Path(r'C:\Users\Twibap\Workspace\Organizers')
f=root/'HeatOrganizerDraft.FCMacro'
s=f.read_text(encoding='utf-8-sig')
(root/'HeatOrganizerDraft-v01.FCMacro').write_text(s,encoding='utf-8')
s=s.replace('Organizer parts - 36 pieces','Organizer parts - 34 pieces / allocated v0.2')
s=s.replace('card tray / sample 24 cards','24 cards: basic12 + starting3 + stress3 + heat6')
a=s.index('    for col in range(4):\n        name = \'C%02d\'')
b=s.index("    rail_x =",a)
s=s[:a]+'''    common_specs = [
        ('C01', 0, 1, 'Reserve / stress24 + heat24 = 48 cards', 'reserve_cards', 48),
        ('C02', 1, 2, 'Garage / 120 cards in two adjacent stacks of 60', 'garage_cards', 120),
        ('C04', 3, 1, 'Legends10 + events18 + tracks8; sponsorship49 below = 85', 'championship_cards', 85),
    ]
    for name, col, span, label, role, count in common_specs:
        x = '1 mm + %d * (Parameters.PlayerW + Parameters.Gap)' % col
        width = 'Parameters.PlayerW' if span == 1 else '2 * Parameters.PlayerW + Parameters.Gap'
        color = (0.20, 0.45 + col * 0.035, 0.57 + col * 0.035)
        body = tray(name + 'Body', width, 'Parameters.CommonL', 'Parameters.BodyH', x, common_y,
                    '0 mm', 1, 12, name + ' - ' + label, color, role)
        body.addProperty('App::PropertyInteger', 'CardCount', 'Contents').CardCount = count
        lid(name + 'Lid', width, 'Parameters.CommonL', x, common_y, name + ' - locating lid', color)
        layout.append({'name': name, 'x': 1 + col * (p['PlayerW'] + p['Gap']),
                       'y': 1 + 2 * (p['PlayerL'] + p['Gap']), 'width': span*p['PlayerW']+(span-1)*p['Gap'],
                       'length': p['CommonL'], 'height': p['TotalH'], 'role': role, 'color': list(color),
                       'cards': count, 'allocation': label})
''' +s[b:]
s=s.replace("name + ' - generic token compartments / fit unverified'", "name + (' - weather6 / road12 / standee bases' if index == 1 else ' - press corner standees2 / spare; fit unverified')")
s=s.replace("('C01Body', 4), ('C01Lid', 4),", "('C01Body', 2), ('C01Lid', 2), ('C02Body', 1), ('C02Lid', 1),")
s=s.replace('24 cards is measured sample, not confirmed final player deck count.', 'Player set confirmed: basic12 + starting3 + stress3 + heat6 =24 cards; 8 sets.')
s=s.replace("'layout': layout, 'part_count'", "'component_allocation': json.loads((PROJECT_ROOT / 'heat-component-allocation.json').read_text(encoding='utf-8')), 'layout': layout, 'part_count'")
f.write_text(s,encoding='utf-8')
f=root/'tools/headless_draft.py';s=f.read_text();s=s.replace('== 36','== 34');s=s.replace("    report['fcstd'] =", "    assert 48 * p['CardPitch'] + 1 <= p['BodyH'] - p['Base'] - p['LipD']\n    assert 60 * p['CardPitch'] + 1 <= p['BodyH'] - p['Base'] - p['LipD']\n    assert 85 * p['CardPitch'] + 1 <= p['BodyH'] - p['Base'] - p['LipD']\n    assert 2 * (p['SleeveW'] + 2*p['EdgeClear']) <= 2*p['PlayerW'] + p['Gap'] - 2*p['Wall']\n    report['allocation'] = {'player_sets': 8, 'player_cards_each': 24, 'reserve_cards': 48, 'garage_cards': 120, 'garage_stacks': [60,60], 'championship_and_sponsor_cards': 85, 'estimated_card_clearance_passed': True}\n    report['fcstd'] =")
f.write_text(s,encoding='utf-8')
f=root/'tools/render_heat_draft.py';s=f.read_text(encoding='utf-8-sig');a=s.index('    for col in range(4):\n        planrect',s.index('    cy=y0'));b=s.index('    rx=',a)
s=s[:a]+'''    planrect(x0,cy,p['PlayerW'],p['CommonL'],AMBER,'공용 48장','스트레스24 + 열24')
    planrect(x0+p['PlayerW']+p['Gap'],cy,2*p['PlayerW']+p['Gap'],p['CommonL'],AMBER,'차고 120장','한 트레이 / 60장씩 두 묶음')
    planrect(x0+3*(p['PlayerW']+p['Gap']),cy,p['PlayerW'],p['CommonL'],AMBER,'기타 85장','전설·이벤트·트랙36 / 후원49')
''' +s[b:]
s=s.replace('"2단 트레이"','"24장 / 차량·기어"').replace('BLUE,"토큰",""','BLUE,"기상·노면",""').replace('BLUE,"예약",""','BLUE,"취재진",""').replace('DRAFT  ·  V0.1','DRAFT  ·  V0.2').replace('공용칸 유효 깊이 33.6 mm / 약 86장* ','후원49 + 기타36 = 85장 / 여유 약 1.7 mm').replace('차량·점수패드 공간은 예약 상태 / 실제 끼움·출력 검증 전','차량·토큰·취재진 말 실측 전 / 점수패드 3권은 상단 적층')
f.write_text(s,encoding='utf-8')
allocation={
 'version':'0.2','expansions':['Heavy Rain','Tunnel Vision'],
 'player_sets':{'sets':8,'cards_each':24,'basic_each':12,'starting_each':3,'stress_each':3,'heat_each':6},
 'reserve':{'stress':37+5+6-8*3,'heat':48+15+9-8*6,'total':48,'tray':'C01'},
 'garage':{'base_regular':34,'base_advanced':62,'expansion_advanced_each':12,'total':120,'tray':'C02','stacks':[60,60]},
 'other_cards':{'legends':10,'events':18,'tracks':8,'combined_set':36,'sponsorship':49,'tray':'C04','total_in_tray':85,'storage':'sponsorship below, legends/events/tracks combined above; thin separator optional'},
 'tokens':{'weather':6,'road_conditions':12,'press_corner_standees':2,'rail01':'weather / road / standee bases','rail02':'two press standees and spare compartment; physical fit unverified'},
 'flat_stack':{'double_sided_maps':4,'player_mats':8,'legends_mat':1,'championship_mat':1,'rulebooks':4,'scorepads':3,'reserve_mm':60,'status':'map thickness estimated50; base mats/rules4; expansion mats/rules and scorepads unmeasured'},
 'sources':['https://cdn.svc.asmodee.net/production-daysofwonder/uploads/2025/03/9101-HT-RulesAdvanced-EN_compressed.pdf','https://cdn.svc.asmodee.net/production-daysofwonder/uploads/2025/03/HTEX1-Rules-EN-FC.pdf','https://cdn.svc.asmodee.net/production-daysofwonder/uploads/2025/02/9103-HTEX2_EN_RULES_20240924_compressed.pdf']}
(root/'heat-component-allocation.json').write_text(json.dumps(allocation,ensure_ascii=False,indent=2),encoding='utf-8')
