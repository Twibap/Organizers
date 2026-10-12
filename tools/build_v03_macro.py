from pathlib import Path
root=Path(r'C:\Users\Twibap\Workspace\Organizers')
s=(root/'HeatOrganizerDraft.FCMacro').read_text(encoding='utf-8-sig')
(root/'HeatOrganizerDraft-v02.FCMacro').write_text(s,encoding='utf-8')
s=s.replace("('SampleCards',", "('ModuleW', '=PlayerW + 36 mm'), ('ModuleH', '=TotalH / 2'),\n        ('ModuleBodyH', '=ModuleH - LidT'), ('TokenW', '=Span - 3 * (PlayerW + Gap)'),\n        ('SampleCards',")
s=s.replace("('RailW', '=Span - 4 * (PlayerW + Gap)')", "('RailW', '=Span - 2 * (ModuleW + Gap) - (PlayerW + Gap)')")
s=s.replace('Organizer parts - 34 pieces / allocated v0.2','Organizer parts - 34 pieces / reference redesign v0.3')
s=s.replace("def lid(name, width, length, x, y, label, color, slots=1):\n        z = 'Parameters.BodyH'", "def lid(name, width, length, x, y, label, color, slots=1, z='Parameters.BodyH', split_x=None, split_y=None):")
s=s.replace("lip_z = 'Parameters.BodyH - Parameters.LipD'", "lip_z = '(' + z + ') - Parameters.LipD'")
needle="        obj = feature(name, 'Part::Fuse', plate, ring)"
s=s.replace(needle,'''        if split_x is not None:
            gap = box(name + 'VerticalGap', 'Parameters.Wall + 2 * Parameters.LipClear', length,
                      'Parameters.LipD + 0.1 mm', '('+x+') + ('+split_x+') - Parameters.LipClear', y, lip_z)
            ring = feature(name + 'ClearVertical', 'Part::Cut', ring, gap)
        if split_y is not None:
            gap = box(name + 'HorizontalGap', width, 'Parameters.Wall + 2 * Parameters.LipClear',
                      'Parameters.LipD + 0.1 mm', x, '('+y+') + ('+split_y+') - Parameters.LipClear', lip_z)
            ring = feature(name + 'ClearHorizontal', 'Part::Cut', ring, gap)
''' +needle)
a=s.index('    player_colors =');b=s.index('    refs =',a)
new='''    player_colors = [(0.78,0.22,0.18),(0.16,0.43,0.70),(0.91,0.66,0.15),(0.18,0.58,0.43),
                     (0.30,0.33,0.37),(0.72,0.70,0.65),(0.90,0.40,0.16),(0.52,0.32,0.65)]

    def pocket_tray(name, width, length, height, x, y, z, pockets, label, color, role):
        outer = box(name+'Outer',width,length,height,x,y,z)
        cuts=[]
        for i,(cw,cl,dx,dy) in enumerate(pockets):
            cuts.append(box(name+'Pocket'+str(i),cw,cl,height,'('+x+') + ('+dx+')',
                            '('+y+') + ('+dy+')','('+z+') + Parameters.Base'))
        tool=doc.addObject('Part::MultiFuse',name+'PocketTool')
        tool.Shapes,tool.Refine=cuts,True
        construction.addObject(tool)
        hollow=feature(name+'Hollow','Part::Cut',outer,tool)
        cutter=doc.addObject('Part::Cylinder',name+'FingerCut')
        cutter.Placement.Rotation=App.Rotation(App.Vector(0,0,1),App.Vector(0,1,0))
        cutter.Radius=8
        expr(cutter,'Height','Parameters.Wall + 2 mm')
        expr(cutter,'Placement.Base.x','('+x+') + Parameters.PlayerW / 2')
        expr(cutter,'Placement.Base.y','('+y+') - 1 mm')
        expr(cutter,'Placement.Base.z','('+z+') + ('+height+')')
        construction.addObject(cutter)
        final=feature(name,'Part::Cut',hollow,cutter)
        return finish(final,label,color,role)

    # Four footprint positions, two independently removable ready sets per position.
    for row in range(2):
        for col in range(2):
            for level in range(2):
                index=(row*2+col)*2+level+1
                name='P%02d'%index
                x='1 mm + %d * (Parameters.ModuleW + Parameters.Gap)'%col
                y='1 mm + %d * (Parameters.PlayerL + Parameters.Gap)'%row
                z='%d * Parameters.ModuleH'%level
                color=player_colors[index-1]
                pockets=[
                    ('Parameters.PlayerW - 2 * Parameters.Wall','Parameters.PlayerL - 2 * Parameters.Wall','Parameters.Wall','Parameters.Wall'),
                    ('Parameters.ModuleW - Parameters.PlayerW - Parameters.Wall','Parameters.PlayerL - 4 * Parameters.Wall - 32 mm','Parameters.PlayerW','Parameters.Wall'),
                    ('Parameters.ModuleW - Parameters.PlayerW - Parameters.Wall','32 mm','Parameters.PlayerW','Parameters.PlayerL - Parameters.Wall - 32 mm')]
                body=pocket_tray(name+'Body','Parameters.ModuleW','Parameters.PlayerL','Parameters.ModuleBodyH',x,y,z,pockets,
                                name+' - READY SET / 24 cards + car + gear; car fit provisional',color,'ready_player_set')
                body.addProperty('App::PropertyInteger','CardCount','Contents').CardCount=24
                body.addProperty('App::PropertyString','PocketSizes','Contents').PocketSizes='Card60x91; car34x55; gear34x32 mm; height14.6 under lid lip'
                lid(name+'Lid','Parameters.ModuleW','Parameters.PlayerL',x,y,name+' - locating lid',color,
                    z='('+z+') + Parameters.ModuleBodyH',split_x='Parameters.PlayerW - Parameters.Wall',
                    split_y='Parameters.PlayerL - 2 * Parameters.Wall - 32 mm')
                layout.append({'name':name,'x':1+col*(p['ModuleW']+p['Gap']),'y':1+row*(p['PlayerL']+p['Gap']),
                               'z':level*p['ModuleH'],'width':p['ModuleW'],'length':p['PlayerL'],'height':p['ModuleH'],
                               'role':'ready_player_set','level':level,'color':list(color),'cards':24})
    side_x='1 mm + 2 * (Parameters.ModuleW + Parameters.Gap)'
    common_y='1 mm + 2 * (Parameters.PlayerL + Parameters.Gap)'
    common_specs=[
        ('Reserve',side_x,'1 mm','Parameters.PlayerW','Parameters.PlayerL','Reserve / stress24 + heat24 =48','reserve_cards',48),
        ('Sponsor',side_x,'1 mm + Parameters.PlayerL + Parameters.Gap','Parameters.PlayerW','Parameters.PlayerL','Sponsorship / base35 + 7 + 7 =49','sponsor_cards',49),
        ('Other','1 mm + 2 * (Parameters.PlayerW + Parameters.Gap)',common_y,'Parameters.PlayerW','Parameters.CommonL','Legends10 + event18 + track8 =36; one set','other_cards',36)]
    for name,x,y,w,l,label,role,count in common_specs:
        color=(0.24,0.52,0.64)
        body=tray(name+'Body',w,l,'Parameters.BodyH',x,y,'0 mm',1,10,label,color,role)
        body.addProperty('App::PropertyInteger','CardCount','Contents').CardCount=count
        lid(name+'Lid',w,l,x,y,name+' - locating lid',color)
        # Evaluated coordinates from the completed native shape are recorded later.
        layout.append({'name':name,'width':p['PlayerW'],'length':p['PlayerL'] if name!='Other' else p['CommonL'],
                       'height':p['TotalH'],'role':role,'color':list(color),'cards':count,'allocation':label})
    gx='1 mm'
    gy=common_y
    gw='2 * Parameters.PlayerW + Parameters.Gap'
    garage=pocket_tray('GarageBody',gw,'Parameters.CommonL','Parameters.BodyH',gx,gy,'0 mm',
                     [('Parameters.PlayerW - 2 * Parameters.Wall','Parameters.CommonL - 2 * Parameters.Wall','Parameters.Wall','Parameters.Wall'),
                      ('Parameters.PlayerW - 2 * Parameters.Wall','Parameters.CommonL - 2 * Parameters.Wall','Parameters.PlayerW + Parameters.Gap','Parameters.Wall')],
                     'Garage /120 cards; one carrier, 60 cards per bay',(0.18,0.43,0.56),'garage_cards')
    garage.addProperty('App::PropertyInteger','CardCount','Contents').CardCount=120
    # Middle separator has Wall+Gap thickness; skirt clearance covers it completely.
    lid('GarageLid',gw,'Parameters.CommonL',gx,gy,'Garage - one lid',(0.18,0.43,0.56),
        split_x='Parameters.PlayerW - Parameters.Wall')
    layout.append({'name':'Garage','width':2*p['PlayerW']+p['Gap'],'length':p['CommonL'],'height':p['TotalH'],
                   'role':'garage_cards','color':[0.18,0.43,0.56],'cards':120})
    tx='1 mm + 3 * (Parameters.PlayerW + Parameters.Gap)'
    tc=(0.72,0.50,0.22)
    tray('WeatherLower','Parameters.TokenW','Parameters.CommonL','Parameters.LowerH',tx,common_y,'0 mm',2,6,
         'Weather6 / road conditions12 - low serving tray; fit provisional',tc,'weather_road')
    tray('PressUpper','Parameters.TokenW','Parameters.CommonL','Parameters.UpperH',tx,common_y,'Parameters.LowerH',1,6,
         'Press corner standees2 - removable upper tray; fit provisional',tc,'press_standees')
    lid('TokensLid','Parameters.TokenW','Parameters.CommonL',tx,common_y,'Tokens - locating lid',tc)
    layout.append({'name':'Tokens','width':p['TokenW'],'length':p['CommonL'],'height':p['TotalH'],'role':'weather_press','color':list(tc)})
    rx='1 mm + 2 * (Parameters.ModuleW + Parameters.Gap) + Parameters.PlayerW + Parameters.Gap'
    tray('Accessory','Parameters.RailW','Parameters.PlayerRegionL','Parameters.BodyH',rx,'1 mm','0 mm',3,5,
         'Small spare accessories / standee bases; no mandatory component fit claimed',tc,'accessory_spare')
    lid('AccessoryLid','Parameters.RailW','Parameters.PlayerRegionL',rx,'1 mm','Accessory - locating lid',tc,slots=3)
    layout.append({'name':'Accessory','width':p['RailW'],'length':p['PlayerRegionL'],'height':p['TotalH'],'role':'spare','color':list(tc)})
'''
s=s[:a]+new+s[b:]
# Card sample remains at first player's card position and represents the actual measured pack.
s=s.replace("    return doc, parts, lids, refs, p, cells, layout, colors", "    for module in layout:\n        obj=doc.getObject(module['name']+'Body') or doc.getObject(module['name']+'Lower') or doc.getObject(module['name'])\n        if obj is None and module['name']=='Tokens': obj=doc.WeatherLower\n        bounds=obj.Shape.BoundBox\n        module['x'],module['y'],module['z']=bounds.XMin,bounds.YMin,bounds.ZMin\n    return doc, parts, lids, refs, p, cells, layout, colors")
a=s.index("    unique =");b=s.index('    stls =',a)
s=s[:a]+"    unique = [('P01Body',8),('P01Lid',8),('ReserveBody',1),('ReserveLid',1),('SponsorBody',1),('SponsorLid',1),('OtherBody',1),('OtherLid',1),('GarageBody',1),('GarageLid',1),('WeatherLower',1),('PressUpper',1),('TokensLid',1),('Accessory',1),('AccessoryLid',1)]\n"+s[b:]
s=s.replace("'Two track expansions add one player each: 8 player modules.'", "'Two track expansions add one player each: 8 ready modules stacked in four pairs.'")
s=s.replace("'player_card_usable_depth': p['LowerH'] - p['Base']", "'player_card_usable_depth': p['ModuleBodyH'] - p['Base'] - p['LipD']")
s=s.replace("'player_upper_clear_height_under_lip': p['UpperH'] - p['Base'] - p['LipD']", "'player_upper_clear_height_under_lip': p['ModuleBodyH'] - p['Base'] - p['LipD']")
s=s.replace("'Car/gear/standee/token and scorepad dimensions unmeasured; all-component fit unverified.'", "'Car pocket34x55x14.6 and gear34x32x14.6 are provisional; car/gear actual dimensions unmeasured.'")
s=s.replace("'status': 'draft_not_physical_fit_verified'", "'version':'0.3_reference_redesign', 'reference_videos':['https://youtu.be/xePYRwZCSzQ','https://youtube.com/shorts/PnYFqH4tk2Y'], 'status': 'draft_not_physical_fit_verified'")
(root/'HeatOrganizerReferenceDraft.FCMacro').write_text(s,encoding='utf-8')
