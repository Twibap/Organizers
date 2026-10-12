from pathlib import Path
p=Path(r'C:\Users\Twibap\Workspace\Organizers\tools\compact_car_tray.py')
s=p.read_text(encoding='utf-8-sig').replace("('AnchorX',anchor_x),('AnchorY',anchor_y)","('AnchorX','='+anchor_x if 'Parameters' in anchor_x else anchor_x),('AnchorY','='+anchor_y if 'Parameters' in anchor_y else anchor_y)")
p.write_text(s,encoding='utf-8')
