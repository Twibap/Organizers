from pathlib import Path
import json,sys
from PIL import Image
import render_heat_draft as r
folder=Path(sys.argv[1]);m=json.loads((folder/'manifest.json').read_text());p=m['parameters']
meshes=json.loads((folder/'preview-mesh.json').read_text());c=r.Canvas()
c.text((52,38),'HEAT  공개 오거나이저 참고 재구성',40,bold=True)
c.text((54,103),'V0.3  |  플레이어별 카드·차량·기어 통합  |  총 높이 38 mm',23,r.MUTED)
for b in [(40,168,1050,924),(1070,168,1760,924),(40,946,1050,1274),(1070,946,1760,1274)]:c.rect(b,r.WHITE,radius=16)
c.text((65,190),'4개 자리 × 2단 = 플레이어 8세트',27,bold=True)
c.text((65,237),'카드 분류는 유지 / 후원 카드 분리 / 기상·취재진 전용 트레이',19,r.MUTED)
r.render_mesh(c,meshes,(88,295,1008,796),p)
c.text((65,840),'본체 외곽 288 × 288 / 일체형 모듈 100 × 95 × 19',20,bold=True)
c.text((65,881),'차량 실측 11 × 23 × 7 mm 반영 / 기어·토큰은 실측 전',18,r.RED)
c.text((1098,190),'상면 배치 · 카드가 누운 방향',27,bold=True)
c.text((1098,238),'각 플레이어 모듈: 24장 + 차량1 + 기어1',19,r.MUTED)
bx,by,scale=1192,307,1.65
c.rect((bx,by,bx+290*scale,by+290*scale),r.WHITE,r.INK,1.5)
def plan(x,y,w,l,label,sub,color):
    a,b=bx+x*scale,by+y*scale
    c.rect((a,b,a+w*scale,b+l*scale),r.mix(color,1.1),color,1.5,5)
    c.rect((a+2*scale,b+2*scale,a+(w-2)*scale,b+(l-2)*scale),'#F9FCFC',color,1,3)
    c.text((a+w*scale/2,b+l*scale/2-10),label,17,color,True,'mm')
    if sub:c.text((a+w*scale/2,b+l*scale/2+15),sub,13,r.MUTED,anchor='mm')
for row in range(2):
    for col in range(2):
        first=(row*2+col)*2+1
        x,y=1+col*100.8,1+row*95.8
        plan(x,y,100,95,f'P{first} + P{first+1}','2세트 적층 / 각 19mm',r.TEAL)
        a,b=bx+x*scale,by+y*scale
        c.line([(a+64*scale,b+3*scale),(a+64*scale,b+92*scale)],r.TEAL,1)
        c.line([(a+64*scale,b+60*scale),(a+98*scale,b+60*scale)],r.TEAL,1)
plan(202.6,1,64,95,'공용 48장','스트레스·열',r.AMBER)
plan(202.6,96.8,64,95,'후원 49장','별도 한 벌',r.AMBER)
plan(1,192.6,128.8,96.4,'차고 120장','한 트레이 / 60장씩 두 칸',r.AMBER)
c.line([(bx+65.4*scale,by+196*scale),(bx+65.4*scale,by+286*scale)],r.AMBER,1)
plan(130.6,192.6,64,96.4,'기타 36장','전설·이벤트·트랙',r.AMBER)
plan(195.4,192.6,93.6,96.4,'기상·취재진','토큰 하단 / 말 상단',r.BLUE)
plan(267.4,1,21.6,190.8,'예비','',r.BLUE)
r.dim(c,(bx,by-18),(bx+290*scale,by-18),'290 mm')
c.text((1098,815),'차고·후원·공용·기타 덱을 각각 꺼낼 수 있음',19,r.MUTED)
c.text((1098,855),'아래 플레이어 모듈을 꺼낼 때 위 모듈을 먼저 분리',18,r.MUTED)
c.text((1098,891),'점수패드 3권은 보드·판류·설명서와 상단 적층',18,r.MUTED)
r.side_height(c,p)
c.text((1098,967),'일체형 플레이어 트레이 1개',25,bold=True)
single=[n for n in meshes if n['name']=='P01Body']
r.render_mesh(c,single,(1104,1027,1420,1225),p)
c.text((1440,1032),'카드칸 60 × 91',18,bold=True)
c.text((1440,1074),'24장 약 9 mm',18,r.MUTED)
c.text((1440,1120),'차량칸 34 × 57',18,bold=True)
c.text((1440,1162),'기어칸 34 × 32',18,bold=True)
c.text((1440,1204),'차량 실측 11×23×7',17,r.RED)
c.text((1098,1242),'덮개 1.6mm 포함 19mm / 두 모듈 적층 38mm',18,r.MUTED)
c.text((46,1280),'참고: The Dicetroyers + AM MEDIA 3D  |  구조 원칙을 참고한 새 초안 / 실제 부품 끼움·출력 전',13,r.MUTED)
target=folder/'HeatOrganizerDraft-preview.png';c.im.resize((r.W,r.H),Image.Resampling.LANCZOS).save(target)
print(target)
