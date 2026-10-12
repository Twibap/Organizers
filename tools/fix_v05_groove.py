from pathlib import Path
p=Path(r'C:\Users\Twibap\Workspace\Organizers\tools\compact_car_tray.py')
s=p.read_text(encoding='utf-8-sig')
a=s.index("            groove=cyl(name+'GearRound'")
b=s.index('            car_positions.append',a)
s=s[:a]+'''            groove=box(name+'GearPocket',P+'GearChannelL',P+'GearWellD',P+'UpperH',xs,
                       '('+gy+') - '+P+'GearWellD / 2',P+'SeatFloor')
            upper=boolean(name+'GearHollow','Part::Cut',upper,groove)
'''+s[b:]
p.write_text(s,encoding='utf-8')
