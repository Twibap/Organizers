#!/usr/bin/env python3
"""Render the compact V0.5 Heat organizer from exported FreeCAD meshes.

Usage: python tools/render_heat_v05.py OUTPUT_DIR
Only this preview is written. Component meshes are nominal measurement envelopes,
and the detail is deliberately exploded so the lower scoreboard tray is visible.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image

import render_heat_draft as r

PLAYER_COLORS = ['#C15346', '#537FA9', '#D4B646', '#629560',
                 '#7F858B', '#B4BEC6', '#D58C4B', '#9973B4']


def read_meshes(path: Path):
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding='utf-8-sig'))
    if isinstance(data, dict):
        data = data.get('pieces', data.get('meshes', []))
    return [m for m in data if m.get('vertices') and m.get('triangles')]


def get_params(manifest):
    defaults = dict(r.DEFAULTS)
    defaults.update(ModuleH=19, ModuleBodyH=17.4, ModuleW=64,
                    TokenW=93.6, PlayerRegionL=190.8, CommonL=96.4)
    raw = manifest.get('parameters', manifest.get('params', {}))
    return {k: r.numeric(raw.get(k, v), v) for k, v in defaults.items()}


def show_mesh(c, meshes, bounds, params):
    if meshes:
        return r.render_mesh(c, meshes, bounds, params)
    c.text(((bounds[0]+bounds[2])/2, (bounds[1]+bounds[3])/2),
           'CAD 메시를 찾을 수 없음', 18, r.RED, anchor='mm')
    return 0


def moved_mesh(mesh, dz):
    result = dict(mesh)
    result['vertices'] = [[v[0], v[1], v[2]+dz] for v in mesh['vertices']]
    return result


def plan_panel(c):
    c.text((1098, 190), '상면 배치 · 8인 + 확장팩 2개', 25, bold=True)
    c.text((1098, 236), '자동차 트레이 축소로 빈 공간 확보', 18, r.MUTED)
    bx, by, scale = 1190, 288, 1.55
    c.rect((bx, by, bx+290*scale, by+290*scale), r.WHITE, r.INK, 1.5)
    r.dim(c, (bx, by-16), (bx+290*scale, by-16), '290 mm')

    def plan(x, y, w, length, label, sub, color, label_size=15):
        a, b = bx+x*scale, by+y*scale
        c.rect((a, b, a+w*scale, b+length*scale), r.mix(color, 1.17), color, 1.4, 5)
        c.rect((a+2*scale, b+2*scale, a+(w-2)*scale, b+(length-2)*scale),
               '#FAFCFC', color, 1, 3)
        if label:
            c.text((a+w*scale/2, b+length*scale/2-12), label, label_size, color, True, 'mm')
        if sub:
            c.text((a+w*scale/2, b+length*scale/2+13), sub, 12, r.MUTED, anchor='mm')
        return a, b

    for row in range(2):
        for col in range(2):
            first = (row*2+col)*2+1
            a, b = plan(1+col*64.8, 1+row*95.8, 64, 95,
                        f'P{first} / P{first+1}', '각 24장', r.TEAL, 16)
            for level in range(2):
                sx = a+(4+level*28)*scale
                sy = b+(95-11)*scale
                c.rect((sx, sy, sx+25*scale, sy+5*scale), PLAYER_COLORS[first-1+level], radius=2)
    plan(130.6, 1, 64, 95, '공용 48장', '스트레스·열', r.AMBER)
    plan(130.6, 96.8, 64, 95, '후원 49장', '별도 한 벌', r.AMBER)
    plan(1, 192.6, 128.8, 96.4, '차고 120장', '60장씩 두 칸', r.AMBER, 17)
    c.line([(bx+65.4*scale, by+196*scale), (bx+65.4*scale, by+286*scale)], r.AMBER, 1.2)
    plan(130.6, 192.6, 64, 96.4, '기타 36장', '전설·이벤트·트랙', r.AMBER)
    plan(195.4, 192.6, 93.6, 96.4, '기상·취재진', '하단 토큰 / 상단 말', r.BLUE, 16)

    # Reserve the former car region visually, then draw the new actual footprint.
    x, y = bx+195.4*scale, by+scale
    c.rect((x, y, x+93.6*scale, y+190.8*scale), '#F0F3F5', r.LINE, 1, 5)
    a, b = plan(195.4, 1, 64.8, 110.8, '', '', r.BLUE)
    c.text((a+32.4*scale, b+8*scale), '차량·기어', 14, r.BLUE, True, 'mm')
    # World orientation is two columns by four rows, equivalent to local 4 x 2.
    for row in range(4):
        for col in range(2):
            number = row+col*4
            sx, sy = a+(3+col*29.8)*scale, b+(18+row*21.5)*scale
            color = PLAYER_COLORS[number]
            c.rect((sx, sy, sx+27*scale, sy+18.5*scale), '#F6F9FB', r.LINE, 1, 2)
            c.rect((sx+2*scale, sy+2*scale, sx+25*scale, sy+8*scale),
                   r.mix(color, 1.08), color, 1, 2)
            c.rect((sx+2*scale, sy+10*scale, sx+25*scale, sy+16.5*scale),
                   r.mix(color, 1.08), color, 1, 2)
    c.text((a+32.4*scale, b+105*scale), '하부 점수판', 12, r.BLUE, True, 'mm')
    c.text((x+46.8*scale, y+151*scale), '미배정 공간', 14, r.MUTED, anchor='mm')
    c.text((1098, 767), '기어는 눕혀 보관 · 8쌍은 색별로 분리', 18, bold=True)
    c.text((1098, 805), '점수판은 자동차 트레이 아래 별도 수납', 17, r.MUTED)


def car_detail(c, meshes, references, p):
    c.text((65, 895), '자동차·기어 8쌍 + 하부 점수판', 26, bold=True)
    c.text((65, 940), '분해 표시 · 위 트레이를 들어 점수판을 꺼냄', 18, r.MUTED)
    detail = []
    for m in meshes:
        name = m.get('name')
        if name == 'CarScoreTray':
            detail.append(m)
        elif name == 'CarGearBody':
            detail.append(moved_mesh(m, 20))
    for m in references:
        name = m.get('name', '')
        if name.startswith(('CarSample', 'GearSample')):
            detail.append(moved_mesh(m, 20))
        elif name == 'ScoreboardSample':
            detail.append(m)
    show_mesh(c, detail, (66, 980, 539, 1208), p)
    c.text((580, 984), '외곽 110.8 × 64.8 × 30.2 mm', 21, bold=True)
    c.text((580, 1024), '이전 트레이 대비 외곽 부피 약 68% 감소', 17, r.BLUE, bold=True)
    c.text((580, 1067), '자동차 받침 25 × 13 mm', 19, bold=True)
    c.text((580, 1106), '눕힌 기어 홈 26 × 16 mm', 19, bold=True)
    c.text((580, 1150), '점수판 100 × 60 × 최대 10 mm', 20, bold=True)
    c.text((580, 1189), '실측 두께 7 mm / 위쪽 여유 최소 0.6 mm', 17, r.MUTED)
    c.text((65, 1232), '회색 점수판은 최대 두께 10 mm 기준 검사 형상 · 출력 부품 아님', 17, r.MUTED)


def height_panel(c, p):
    c.text((1098, 895), '박스 내부 높이 · 100 mm 기준', 25, bold=True)
    x, y, width, scale = 1100, 960, 208, 2.28
    height, organizer, reserve = p['BoxH'], p['TotalH'], p['StackReserve']
    bottom = y+height*scale
    c.rect((x, y, x+width, bottom), r.WHITE, r.INK, 1.2)
    c.rect((x+2, bottom-organizer*scale, x+width-2, bottom-2), r.TEAL)
    c.rect((x+2, bottom-(organizer+reserve)*scale,
            x+width-2, bottom-organizer*scale), r.AMBER)
    c.rect((x+2, y+2, x+width-2, y+p['Headroom']*scale), '#DCE6E9')
    c.text((x+width/2, bottom-organizer*scale/2), '전체 38 mm', 19, r.WHITE, True, 'mm')
    c.text((x+width/2, bottom-(organizer+reserve/2)*scale), '상부 60 mm', 19, r.WHITE, True, 'mm')
    c.text((1340, 959), '자동차 트레이 높이 30.2 mm', 19, bold=True)
    c.text((1340, 998), '기존 카드 트레이 높이 38 mm', 18, r.MUTED)
    c.text((1340, 1037), '맵 4장 약 50 mm', 19, bold=True)
    c.text((1340, 1078), '판류·설명서: 상부 적층', 18, r.MUTED)
    c.text((1340, 1117), '윗부분 여유 2 mm', 18, r.MUTED)
    c.text((1098, 1229), '전체 판류·설명서 적층 두께는 실측 필요', 17, r.RED)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output_directory', type=Path)
    args = parser.parse_args()
    folder = args.output_directory.resolve()
    manifest = json.loads((folder/'manifest.json').read_text(encoding='utf-8-sig'))
    p = get_params(manifest)
    meshes = read_meshes(folder/'preview-mesh.json')
    references = read_meshes(folder/'component-reference-mesh.json')
    c = r.Canvas()
    c.text((52, 38), 'HEAT  자동차·기어 트레이 최소 부피 재구성', 39, bold=True)
    c.text((54, 103), 'V0.5  |  8쌍 + 하부 점수판 최대 10 mm  |  기본판 + 확장팩 2개', 23, r.MUTED)
    for panel in [(40,168,1050,850), (1070,168,1760,850),
                  (40,872,1050,1270), (1070,872,1760,1270)]:
        c.rect(panel, r.WHITE, radius=16)
    c.text((65, 190), '기어를 눕혀 높이와 수납 면적 축소', 26, bold=True)
    c.text((65, 237), '덮개 제외 CAD 형상 / 자동차·기어·점수판은 실측 외곽 기준', 18, r.MUTED)
    triangles = show_mesh(c, meshes+references, (88, 294, 1008, 716), p)
    c.text((65, 750), '전체 288 × 288 × 38 / 자동차 트레이 110.8 × 64.8 × 30.2', 20, bold=True)
    c.text((65, 792), '자동차 11 × 23 × 7 · 기어 Ø15 × 25 · 점수판 100 × 60 × 최대 10', 18, r.MUTED)
    plan_panel(c)
    car_detail(c, meshes, references, p)
    height_panel(c, p)
    c.text((46, 1280),
           '새 CAD 초안 · 참고물은 측정 외곽 기준 · 기어 전체 폭은 밑판 지름 기준 · 실제 출력·끼움 검증 전',
           13, r.MUTED)
    target = folder/'HeatOrganizerDraft-preview.png'
    c.im.resize((r.W, r.H), Image.Resampling.LANCZOS).save(target)
    print(json.dumps({'preview':str(target), 'width':r.W, 'height':r.H,
                      'triangles':triangles, 'component_reference_meshes':len(references)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
