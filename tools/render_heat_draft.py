#!/usr/bin/env python3
"""Render a reviewable Heat organizer draft from a CAD export directory.

Usage: python tools/render_heat_draft.py OUTPUT_DIRECTORY
Reads manifest.json and, when present, preview-mesh.json. Writes
HeatOrganizerDraft-preview.png. Pillow is the only nonstandard dependency.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

try:
    import numpy as np
except ImportError:
    np = None

W, H, SS = 1800, 1300, 2
INK = "#193746"
MUTED = "#657A87"
BG = "#F0F4F5"
WHITE = "#FFFFFF"
LINE = "#DCE6E9"
TEAL = "#2D908F"
AMBER = "#D7954E"
BLUE = "#628DAE"
RED = "#A95142"

DEFAULTS = dict(BoxX=290, BoxY=290, BoxH=100, Span=288, Wall=2,
                Base=2, Gap=0.8, PlayerW=64, PlayerL=95, LowerH=13,
                TotalH=38, LidT=1.6, LipD=0.8, LipClear=0.25,
                LipWall=1.2, StackReserve=60, Headroom=2,
                CommonL=96.4, RailW=28.8, PlayerRegionL=190.8)


def numeric(value, fallback):
    if isinstance(value, dict):
        value = value.get("value", fallback)
    try:
        return float(value)
    except (ValueError, TypeError):
        return fallback


def fonts(size, bold=False):
    candidates = (
        r"C:\Windows\Fonts\malgunbd.ttf" if bold else r"C:\Windows\Fonts\malgun.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    )
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, int(size * SS))
    return ImageFont.load_default()


class Canvas:
    def __init__(self):
        self.im = Image.new("RGB", (W * SS, H * SS), BG)
        self.d = ImageDraw.Draw(self.im)
        self.fonts = {}

    def font(self, size, bold=False):
        key = (size, bold)
        if key not in self.fonts:
            self.fonts[key] = fonts(size, bold)
        return self.fonts[key]

    def line(self, points, color=LINE, width=1):
        self.d.line([(round(x * SS), round(y * SS)) for x, y in points],
                    fill=color, width=max(1, round(width * SS)))

    def rect(self, b, fill=WHITE, outline=None, width=1, radius=0):
        b = tuple(round(v * SS) for v in b)
        if radius:
            self.d.rounded_rectangle(b, radius=round(radius * SS),
                                     fill=fill, outline=outline, width=max(1, round(width * SS)))
        else:
            self.d.rectangle(b, fill=fill, outline=outline, width=max(1, round(width * SS)))

    def poly(self, pts, fill, outline=None, width=1):
        self.d.polygon([(round(x * SS), round(y * SS)) for x, y in pts],
                       fill=fill)
        if outline:
            self.line(pts + [pts[0]], outline, width)

    def text(self, xy, s, size=20, color=INK, bold=False, anchor=None):
        self.d.text(tuple(round(v * SS) for v in xy), str(s),
                    fill=color, font=self.font(size, bold), anchor=anchor)

    def textfit(self, xy, s, max_width, size=20, color=INK, bold=False):
        font = self.font(size, bold)
        lines, line = [], ""
        for char in str(s):
            candidate = line + char
            if self.d.textlength(candidate, font=font) > max_width * SS and line:
                lines.append(line)
                line = char
            else:
                line = candidate
        if line:
            lines.append(line)
        for i, line in enumerate(lines):
            self.text((xy[0], xy[1] + i * size * 1.45), line, size, color, bold)
        return len(lines) * size * 1.45


def rgb(color):
    if isinstance(color, str):
        color = color.lstrip("#")
        return tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
    vals = list(color[:3])
    if max(vals, default=0) <= 1:
        vals = [v * 255 for v in vals]
    return tuple(max(0, min(255, round(v))) for v in vals)


def mix(col, factor):
    return tuple(max(0, min(255, round(v * factor))) for v in rgb(col))


def iso(v):
    x, y, z = v
    return ((x - y) * 0.8660254038, (x + y) * 0.5 - z)


def box_mesh(x, y, z, w, l, h, color):
    v = [[x, y, z], [x+w, y, z], [x+w, y+l, z], [x, y+l, z],
         [x, y, z+h], [x+w, y, z+h], [x+w, y+l, z+h], [x, y+l, z+h]]
    return {"color": color, "vertices": v, "triangles": [
        [0, 2, 1], [0, 3, 2], [0, 1, 5], [0, 5, 4],
        [1, 2, 6], [1, 6, 5], [2, 3, 7], [2, 7, 6],
        [3, 0, 4], [3, 4, 7], [4, 5, 6], [4, 6, 7]]}


def fallback_mesh(p):
    """Open tray walls when CAD tessellation is not present."""
    pieces = []
    base, wall = p["Base"], p["Wall"]
    def tray(x, y, z, w, l, h, color):
        pieces.extend([
            box_mesh(x,y,z,w,l,base,color),
            box_mesh(x,y,z,w,wall,h,color),
            box_mesh(x,y+l-wall,z,w,wall,h,color),
            box_mesh(x,y+wall,z,wall,l-2*wall,h,color),
            box_mesh(x+w-wall,y+wall,z,wall,l-2*wall,h,color),
        ])
    x0 = (p["BoxX"]-p["Span"])/2
    y0 = (p["BoxY"]-p["Span"])/2
    upperh = p["TotalH"]-p["LowerH"]-p["LidT"]
    for row in range(2):
        for col in range(4):
            x, y = x0+col*(p["PlayerW"]+p["Gap"]), y0+row*(p["PlayerL"]+p["Gap"])
            tray(x,y,0,p["PlayerW"],p["PlayerL"],p["LowerH"],TEAL)
            tray(x,y,p["LowerH"],p["PlayerW"],p["PlayerL"],upperh,TEAL)
    cy = y0+p["PlayerRegionL"]+p["Gap"]
    for col in range(4):
        tray(x0+col*(p["PlayerW"]+p["Gap"]),cy,0,
             p["PlayerW"],p["CommonL"],p["TotalH"]-p["LidT"],AMBER)
    rx = x0+4*(p["PlayerW"]+p["Gap"])
    tray(rx,y0,0,p["RailW"],p["PlayerRegionL"],p["TotalH"]-p["LidT"],BLUE)
    tray(rx,cy,0,p["RailW"],p["CommonL"],p["TotalH"]-p["LidT"],BLUE)
    return pieces


def render_mesh(c, meshes, bounds, p):
    meshes = [m for m in meshes if m.get("vertices") and m.get("triangles")]
    verts = [v for m in meshes for v in m["vertices"]]
    if not verts:
        meshes = fallback_mesh(p)
        verts = [v for m in meshes for v in m["vertices"]]
    projections = [iso(v) for v in verts]
    xmin, xmax = min(v[0] for v in projections), max(v[0] for v in projections)
    ymin, ymax = min(v[1] for v in projections), max(v[1] for v in projections)
    x1,y1,x2,y2 = bounds
    scale = min((x2-x1)/(xmax-xmin), (y2-y1)/(ymax-ymin))
    ox = (x1+x2)/2 - (xmin+xmax)/2*scale
    oy = (y1+y2)/2 - (ymin+ymax)/2*scale
    def project(v):
        a,b = iso(v)
        return [a*scale+ox, b*scale+oy]
    triangles = []
    light = (0.18, -0.36, 0.92)
    for mesh in meshes:
        vs = mesh["vertices"]
        col = mesh.get("color", [0.2,0.6,0.6])
        for tri in mesh["triangles"]:
            try:
                a,b,d = [vs[int(i)] for i in tri]
            except (IndexError, TypeError, ValueError):
                continue
            u = [b[k]-a[k] for k in range(3)]
            v = [d[k]-a[k] for k in range(3)]
            n = [u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0]]
            length = math.sqrt(sum(t*t for t in n))
            if length < 1e-8:
                continue
            normal = [t/length for t in n]
            if sum(normal) <= 1e-8:
                continue  # Camera-facing surfaces only; suppress hidden triangle seams.
            brightness = 0.77 + 0.25*max(0,sum(normal[k]*light[k] for k in range(3)))
            depth = sum(sum(pt) for pt in (a,b,d))/3
            triangles.append((depth, [project(pt) for pt in (a,b,d)], mix(col, brightness),
                              [sum(pt) for pt in (a,b,d)]))
    triangles.sort(key=lambda t:t[0])
    if np is None:
        for _,pts,col,_ in triangles:
            c.poly(pts,col)
    else:
        # Orthographic depth interpolation prevents painter-order artifacts.
        left,top,right,bottom = [round(t*SS) for t in bounds]
        rw,rh = right-left,bottom-top
        colorbuf = np.full((rh,rw,3),255,dtype=np.uint8)
        depthbuf = np.full((rh,rw),-np.inf,dtype=np.float32)
        for _,pts,col,depths in triangles:
            pp=[(pt[0]*SS-left,pt[1]*SS-top) for pt in pts]
            xs=[pt[0] for pt in pp]
            ys=[pt[1] for pt in pp]
            lo_x=max(0,int(math.floor(min(xs))))
            hi_x=min(rw-1,int(math.ceil(max(xs))))
            lo_y=max(0,int(math.floor(min(ys))))
            hi_y=min(rh-1,int(math.ceil(max(ys))))
            if hi_x<lo_x or hi_y<lo_y:
                continue
            xx,yy=np.meshgrid(np.arange(lo_x,hi_x+1)+0.5,
                              np.arange(lo_y,hi_y+1)+0.5)
            den=(ys[1]-ys[2])*(xs[0]-xs[2])+(xs[2]-xs[1])*(ys[0]-ys[2])
            if abs(den)<1e-8:
                continue
            aa=((ys[1]-ys[2])*(xx-xs[2])+(xs[2]-xs[1])*(yy-ys[2]))/den
            bb=((ys[2]-ys[0])*(xx-xs[2])+(xs[0]-xs[2])*(yy-ys[2]))/den
            dd=1-aa-bb
            depth=aa*depths[0]+bb*depths[1]+dd*depths[2]
            zview=depthbuf[lo_y:hi_y+1,lo_x:hi_x+1]
            mask=(aa>=-1e-7)&(bb>=-1e-7)&(dd>=-1e-7)&(depth>=zview)
            zview[mask]=depth[mask]
            colorbuf[lo_y:hi_y+1,lo_x:hi_x+1][mask]=col
        c.im.paste(Image.fromarray(colorbuf),(left,top))
    return len(triangles)


def dim(c, a, b, label, horizontal=True):
    c.line([a,b],MUTED,1.2)
    tick = 6
    if horizontal:
        for x,y in (a,b):
            c.line([(x,y-tick),(x,y+tick)],MUTED,1.2)
        c.text(((a[0]+b[0])/2,(a[1]+b[1])/2-10),label,17,MUTED,anchor="mb")
    else:
        for x,y in (a,b):
            c.line([(x-tick,y),(x+tick,y)],MUTED,1.2)
        c.text(((a[0]+b[0])/2-13,(a[1]+b[1])/2),label,17,MUTED,anchor="rm")


def top_plan(c,p):
    c.text((1100,189),"상면 배치",27,bold=True)
    c.text((1100,235),"288 × 288 mm  ·  8인 + 확장팩 2개",19,MUTED)
    bx,by,scale = 1193,298,1.66
    x0=(p["BoxX"]-p["Span"])/2
    y0=(p["BoxY"]-p["Span"])/2
    def planrect(x,y,w,l,color,label,small=""):
        a,b = bx+x*scale,by+y*scale
        c.rect((a,b,a+w*scale,b+l*scale),mix(color,1.15),color,1.8,7)
        c.rect((a+p["Wall"]*scale,b+p["Wall"]*scale,
                a+(w-p["Wall"])*scale,b+(l-p["Wall"])*scale),
               "#F8FCFB",color,1,4)
        c.text((a+w*scale/2,b+l*scale/2-13),label,17,color,True,"mm")
        if small:
            c.text((a+w*scale/2,b+l*scale/2+15),small,13,MUTED,anchor="mm")
    c.rect((bx,by,bx+p["BoxX"]*scale,by+p["BoxY"]*scale),WHITE,INK,1.5)
    for row in range(2):
        for col in range(4):
            num=row*4+col+1
            planrect(x0+col*(p["PlayerW"]+p["Gap"]),
                     y0+row*(p["PlayerL"]+p["Gap"]),
                     p["PlayerW"],p["PlayerL"],TEAL,f"플레이어 {num}","24장 / 차량·기어")
    cy=y0+p["PlayerRegionL"]+p["Gap"]
    planrect(x0,cy,p['PlayerW'],p['CommonL'],AMBER,'공용 48장','각 24장')
    planrect(x0+p['PlayerW']+p['Gap'],cy,2*p['PlayerW']+p['Gap'],p['CommonL'],AMBER,'차고 120장','한 트레이 / 60장씩 두 묶음')
    planrect(x0+3*(p['PlayerW']+p['Gap']),cy,p['PlayerW'],p['CommonL'],AMBER,'기타 85장','기타36 + 후원49')
    rx=x0+4*(p["PlayerW"]+p["Gap"])
    planrect(rx,y0,p["RailW"],p["PlayerRegionL"],BLUE,"기상","")
    for k in (1,2):
        y=by+(y0+k*p["PlayerRegionL"]/3)*scale
        c.line([(bx+(rx+p["Wall"])*scale,y),
                (bx+(rx+p["RailW"]-p["Wall"])*scale,y)],BLUE,2)
    planrect(rx,cy,p["RailW"],p["CommonL"],BLUE,"취재","")
    y=by+(cy+p["CommonL"]/2)*scale
    c.line([(bx+(rx+p["Wall"])*scale,y),
            (bx+(rx+p["RailW"]-p["Wall"])*scale,y)],BLUE,2)
    dim(c,(bx,by-20),(bx+p["BoxX"]*scale,by-20),f'{p["BoxX"]:g} mm')
    dim(c,(bx-24,by),(bx-24,by+p["BoxY"]*scale),f'{p["BoxY"]:g} mm',False)
    c.text((1100,815),"개인 카드칸 내부 60 × 91 mm",18,MUTED)
    c.text((1100,845),"후원49 + 기타36 = 85장 / 여유 약 1.7 mm",18,MUTED)


def side_height(c,p):
    c.text((63,973),"박스 내부 높이 배분",25,bold=True)
    x,y,bw,hs = 64,1020,370,2.08
    h = p["BoxH"]
    reserve,org=p["StackReserve"],p["TotalH"]
    room=p["Headroom"]
    bottom=y+h*hs
    c.rect((x,y,x+bw,bottom),WHITE,INK,1.5)
    c.rect((x+2,bottom-org*hs,x+bw-2,bottom-2),TEAL)
    c.rect((x+2,bottom-(org+reserve)*hs,x+bw-2,bottom-org*hs),AMBER)
    c.rect((x+2,y+2,x+bw-2,y+room*hs),"#DBE5E9")
    c.text((x+bw/2,bottom-org*hs/2),"오거나이저 38 mm",20,WHITE,True,"mm")
    c.text((x+bw/2,bottom-(org+reserve/2)*hs),"상부 적층 예약 60 mm",20,WHITE,True,"mm")
    c.line([(x+bw+25,y),(x+bw+25,bottom)],MUTED,1.2)
    for yy in (y,bottom):
        c.line([(x+bw+19,yy),(x+bw+31,yy)],MUTED,1.2)
    c.text((x+bw+42,y+h*hs/2),f'{h:g}',17,MUTED,anchor="mm")
    c.text((526,1018),"상부 적층 = 맵 4장 + 판류 + 설명서 + 점수패드",20,bold=True)
    c.text((526,1060),"54 mm + 확장 판류·설명서 + 점수패드 3권",20,MUTED)
    c.text((526,1102),"60 mm는 실측값이 아닌 설계 예약 공간",19,RED)
    c.text((526,1144),"남는 높이 2 mm는 뚜껑 여유",19,MUTED)
    c.textfit((526,1186),"추가 적층이 6 mm를 넘으면 트레이 높이 조정 필요",475,18,RED)


def exploded(c,p):
    c.text((1100,920),"개인 트레이 1세트",25,bold=True)
    c.text((1100,963),"64 × 95 mm  ·  닫힘 높이 38 mm",18,MUTED)
    ox,oy,scale = 1213,1093,1.3
    def point(v):
        xx,yy=iso(v)
        return [ox+xx*scale,oy+yy*scale]
    def slab(z,h,color):
        w,l=p["PlayerW"],p["PlayerL"]
        pts=[[0,0,z],[w,0,z],[w,l,z],[0,l,z],
             [0,0,z+h],[w,0,z+h],[w,l,z+h],[0,l,z+h]]
        for ids,factor in (([1,2,6,5],.73),([2,3,7,6],.88),([4,5,6,7],1.08)):
            c.poly([point(pts[i]) for i in ids],mix(color,factor),WHITE,.7)
        return point([w,0,z+h])
    # Exploded spacing is illustrative; dimensions are the actual part heights.
    a=slab(0,p["LowerH"],TEAL)
    b=slab(31,p["TotalH"]-p["LowerH"]-p["LidT"],TEAL)
    d=slab(72,p["LidT"],BLUE)
    for pt,yy,label in ((d,1038,"덮개 1.6 mm"),
                         (b,1100,"상부 트레이 23.4 mm"),
                         (a,1174,"하부 트레이 13 mm")):
        c.line([pt,[1388,yy+12]],MUTED,1)
        c.text((1405,yy),label,18)
    c.text((1100,1240),"하부: 24장 × 약 9 mm / 내부 깊이 11 mm",18,MUTED)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_directory",type=Path)
    args=parser.parse_args()
    directory=args.output_directory.resolve()
    manifest=json.loads((directory/"manifest.json").read_text(encoding="utf-8-sig"))
    raw=manifest.get("parameters",manifest.get("params",{}))
    p={k:numeric(raw.get(k,manifest.get(k,v)),v) for k,v in DEFAULTS.items()}
    mesh_path=directory/"preview-mesh.json"
    meshes=None
    if mesh_path.exists():
        data=json.loads(mesh_path.read_text(encoding="utf-8-sig"))
        if isinstance(data,list):
            meshes=data
        elif isinstance(data,dict):
            meshes=data.get("pieces",data.get("meshes",[]))
    c=Canvas()
    c.text((52,38),"HEAT  오거나이저 제작 초안",42,bold=True)
    c.text((54,102),"기본판 + 확장팩 2개  |  슬리브 58 × 89 mm  |  모든 치수 mm",23,MUTED)
    c.rect((1510,47,1750,108),"#FBECDD",None,radius=12)
    c.text((1630,78),"DRAFT  ·  V0.2",23,RED,True,"mm")
    c.rect((40,168,1050,924),WHITE,None,radius=16)
    c.rect((1070,168,1760,890),WHITE,None,radius=16)
    c.rect((40,946,1050,1274),WHITE,None,radius=16)
    c.rect((1070,906,1760,1274),WHITE,None,radius=16)
    c.text((65,189),"3D 구조 검토",27,bold=True)
    c.text((65,233),"덮개를 제외한 CAD 형상 / 8개의 개인 2단 트레이",19,MUTED)
    if not meshes:
        meshes=fallback_mesh(p)
        c.text((65,275),"형상 도식 · CAD 메시 미제공",16,RED)
    count=render_mesh(c,meshes,(94,310,1000,798),p)
    c.text((65,840),"본체 외곽 288 × 288 / 닫힘 높이 38",20,bold=True)
    c.text((65,879),"차량·토큰·취재진 말 실측 전 / 점수패드 3권은 상단 적층",18,RED)
    top_plan(c,p)
    side_height(c,p)
    exploded(c,p)
    c.text((46,1280),"* 24장 9 mm 표본에서 추정한 카드 용량. 압축값 8.8 mm는 설계 기준으로 사용하지 않음.",13,MUTED)
    target=directory/"HeatOrganizerDraft-preview.png"
    c.im.resize((W,H),Image.Resampling.LANCZOS).save(target)
    print(json.dumps({"preview":str(target),"width":W,"height":H,"triangles":count},ensure_ascii=False))


if __name__=="__main__":
    main()
