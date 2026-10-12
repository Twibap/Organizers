from pathlib import Path
f=Path('HeatOrganizerReferenceDraft.FCMacro');s=f.read_text();a=s.index("    garage=pocket_tray(");b=s.index("    layout.append({'name':'Garage'",a)
s=s[:a]+'''    garage=pocket_tray('GarageBody',gw,'Parameters.CommonL','Parameters.BodyH',gx,gy,'0 mm',
                     [('(2 * Parameters.PlayerW + Parameters.Gap - 3 * Parameters.Wall) / 2','Parameters.CommonL - 2 * Parameters.Wall','Parameters.Wall','Parameters.Wall'),
                      ('(2 * Parameters.PlayerW + Parameters.Gap - 3 * Parameters.Wall) / 2','Parameters.CommonL - 2 * Parameters.Wall','(2 * Parameters.PlayerW + Parameters.Gap + Parameters.Wall) / 2','Parameters.Wall')],
                     'Garage /120 cards; one carrier, 60 cards per bay',(0.18,0.43,0.56),'garage_cards')
    garage.addProperty('App::PropertyInteger','CardCount','Contents').CardCount=120
    lid('GarageLid',gw,'Parameters.CommonL',gx,gy,'Garage - one lid',(0.18,0.43,0.56),
        split_x='(2 * Parameters.PlayerW + Parameters.Gap - Parameters.Wall) / 2')
''' +s[b:]
f.write_text(s,encoding='utf-8')
f=Path('tools/headless_reference_draft.py');s=f.read_text(encoding='utf-8-sig').replace("b.XMin+p['PlayerW']+p['Gap']+1","b.XMin+(2*p['PlayerW']+p['Gap']+p['Wall'])/2+1")
f.write_text(s,encoding='utf-8')
