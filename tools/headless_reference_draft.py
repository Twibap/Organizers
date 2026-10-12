from pathlib import Path
import json, math, os, runpy, traceback
import FreeCAD as App
import Part, Mesh
root=Path(os.environ['ORGANIZER_PROJECT_ROOT'])
report={'passed':False}
output=None
try:
    scope=runpy.run_path(str(root/'HeatOrganizerReferenceDraft.FCMacro'))
    doc,parts,output,p=scope['draft_document'],scope['draft_parts'],scope['draft_output'],scope['draft_parameters']
    assert len(parts)==29,len(parts)
    for obj in parts:
        assert obj.Shape.isValid() and len(obj.Shape.Solids)==1,obj.Name
        b=obj.Shape.BoundBox
        assert b.XMin>=1-1e-6 and b.YMin>=1-1e-6 and b.ZMin>=-1e-6,obj.Name
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
    # Check actual proxy solids for all 8 measured card packs and each shared deck stack.
    proxies=[]
    for index in range(1,9):
        obj=doc.getObject('P%02dBody'%index)
        b=obj.Shape.BoundBox
        proxies.append((obj,Part.makeBox(58,89,9,App.Vector(b.XMin+3,b.YMin+3,b.ZMin+2))))
        assert b.ZMin+2+9<=b.ZMax-p['LipD']-1
    for name,count in [('ReserveBody',48),('SponsorBody',49),('OtherBody',36),('GarageBody',60)]:
        obj=doc.getObject(name);b=obj.Shape.BoundBox
        card=Part.makeBox(58,89,count*p['CardPitch'],App.Vector(b.XMin+3,b.YMin+3,2))
        proxies.append((obj,card))
        assert 2+count*p['CardPitch']+1 <= p['BodyH']-p['LipD'],name
        if name=='GarageBody':
            second=Part.makeBox(58,89,count*p['CardPitch'],App.Vector(b.XMin+(2*p['PlayerW']+p['Gap']+p['Wall'])/2+1,b.YMin+3,2))
            proxies.append((obj,second))
    for obj,card in proxies:
        assert obj.Shape.common(card).Volume<1e-6,obj.Name
    manifest=json.loads((output/'manifest.json').read_text())
    assert sum(f['quantity'] for f in manifest['stl_files'])==29
    for f in manifest['stl_files']:
        mesh=Mesh.Mesh(str(output/f['file']))
        assert mesh.isSolid(),f['file']
    step=Part.Shape();step.read(str(output/'HeatOrganizerDraft-assembled.step'))
    assert step.isValid() and len(step.Solids)==29
    App.closeDocument(doc.Name)
    reopened=App.openDocument(str(output/'HeatOrganizerDraft.FCStd'));reopened.recompute()
    assert len(reopened.OrganizerParts.Group)==29
    cell=scope['draft_cells']['SleeveW']
    reopened.Parameters.set(cell,'58.5 mm');reopened.recompute()
    assert math.isclose(reopened.P01Body.Shape.BoundBox.XLength,100.5,abs_tol=1e-6)
    assert math.isclose(reopened.Accessory.Shape.BoundBox.XLength,20.1,abs_tol=1e-6)
    assert all(o.Shape.isValid() for o in reopened.OrganizerParts.Group)
    App.closeDocument(reopened.Name)
    report.update(passed=True,valid_solids=29,envelope_mm=[288,288,38],part_collisions=0,overlap_pairs=checked,
                  measured_card_proxies_fit=len(proxies),stl_closed=True,step_valid=True,fcstd_reopened=True,parameter_recomputed=True,
                  car_gear_tokens_physical_fit='unverified',output_directory=str(output))
except BaseException:
    report['error']=traceback.format_exc()
    traceback.print_exc()
if output: (output/'draft-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
import sys
sys.stdout.flush()
os._exit(0 if report['passed'] else 1)
