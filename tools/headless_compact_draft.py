from pathlib import Path
import json,math,os,runpy,traceback
import FreeCAD as App
import Part,Mesh
root=Path(os.environ['ORGANIZER_PROJECT_ROOT']);report={'passed':False};output=None
try:
    scope=runpy.run_path(str(root/'HeatOrganizerCompactDraft.FCMacro'))
    doc,parts,output,p=scope['draft_document'],scope['draft_parts'],scope['draft_output'],scope['draft_parameters']
    c=json.loads(doc.CarGearBody.CompactParametersJSON)
    assert len(parts)==30,len(parts)
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
            if min(a.XMax,b.XMax)-max(a.XMin,b.XMin)<=1e-6 or min(a.YMax,b.YMax)-max(a.YMin,b.YMin)<=1e-6 or min(a.ZMax,b.ZMax)-max(a.ZMin,b.ZMin)<=1e-6:continue
            volume=one.Shape.common(two.Shape).Volume
            assert volume<1e-6,(one.Name,two.Name,volume);checked+=1
    proxies=[]
    for idx in range(1,9):
        b=doc.getObject('P%02dBody'%idx).Shape.BoundBox
        proxies.append(('Player%02dCards'%idx,Part.makeBox(58,89,9,App.Vector(b.XMin+3,b.YMin+3,b.ZMin+2))))
    for name,count in [('ReserveBody',48),('SponsorBody',49),('OtherBody',36),('GarageBody',60)]:
        b=doc.getObject(name).Shape.BoundBox
        proxies.append((name,Part.makeBox(58,89,count*p['CardPitch'],App.Vector(b.XMin+3,b.YMin+3,2))))
        if name=='GarageBody':proxies.append(('GarageSecond',Part.makeBox(58,89,count*p['CardPitch'],App.Vector(b.XMin+(2*p['PlayerW']+p['Gap']+p['Wall'])/2+1,b.YMin+3,2))))
    card_count=len(proxies)
    for sample in doc.ComponentSamples.Group:proxies.append((sample.Name,sample.Shape))
    assert len(doc.ComponentSamples.Group)==17
    for name,shape in proxies:
        for obj in parts:
            v=shape.common(obj.Shape).Volume
            assert v<1e-6,(name,obj.Name,v)
    for i,(name,shape) in enumerate(proxies):
        for name2,shape2 in proxies[i+1:]:assert shape.common(shape2).Volume<1e-6,(name,name2)
    assert math.isclose(c['OuterW'],110.8,abs_tol=1e-6)
    assert math.isclose(c['OuterL'],64.8,abs_tol=1e-6)
    assert math.isclose(c['TotalH'],30.2,abs_tol=1e-6)
    assert math.isclose(c['LidZ']-c['SeatFloor']-c['GearD'],1,abs_tol=1e-6)
    assert math.isclose(c['LowerH']-c['Floor']-c['BoardCap'],0.6,abs_tol=1e-6)
    b=doc.CarGearBody.Shape.BoundBox
    assert math.isclose(b.XLength,64.8,abs_tol=1e-6) and math.isclose(b.YLength,110.8,abs_tol=1e-6)
    score=doc.ScoreboardSample.Shape.BoundBox
    assert math.isclose(score.XLength,60,abs_tol=1e-6) and math.isclose(score.YLength,100,abs_tol=1e-6) and math.isclose(score.ZLength,10,abs_tol=1e-6)
    for rise in [1.5,5,20]:
        shape=doc.CarGearBody.Shape.copy();shape.translate(App.Vector(0,0,rise))
        assert shape.common(doc.CarScoreTray.Shape).Volume<1e-6,('upper tray lift',rise)
    manifest=json.loads((output/'manifest.json').read_text())
    assert sum(f['quantity'] for f in manifest['stl_files'])==30
    for f in manifest['stl_files']:assert Mesh.Mesh(str(output/f['file'])).isSolid(),f['file']
    step=Part.Shape();step.read(str(output/'HeatOrganizerDraft-assembled.step'))
    assert step.isValid() and len(step.Solids)==30
    App.closeDocument(doc.Name)
    d=App.openDocument(str(output/'HeatOrganizerDraft.FCStd'));d.recompute()
    assert len(d.OrganizerParts.Group)==30
    d.Parameters.set(scope['draft_cells']['SleeveW'],'58.5 mm');d.recompute()
    assert math.isclose(d.P01Body.Shape.BoundBox.XLength,64.5,abs_tol=1e-6)
    assert math.isclose(d.CarGearBody.Shape.BoundBox.XLength,64.8,abs_tol=1e-6)
    # Capacity is editable; one extra mm raises the upper tray and cover by one mm.
    cell=next('B'+str(i) for i in range(2,50) if d.CompactParameters.get('A'+str(i))=='BoardCap')
    d.CompactParameters.set(cell,'11 mm');d.recompute()
    assert math.isclose(d.CarGearLid.Shape.BoundBox.ZMax,31.2,abs_tol=1e-6)
    assert all(o.Shape.isValid() for o in d.OrganizerParts.Group)
    App.closeDocument(d.Name)
    old=93.6*190.8*38;new=110.8*64.8*30.2
    report.update(passed=True,valid_solids=30,part_collisions=0,overlap_pairs=checked,envelope_mm=[288,288,38],
                  compact_car_tray_mm=[110.8,64.8,30.2],compact_volume_cm3=new/1000,volume_reduction_percent=100*(1-new/old),
                  card_proxies_fit=card_count,car_proxies_fit=8,lying_gear_cylinders_fit=8,scoreboard_maximum_proxy_mm=[100,60,10],
                  measured_scoreboard_bundle_mm=[100,60,7],gear_top_clearance_mm=1,scoreboard_top_clearance_at10mm=0.6,
                  upper_tray_lift_checked=True,stl_closed=True,step_valid=True,fcstd_reopened=True,parameters_recomputed=True,
                  physical_fit='unverified',gear_profile_assumption='Entire gear within measured baseD15 cylinder',output_directory=str(output))
except BaseException:
    report['error']=traceback.format_exc();traceback.print_exc()
if output:(output/'draft-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
import sys
sys.stdout.flush();os._exit(0 if report['passed'] else 1)
