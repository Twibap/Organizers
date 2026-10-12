from pathlib import Path
p=Path(r'C:\Users\Twibap\Workspace\Organizers\tools\render_heat_v04.py')
s=p.read_text(encoding='utf-8')
s=s.replace("            c.rect((sx+4*scale, sy+5*scale, sx+17*scale, sy+30*scale),", "            car_dx=22 if col==0 else 4\n            c.rect((sx+car_dx*scale, sy+5*scale, sx+(car_dx+13)*scale, sy+30*scale),")
s=s.replace("cx, cy, radius = sx+28*scale, sy+17.5*scale, 7.5*scale", "cx, cy, radius = sx+(11 if col==0 else 28)*scale, sy+17.5*scale, 7.5*scale")
s=s.replace('부품 참고물은 실측 외곽 도형','기어 참고물은 밑판 기준 원통')
p.write_text(s,encoding='utf-8')
