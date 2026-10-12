from pathlib import Path
import json
root=Path(r'C:\Users\Twibap\Workspace\Organizers')
p=root/'heat-measurements.json';m=json.loads(p.read_text(encoding='utf-8-sig'))
m['scoreboard']={'width':100,'length':60,'measured_total_stack_height':7,'design_maximum_stack_height':10,'scope':'entire stored bundle','status':'user_measured; design capacity10mm explicitly requested'}
m['gear_pawn']['storage_orientation']='horizontal'
m['provisional_layout']['scorepads_note']='Measured whole scoreboard bundle100x60x7mm stored in dedicated lower tray; capacity10mm. Removed from upper flat-stack allocation.'
p.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
s=(root/'HeatOrganizerCDraft.FCMacro').read_text(encoding='utf-8-sig')
start=s.index('    # Instructions C principle:')
end=s.index('    refs = [box(',start)
s=s[:start]+'''    import sys
    sys.path.insert(0,str(PROJECT_ROOT/'tools'))
    import compact_car_tray
    compact=compact_car_tray.build_compact(doc,construction,final_group,component_group,MEASUREMENTS,tx,'1 mm',True)
    parts.extend(compact['parts']);lids.extend(compact['lids']);colors.update(compact['colors'])
    doc.CarGearBody.addProperty('App::PropertyString','CompactParametersJSON','Draft').CompactParametersJSON=json.dumps(compact['parameters'])
    layout.append({'name':'CarGear','width':compact['parameters']['OuterL'],'length':compact['parameters']['OuterW'],
                   'height':compact['parameters']['TotalH'],'role':'compact_car_gear_scoreboard','color':[0.31,0.38,0.44],
                   'cars':8,'gears':8,'scoreboard_maximum_height':10})
'''+s[end:]
start=s.index('    for idx,gx,gy in gear_centres:')
end=s.index('    for ref in refs:',start)
s=s[:start]+s[end:]
s=s.replace("    doc.recompute()\n    if App.GuiUp:","    refs.extend(compact['refs'])\n    doc.recompute()\n    if App.GuiUp:")
# Remove the superseded carrier dimensions from the main card-organization sheet.
lines=s.splitlines(True)
s=''.join(line for line in lines if not any(word in line for word in ["('CarW', MEASUREMENTS", "('GearD', MEASUREMENTS", "('DrawerClear', 0.4)", "('DeckTop', '=DeckBottom", "('GearWellD', '=GearD", "('CarWellW', '=CarW", "('BayW', '=(TokenW", "('DrawerH', '=DeckBottom"]))
s=s.replace('31 pieces / Instructions C redesign v0.4','30 pieces / compact car + scoreboard v0.5')
s=s.replace("('CarGearBody',1),('CarGearFrame',1),('CarGearLid',1),('CarGearDrawer',1)","('CarGearBody',1),('CarScoreTray',1),('CarGearLid',1)")
s=s.replace("if not obj.Name.startswith(('CarSample','GearSample')): continue", "if not obj.Name.startswith(('CarSample','GearSample','ScoreboardSample')): continue")
s=s.replace("        index=int(obj.Name[-2:])-1", "        index=0 if obj.Name=='ScoreboardSample' else int(obj.Name[-2:])-1")
s=s.replace("'color':list([(0.78", "'color':([0.65,0.64,0.55] if obj.Name=='ScoreboardSample' else list([(0.78")
s=s.replace("(0.52,0.32,0.65)][index]),", "(0.52,0.32,0.65)][index])),")
s=s.replace("'version':'0.4_instructions_C_redesign'", "'version':'0.5_compact_car_scoreboard'")
start=s.index("                'gear_seat':")
end=s.index("                'maximum_print_part_xy':",start)
s=s[:start]+'''                'compact_car_tray':json.loads(doc.CarGearBody.CompactParametersJSON),
                'carrier_assembly_retention':'Two removable stacked trays with alignment keys; physical retention unverified.',
'''+s[end:]
s=s.replace("'Measured car11x23x7 and gear baseD15/H25. Entire gear assumed within D15 cylinder; actual upper profile unmeasured.'", "'Measured car11x23x7 and gear baseD15/H25; lying horizontally. Whole gear assumed within D15 cylinder.'")
s=s.replace("'Instructions C inspired two-column car/gear carrier and lower pull-out tray. Drawer usable5mm, contents physical fit unmeasured.'", "'Compact 4-column x2-row car/gear tray above100x60x10 maximum scoreboard bundle. Measured whole bundle7mm.'")
s=s.replace("'Scorepads require measured storage allocation; add thickness to upper stack if stored above trays.'", "'Scoreboard bundle7mm measured, stored below cars; removed from upper flat-stack allocation.'")
(root/'HeatOrganizerCompactDraft.FCMacro').write_text(s,encoding='utf-8')
a=json.loads((root/'heat-component-allocation.json').read_text(encoding='utf-8-sig'));a['version']='0.5'
a['car_gear_carrier']={'cars':8,'gears':8,'outer_mm':[110.8,64.8,30.2],'placement_world_mm':[64.8,110.8],'arrangement':'4 columns x2 rows; gears lying horizontally','lower_storage':'Scoreboard whole bundle100x60x7 measured, maximum10mm capacity','parts':['CarScoreTray','CarGearBody','CarGearLid']}
a['flat_stack']['scorepads']=0;a['flat_stack']['scorepad_storage']='Moved to CarScoreTray; whole stored bundle7mm measured.'
a['flat_stack']['status']='map thickness estimated50; base mats/rules4; expansion mats/rules unmeasured; scoreboard stored separately'
(root/'heat-component-allocation.json').write_text(json.dumps(a,ensure_ascii=False,indent=2),encoding='utf-8')
print('V0.5 source, whole-bundle measurement, and allocation updated')
