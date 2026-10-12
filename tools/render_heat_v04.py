#!/usr/bin/env python3
"""Render the V0.4 C-reference Heat insert from exported FreeCAD meshes.

Usage: python tools/render_heat_v04.py OUTPUT_DIR
The exported CAD geometry drives the isometric illustrations. Component proxies
are reference envelopes only; they are never treated as printable parts.
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


def plan_panel(c):
    c.text((1098, 190), '상면 배치 · 8인 + 확장팩 2개', 25, bold=True)
    c.text((1098, 236), '카드 8벌은 4개 자리에서 두 단으로 적층', 18, r.MUTED)
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
    a, b = plan(195.4, 1, 93.6, 190.8, '', '', r.BLUE)
    c.text((a+46.8*scale, b+12*scale), '차량·기어 8세트', 16, r.BLUE, True, 'mm')
    # This is a labeled plan symbol. Detailed fit geometry appears in the CAD view.
    for row in range(4):
        for col in range(2):
            number = col*4+row
            sx, sy = a+(5+col*43.4)*scale, b+(27+row*39)*scale
            c.rect((sx, sy, sx+39*scale, sy+35*scale), '#F2F6F8', r.LINE, 1, 3)
            color = PLAYER_COLORS[number]
            car_dx=22 if col==0 else 4
            c.rect((sx+car_dx*scale, sy+5*scale, sx+(car_dx+13)*scale, sy+30*scale),
                   r.mix(color, 1.08), color, 1, 4)
            cx, cy, radius = sx+(11 if col==0 else 28)*scale, sy+17.5*scale, 7.5*scale
            c.d.ellipse(tuple(round(v*r.SS) for v in (cx-radius, cy-radius, cx+radius, cy+radius)),
                        fill=r.mix(color, 1.08), outline=r.rgb(color), width=2)
    c.text((1098, 767), '자동차·기어를 같은 색의 자리에서 함께 꺼냄', 18, bold=True)
    c.text((1098, 805), '점수패드 3권은 보드·판류·설명서와 상단 적층', 17, r.MUTED)


def car_detail(c, meshes, references, p):
    c.text((65, 895), 'INSTRUCTIONS C 참고 · 공용 자동차 트레이', 26, bold=True)
    c.text((65, 940), '자동차와 기어 8세트 / 두 열 × 네 자리 / 하부 서랍', 18, r.MUTED)
    assembly = [m for m in meshes if m.get('name') in {'CarGearBody', 'CarGearFrame', 'CarGearDrawer'}]
    components = [m for m in references if m.get('name', '').startswith(('CarSample', 'GearSample'))]
    show_mesh(c, assembly+components, (69, 981, 558, 1204), p)
    c.text((610, 984), '자동차 11 × 23 × 7 mm', 21, bold=True)
    c.text((610, 1023), '받침 내부 13 × 25 mm', 18, r.MUTED)
    c.text((610, 1072), '기어 바닥 Ø15 / 높이 25 mm', 21, bold=True)
    c.text((610, 1111), '웰 Ø16 / 세운 상태로 보관', 18, r.MUTED)
    c.text((610, 1160), '기어 위 덮개 여유 1.2 mm', 19, r.BLUE, bold=True)
    c.text((65, 1232), '하부 서랍 내부 깊이 5 mm · 수납 대상은 실측 후 결정', 18, r.RED)


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
    c.text((x+width/2, bottom-organizer*scale/2), '본체 38 mm', 19, r.WHITE, True, 'mm')
    c.text((x+width/2, bottom-(organizer+reserve/2)*scale), '상부 60 mm', 19, r.WHITE, True, 'mm')
    c.text((1340, 959), '맵 4장 약 50 mm', 20, bold=True)
    c.text((1340, 998), '기본 판류·설명서 4 mm', 18, r.MUTED)
    c.text((1340, 1037), '확장 판류·설명서 + 점수패드', 17, r.MUTED)
    c.text((1340, 1078), '전체 상단 적층: 60 mm 이내', 18, bold=True)
    c.text((1340, 1117), '윗부분 여유 2 mm', 18, r.MUTED)
    c.text((1098, 1229), '60 mm는 설계 예약 공간 · 전체 적층 두께 실측 필요', 16, r.RED)


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
    c.text((52, 38), 'HEAT  자동차·기어 공용 트레이 재구성', 39, bold=True)
    c.text((54, 103), 'V0.4  |  INSTRUCTIONS C 참고  |  기본판 + 확장팩 2개  |  모든 치수 mm', 23, r.MUTED)
    for panel in [(40,168,1050,850), (1070,168,1760,850),
                  (40,872,1050,1270), (1070,872,1760,1270)]:
        c.rect(panel, r.WHITE, radius=16)
    c.text((65, 190), '자동차·기어는 공용 / 개인 카드 8벌은 별도', 26, bold=True)
    c.text((65, 237), '덮개를 제외한 CAD 형상 + 자동차 실측 외곽 · 기어 밑판 기준 원통', 18, r.MUTED)
    triangles = show_mesh(c, meshes+references, (88, 294, 1008, 716), p)
    c.text((65, 750), '본체 288 × 288 × 38 / 개인 카드 모듈 64 × 95 × 19', 21, bold=True)
    c.text((65, 792), '기어를 세워 보관하고, 자동차 받침과 하부 서랍을 한 트레이로 구성', 18, r.MUTED)
    plan_panel(c)
    car_detail(c, meshes, references, p)
    height_panel(c, p)
    c.text((46, 1280),
           '참고: The Dicetroyers 설명서 C · 새 CAD 초안 / 기어 참고물은 밑판 기준 원통 / 실제 출력·끼움 검증 전',
           13, r.MUTED)
    target = folder/'HeatOrganizerDraft-preview.png'
    c.im.resize((r.W, r.H), Image.Resampling.LANCZOS).save(target)
    print(json.dumps({'preview':str(target), 'width':r.W, 'height':r.H,
                      'triangles':triangles, 'component_reference_meshes':len(references)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
