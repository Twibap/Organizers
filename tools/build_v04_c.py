from pathlib import Path
import json
root=Path(r'C:\Users\Twibap\Workspace\Organizers')
s=(root/'HeatOrganizerReferenceDraft.FCMacro').read_text(encoding='utf-8-sig')
def swap(old,new):
    global s
    assert s.count(old)==1,(old[:80],s.count(old))
    s=s.replace(old,new)
swap("('Span', 288), ('Wall', 2), ('Base', 2), ('Gap', 0.8),", "('Span', 288), ('Wall', 2), ('Base', 2), ('Gap', 0.8),\n        ('CarW', 11), ('CarL', 23), ('CarH', 7),\n        ('GearD', 15), ('GearH', 25), ('DeckBottom', 9), ('DeckT', 2), ('GearRecess', 0.8),\n        ('DrawerClear', 0.4), ('DrawerBase', 1.2), ('SeatClear', 1), ('GearClear', 0.5),")
swap("('ModuleW', '=PlayerW + 36 mm')", "('ModuleW', '=PlayerW')")
swap("('CardPitch', '=SampleStack / SampleCards'),", "('CardPitch', '=SampleStack / SampleCards'),\n        ('DeckTop', '=DeckBottom + DeckT'), ('GearFloor', '=DeckTop - GearRecess'),\n        ('GearWellD', '=GearD + 2 * GearClear'),\n        ('CarWellW', '=CarW + 2 * SeatClear'), ('CarWellL', '=CarL + 2 * SeatClear'),\n        ('BayW', '=(TokenW - 3 * Wall) / 2'), ('BayL', '=(PlayerRegionL - 5 * Wall) / 4'),\n        ('DrawerH', '=DeckBottom - Base - 2 * DrawerClear'),")
swap("sheet.set('D4', 'Car, gear, scorepad and token sizes unmeasured')", "sheet.set('D4', 'Car11x23x7; gear base D15/H25 measured; other tokens unmeasured')")
swap("final_group.Label = 'Organizer parts - 29 pieces / reference redesign v0.3'", "final_group.Label = 'Organizer parts - 30 pieces / Instructions C redesign v0.4'")
start=s.index('                pockets=[\n')
end=s.index("                layout.append({'name':name",start)
s=s[:start]+'''                body=tray(name+'Body','Parameters.ModuleW','Parameters.PlayerL','Parameters.ModuleBodyH',x,y,z,1,8,
                          name+' - 24 player cards / separate car-gear carrier',color,'player_cards')
                body.addProperty('App::PropertyInteger','CardCount','Contents').CardCount=24
                body.addProperty('App::PropertyString','PocketSizes','Contents').PocketSizes='Card60x91 mm; usable14.6 under lid lip'
                lid(name+'Lid','Parameters.ModuleW','Parameters.PlayerL',x,y,name+' - locating lid',color,
                    z='('+z+') + Parameters.ModuleBodyH')
'''+s[end:]
swap("'role':'ready_player_set','level':level", "'role':'player_cards','level':level")
start=s.index("    rx='1 mm + 2 * (Parameters.ModuleW + Parameters.Gap)")
end=s.index('    refs = [box(',start)
carrier='''    # Instructions C principle: paired car/gear seats in two columns + lower pull-out tray.
    cx=tx
    cy='1 mm'
    cw='Parameters.TokenW'
    cl='Parameters.PlayerRegionL'
    outer=box('CarGearOuter',cw,cl,'Parameters.BodyH',cx,cy,'0 mm')
    upper=box('CarGearUpperCavity','Parameters.TokenW - 2 * Parameters.Wall',
              'Parameters.PlayerRegionL - 2 * Parameters.Wall','Parameters.BodyH',
              '('+cx+') + Parameters.Wall','('+cy+') + Parameters.Wall','Parameters.DeckTop')
    lower=box('CarGearDrawerCavity','Parameters.TokenW - 2 * Parameters.Wall',
              'Parameters.PlayerRegionL - Parameters.Wall','Parameters.DeckBottom - Parameters.Base',
              '('+cx+') + Parameters.Wall',cy,'Parameters.Base')
    shell=feature('CarGearShell','Part::Cut',feature('CarGearHollow','Part::Cut',outer,upper),lower)
    bosses=[]
    gear_centres=[]
    car_origins=[]
    def cylinder(name,radius,height,x,y,z):
        obj=doc.addObject('Part::Cylinder',name)
        for prop,value in [('Radius',radius),('Height',height),('Placement.Base.x',x),('Placement.Base.y',y),('Placement.Base.z',z)]:
            expr(obj,prop,value)
        construction.addObject(obj)
        return obj
    for col in range(2):
        for row in range(4):
            idx=col*4+row+1
            seat='Seat%02d'%idx
            ox='('+cx+') + %d * (Parameters.BayW + Parameters.Wall)'%col
            mid_y='('+cy+') + Parameters.Wall + Parameters.BayL / 2 + %d * (Parameters.BayL + Parameters.Wall)'%row
            car_x='('+ox+') + Parameters.Wall + 3 mm'
            car_y='('+mid_y+') - Parameters.CarWellL / 2'
            gear_x='('+ox+') + Parameters.Wall + 3 mm + Parameters.CarWellW + 4 mm + Parameters.GearWellD / 2'
            well=cylinder(seat+'GearWell','Parameters.GearWellD / 2','Parameters.GearRecess + 0.1 mm',gear_x,mid_y,'Parameters.GearFloor')
            shell=feature(seat+'Recess','Part::Cut',shell,well)
            cup_outer=cylinder(seat+'GearCupOuter','Parameters.GearWellD / 2 + Parameters.Wall','4 mm',gear_x,mid_y,'Parameters.DeckTop')
            cup_inner=cylinder(seat+'GearCupInner','Parameters.GearWellD / 2','4.1 mm',gear_x,mid_y,'Parameters.DeckTop')
            bosses.append(feature(seat+'GearCup','Part::Cut',cup_outer,cup_inner))
            car_outer=box(seat+'CarCradleOuter','Parameters.CarWellW + 2 * Parameters.Wall','Parameters.CarWellL + 2 * Parameters.Wall','6 mm',
                          '('+car_x+') - Parameters.Wall','('+car_y+') - Parameters.Wall','Parameters.DeckTop')
            car_inner=box(seat+'CarCradleInner','Parameters.CarWellW','Parameters.CarWellL','6.1 mm',car_x,car_y,'Parameters.DeckTop')
            bosses.append(feature(seat+'CarCradle','Part::Cut',car_outer,car_inner))
            gear_centres.append((idx,gear_x,mid_y))
            car_origins.append((idx,car_x,car_y))
    bosses.append(box('CarGearCentralSpine','Parameters.Wall','Parameters.PlayerRegionL - 2 * Parameters.Wall','8 mm',
                      '('+cx+') + Parameters.Wall + Parameters.BayW','('+cy+') + Parameters.Wall','Parameters.DeckTop'))
    for row in range(1,4):
        bosses.append(box('CarGearSeatDivider'+str(row),'Parameters.TokenW - 2 * Parameters.Wall','Parameters.Wall','4 mm',
                          '('+cx+') + Parameters.Wall','('+cy+') + Parameters.Wall + %d * Parameters.BayL + %d * Parameters.Wall'%(row,row-1),'Parameters.DeckTop'))
    # Side reliefs expose the vehicles; the full-height corner posts support the lid.
    for side in range(2):
        cut=box('CarGearSideRelief'+str(side),'Parameters.Wall + 0.2 mm','Parameters.PlayerRegionL - 16 mm','Parameters.BodyH',
                '('+cx+') + %d * (Parameters.TokenW - Parameters.Wall) - 0.1 mm'%side,
                '('+cy+') + 8 mm','Parameters.DeckTop + 7 mm')
        shell=feature('CarGearSideCut'+str(side),'Part::Cut',shell,cut)
    body=doc.addObject('Part::MultiFuse','CarGearBody')
    body.Shapes,body.Refine=[shell]+bosses,True
    construction.addObject(body)
    finish(body,'C - paired car/gear carrier / 8 colours + lower drawer',(0.31,0.38,0.44),'car_gear_carrier')
    body.addProperty('App::PropertyString','ContentsSummary','Contents').ContentsSummary='8 cars11x23x7; 8 upright gears baseD15/H25; gear socketD16'
    body.addProperty('App::PropertyString','GearFitAssumption','Contents').GearFitAssumption='15mm is measured base diameter; upper part assumed within same cylinder envelope'
    # Lid has skirt interruptions over the central spine and the three seat partitions.
    lid('CarGearLid',cw,cl,cx,cy,'C - carrier locating lid',(0.31,0.38,0.44),slots=4,
        split_x='Parameters.Wall + Parameters.BayW')
    dw='Parameters.TokenW - 2 * Parameters.Wall - 2 * Parameters.DrawerClear'
    dl='Parameters.PlayerRegionL - Parameters.Wall - Parameters.DrawerClear'
    dx='('+cx+') + Parameters.Wall + Parameters.DrawerClear'
    dy='('+cy+') + Parameters.DrawerClear'
    dz='Parameters.Base + Parameters.DrawerClear'
    drawer_outer=box('CarGearDrawerOuter',dw,dl,'Parameters.DrawerH',dx,dy,dz)
    drawer_inner=box('CarGearDrawerInner','('+dw+') - 2 * Parameters.DrawerBase','('+dl+') - 2 * Parameters.DrawerBase','Parameters.DrawerH',
                     '('+dx+') + Parameters.DrawerBase','('+dy+') + Parameters.DrawerBase','('+dz+') + Parameters.DrawerBase')
    drawer=feature('CarGearDrawerHollow','Part::Cut',drawer_outer,drawer_inner)
    notch=doc.addObject('Part::Cylinder','CarGearDrawerFingerCut')
    notch.Placement.Rotation=App.Rotation(App.Vector(0,0,1),App.Vector(0,1,0))
    notch.Radius=8
    expr(notch,'Height','Parameters.DrawerBase + 2 mm')
    expr(notch,'Placement.Base.x','('+cx+') + Parameters.TokenW / 2')
    expr(notch,'Placement.Base.y','('+dy+') - 1 mm')
    expr(notch,'Placement.Base.z','('+dz+') + Parameters.DrawerH')
    construction.addObject(notch)
    finish(feature('CarGearDrawer','Part::Cut',drawer,notch),'C - lower pull-out tray / provisional 5mm usable height',
           (0.46,0.51,0.56),'optional_lower_drawer')
    layout.append({'name':'CarGear','width':p['TokenW'],'length':p['PlayerRegionL'],'height':p['TotalH'],
                   'role':'car_gear_carrier','color':[0.31,0.38,0.44],'cars':8,'gears':8})
'''
s=s[:start]+carrier+s[end:]
swap("    for ref in refs:\n",'''    for idx,gx,gy in gear_centres:
        gear=cylinder('GearSampleP%02d'%idx,'Parameters.GearD / 2','Parameters.GearH',gx,gy,'Parameters.GearFloor')
        gear.Label='P%02d - gear nominal cylinder, baseD15 / H25; not printable'%idx
        refs.append(gear)
    for idx,px,py in car_origins:
        car=box('CarSampleP%02d'%idx,'Parameters.CarW','Parameters.CarL','Parameters.CarH',
                '('+px+') + Parameters.SeatClear','('+py+') + Parameters.SeatClear','Parameters.DeckTop')
        car.Label='P%02d - measured car envelope11x23x7; not printable'%idx
        refs.append(car)
    for ref in refs:
''')
swap("obj=doc.getObject(module['name']+'Body') or doc.getObject(module['name']+'Lower') or doc.getObject(module['name'])", "obj=doc.getObject(module['name']+'Body') or doc.getObject(module['name']+'Lower') or doc.getObject(module['name'])")
swap("('Accessory',1),('AccessoryLid',1)", "('CarGearBody',1),('CarGearLid',1),('CarGearDrawer',1)")
swap("    (output / 'preview-mesh.json').write_text(json.dumps(preview), encoding='utf-8')",'''    (output / 'preview-mesh.json').write_text(json.dumps(preview), encoding='utf-8')
    component_preview=[]
    for obj in refs:
        if not obj.Name.startswith(('CarSample','GearSample')): continue
        vertices,triangles=obj.Shape.tessellate(0.2)
        index=int(obj.Name[-2:])-1
        component_preview.append({'name':obj.Name,'color':list([(0.78,0.22,0.18),(0.16,0.43,0.70),(0.91,0.66,0.15),(0.18,0.58,0.43),
                                                              (0.30,0.33,0.37),(0.72,0.70,0.65),(0.90,0.40,0.16),(0.52,0.32,0.65)][index]),
                                  'vertices':[[v.x,v.y,v.z] for v in vertices],'triangles':[list(t) for t in triangles]})
    (output/'component-reference-mesh.json').write_text(json.dumps(component_preview),encoding='utf-8')''')
