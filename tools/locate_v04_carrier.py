from pathlib import Path
p=Path(r'C:\Users\Twibap\Workspace\Organizers\HeatOrganizerCDraft.FCMacro')
s=p.read_text(encoding='utf-8')
old="""    body=feature('CarGearBody','Part::Common',complete,upper_plane)
    frame=feature('CarGearFrame','Part::Common',complete,lower_plane)
    finish(frame,'C - lower frame / print separately; assembly retention unverified',(0.31,0.38,0.44),'car_gear_lower_frame')"""
new="""    body=feature('CarGearUpperSplit','Part::Common',complete,upper_plane)
    frame_base=feature('CarGearLowerSplit','Part::Common',complete,lower_plane)
    keys=[]
    for side in range(2):
        for end in range(2):
            key_index=side*2+end
            kx='('+cx+') + %d * (Parameters.TokenW - Parameters.Wall)'%side
            ky='('+cy+') + '+('8 mm' if end==0 else 'Parameters.PlayerRegionL - 12 mm')
            keys.append(box('CarGearLocator'+str(key_index),'Parameters.Wall','4 mm','1.5 mm',kx,ky,'Parameters.DeckBottom'))
            gap=box('CarGearLocatorGap'+str(key_index),'Parameters.Wall + 0.4 mm','4.4 mm','1.7 mm',
                    '('+kx+') - 0.2 mm','('+ky+') - 0.2 mm','Parameters.DeckBottom')
            body=feature('CarGearBody' if key_index==3 else 'CarGearLocatorFit'+str(key_index),'Part::Cut',body,gap)
    frame=doc.addObject('Part::MultiFuse','CarGearFrame')
    frame.Shapes,frame.Refine=[frame_base]+keys,True
    construction.addObject(frame)
    finish(frame,'C - lower frame / 4 locating keys; assembly retention unverified',(0.31,0.38,0.44),'car_gear_lower_frame')"""
assert old in s;s=s.replace(old,new)
s=s.replace("'carrier_assembly_retention':'Upper deck and frame separate; physical assembly retention unverified.'", "'carrier_assembly_retention':'Upper deck and frame separate; 4 alignment keys with0.2mm side clearance. Lift upper car tray independently; retention unverified.'")
p.write_text(s,encoding='utf-8')
print('four locating keys added; car deck lifts independently')
