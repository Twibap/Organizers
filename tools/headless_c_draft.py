from pathlib import Path
import json,math,os,runpy,traceback
import FreeCAD as App
import Part,Mesh
root=Path(os.environ['ORGANIZER_PROJECT_ROOT'])
report={'passed':False}
output=None
try:
    scope=runpy.run_path(str(root/'HeatOrganizerCDraft.FCMacro'))
    doc,parts,output,p=scope['draft_document'],scope['draft_parts'],scope['draft_output'],scope['draft_parameters']
    assert len(parts)==31,len(parts)
    for obj in parts:
        assert obj.Shape.isValid() and len(obj.Shape.Solids)==1,(obj.Name,obj.Shape.isValid(),len(obj.Shape.Solids))
        b=obj.Shape.BoundBox
        assert b.XMin>=1-1e-6 and b.YMin>=1-1e-6 and b.ZMin>=-1e-6,(obj.Name,str(b))
        assert b.XMax<=289+1e-6 and b.YMax<=289+1e-6 and b.ZMax<=38+1e-6,(obj.Name,str(b))
    checked=0
    for i,one in enumerate(parts):
        a=one.Shape.BoundBox
        for two in parts[i+1:]:
            b=two.Shape.BoundBox
            if min(a.XMax,b.XMax)-max(a.XMin,b.XMin)<=1e-6 or min(a.YMax,b.YMax)-max(a.YMin,b.YMin)<=1e-6 or min(a.ZMax,b.ZMax)-max(a.ZMin,b.ZMin)<=1e-6: continue
            overlap=one.Shape.common(two.Shape).Volume
            assert overlap<1e-6,(one.Name,two.Name,overlap)
            checked+=1
    proxies=[]
    for index in range(1,9):
        obj=doc.getObject('P%02dBody'%index);b=obj.Shape.BoundBox
        proxies.append(('Player%02dCards'%index,Part.makeBox(58,89,9,App.Vector(b.XMin+3,b.YMin+3,b.ZMin+2))))
        assert b.ZMin+2+9<=b.ZMax-p['LipD']-1
    for name,count in [('ReserveBody',48),('SponsorBody',49),('OtherBody',36),('GarageBody',60)]:
        obj=doc.getObject(name);b=obj.Shape.BoundBox
        proxies.append((name,Part.makeBox(58,89,count*p['CardPitch'],App.Vector(b.XMin+3,b.YMin+3,2))))
        assert 2+count*p['CardPitch']+1 <= p['BodyH']-p['LipD'],name
        if name=='GarageBody':
            proxies.append(('GarageSecondStack',Part.makeBox(58,89,count*p['CardPitch'],App.Vector(b.XMin+(2*p['PlayerW']+p['Gap']+p['Wall'])/2+1,b.YMin+3,2))))
    measured_cards=len(proxies)
    for idx in range(1,9):
        for kind in ['Car','Gear']:
            ref=doc.getObject('%sSampleP%02d'%(kind,idx))
            assert ref.Shape.isValid(),ref.Name
            proxies.append((ref.Name,ref.Shape))
    for name,shape in proxies:
        for part in parts:
            assert part.Shape.common(shape).Volume<1e-6,(name,part.Name,part.Shape.common(shape).Volume)
    for idx,(name,one) in enumerate(proxies):
        for name2,two in proxies[idx+1:]:
            assert one.common(two).Volume<1e-6,(name,name2)
    assert math.isclose(p['BodyH']-p['GearFloor']-p['GearH'],1.2,abs_tol=1e-6)
    assert math.isclose(p['GearFloor']-p['DeckBottom'],1.2,abs_tol=1e-6)
    assert math.isclose(p['DrawerH']-p['DrawerBase'],5,abs_tol=1e-6)
    d=doc.CarGearDrawer.Shape.BoundBox;c=doc.CarGearBody.Shape.BoundBox
    assert math.isclose(c.YMax-p['Wall']-d.YMax,p['DrawerClear'],abs_tol=1e-6)
    assert math.isclose(p['DeckBottom']-d.ZMax,p['DrawerClear'],abs_tol=1e-6)
    # Pull the separate drawer straight out; no part of its motion may cross the carrier.
    for distance in [2,10,30,90,190]:
        shape=doc.CarGearDrawer.Shape.copy();shape.translate(App.Vector(0,-distance,0))
        for carrier in [doc.CarGearBody,doc.CarGearFrame]:
            assert shape.common(carrier.Shape).Volume<1e-6,('drawer travel',carrier.Name,distance)
    manifest=json.loads((output/'manifest.json').read_text())
    assert sum(f['quantity'] for f in manifest['stl_files'])==31
    for f in manifest['stl_files']:
        assert Mesh.Mesh(str(output/f['file'])).isSolid(),f['file']
    step=Part.Shape();step.read(str(output/'HeatOrganizerDraft-assembled.step'))
    assert step.isValid() and len(step.Solids)==31
    App.closeDocument(doc.Name)
    reopened=App.openDocument(str(output/'HeatOrganizerDraft.FCStd'));reopened.recompute()
    assert len(reopened.OrganizerParts.Group)==31
    reopened.Parameters.set(scope['draft_cells']['SleeveW'],'58.5 mm');reopened.recompute()
    assert math.isclose(reopened.P01Body.Shape.BoundBox.XLength,64.5,abs_tol=1e-6)
    assert math.isclose(reopened.CarGearBody.Shape.BoundBox.XLength,92.1,abs_tol=1e-6)
    assert all(o.Shape.isValid() for o in reopened.OrganizerParts.Group)
    App.closeDocument(reopened.Name)
    report.update(passed=True,valid_solids=31,envelope_mm=[288,288,38],part_collisions=0,overlap_pairs=checked,
                  measured_card_proxies_fit=measured_cards,measured_car_proxies_fit=8,nominal_gear_cylinders_fit=8,
                  gear_top_clearance_mm=1.2,gear_socket_floor_thickness_mm=1.2,lower_drawer_usable_height_mm=5,
                  drawer_motion_checked=True,carrier_split_for_printing=True,drawer_back_and_top_clearance_mm=0.4,
                  stl_closed=True,step_valid=True,fcstd_reopened=True,parameter_recomputed=True,
                  physical_fit='unverified',gear_assumption='baseD15 measured; whole piece assumed within D15 cylinder',
                  output_directory=str(output))
except BaseException:
    report['error']=traceback.format_exc();traceback.print_exc()
if output: (output/'draft-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
import sys
sys.stdout.flush()
os._exit(0 if report['passed'] else 1)
