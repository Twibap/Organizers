from pathlib import Path
root=Path(r'C:\Users\Twibap\Workspace\Organizers')
p=root/'HeatOrganizerCDraft.FCMacro'
s=p.read_text(encoding='utf-8')
s=s.replace("+ Parameters.CarWellW + 4 mm + Parameters.GearWellD / 2'","+ Parameters.CarWellW + 6 mm + Parameters.GearWellD / 2'")
s=s.replace("dl='Parameters.PlayerRegionL - Parameters.Wall - Parameters.DrawerClear'","dl='Parameters.PlayerRegionL - Parameters.Wall - 2 * Parameters.DrawerClear'")
s=s.replace("            bosses.append(feature(seat+'CarCradle','Part::Cut',car_outer,car_inner))", """            cradle=feature(seat+'CarCradleHollow','Part::Cut',car_outer,car_inner)
            finger=doc.addObject('Part::Cylinder',seat+'CarFingerCut')
            finger.Placement.Rotation=App.Rotation(App.Vector(0,0,1),App.Vector(1,0,0))
            finger.Radius=4
            expr(finger,'Height','Parameters.CarWellW + 2 * Parameters.Wall + 2 mm')
            expr(finger,'Placement.Base.x','('+car_x+') - Parameters.Wall - 1 mm')
            expr(finger,'Placement.Base.y',mid_y)
            expr(finger,'Placement.Base.z','Parameters.DeckTop + 6 mm')
            construction.addObject(finger)
            bosses.append(feature(seat+'CarCradle','Part::Cut',cradle,finger))""")
s=s.replace("    body=doc.addObject('Part::MultiFuse','CarGearBody')", """    base_notch=cylinder('CarGearBaseFingerCut','10 mm','Parameters.Base + 0.1 mm',
                        '('+cx+') + Parameters.TokenW / 2','('+cy+') - 2 mm','0 mm')
    shell=feature('CarGearBaseRelief','Part::Cut',shell,base_notch)
    body=doc.addObject('Part::MultiFuse','CarGearBody')""")
p.write_text(s,encoding='utf-8')
print('carrier clearance and finger access corrected')