swap("'version':'0.3_reference_redesign'", "'version':'0.4_instructions_C_redesign', 'reference_pdf':r'C:\\Users\\Twibap\\Downloads\\Instructions-Heat-All-In-Board-Game-Insert-Organizer-The-Dicetroyers-min.pdf'")
swap("'maximum_print_part_xy': max", "'gear_seat':{'orientation':'upright','socket_diameter':p['GearWellD'],'socket_floor':p['GearFloor'],'remaining_shelf_floor':p['GearFloor']-p['DeckBottom'],'gear_top_clearance':p['BodyH']-p['GearFloor']-p['GearH']},\n                'lower_drawer_usable_height':p['DrawerH']-p['DrawerBase'],\n                'maximum_print_part_xy': max")
swap("'Two track expansions add one player each: 8 ready modules stacked in four pairs.'", "'Two track expansions add one player each: 8 card-only modules stacked in four pairs; cars/gears in a shared carrier.'")
swap("'Car pocket34x57x14.6 and gear34x32x14.6 are provisional; car/gear actual dimensions unmeasured.'", "'Measured car11x23x7 and gear baseD15/H25. Entire gear assumed within D15 cylinder; actual upper profile unmeasured.',\n                                'Instructions C inspired two-column car/gear carrier and lower pull-out tray. Drawer usable5mm, contents physical fit unmeasured.'")
(root/'HeatOrganizerCDraft.FCMacro').write_text(s,encoding='utf-8')
m=json.loads((root/'heat-measurements.json').read_text(encoding='utf-8-sig'))
m['gear_pawn']={'base_diameter':15,'height':25,'status':'user_measured','storage_orientation':'upright','upper_profile_assumption':'Entire gear within 15mm cylinder; only base diameter measured.'}
m['included_expansions']=['Heavy Rain','Tunnel Vision']
(root/'heat-measurements.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
a=json.loads((root/'heat-component-allocation.json').read_text(encoding='utf-8-sig'))
a['version']='0.4'
a['player_sets']['storage']='64x95x19 card-only trays, eight trays in four pairs; cars/gears separate shared carrier'
a['car_gear_carrier']={'cars':8,'gears':8,'outer_mm':[93.6,190.8,38],'arrangement':'2 columns x4 paired colour seats; Instructions C inspired','gear_base_diameter_mm':15,'gear_height_mm':25,'orientation':'upright','optional_lower_drawer_usable_height_mm':5,'lower_drawer_contents_fit':'unmeasured; scorepads still included in upper flat stack reserve'}
(root/'heat-component-allocation.json').write_text(json.dumps(a,ensure_ascii=False,indent=2),encoding='utf-8')
print('V0.4 C source and measurements updated')
