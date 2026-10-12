from pathlib import Path
import json,os
import FreeCAD as App
import Part
root=Path(r'C:\Users\Twibap\Workspace\Organizers');folder=Path((root/'output/latest-heat-draft.txt').read_text().strip())
doc=App.openDocument(str(folder/'HeatOrganizerReview.FCStd'))
checked=[]
for i in range(1,9):
    obj=doc.getObject('P%02dBody'%i);b=obj.Shape.BoundBox
    proxy=Part.makeBox(11,23,7,App.Vector(b.XMin+66,b.YMin+4,b.ZMin+2))
    assert all(part.Shape.common(proxy).Volume<1e-6 for part in doc.OrganizerParts.Group),obj.Name
    assert proxy.BoundBox.ZMax<=b.ZMax-.8-1
    checked.append(obj.Name)
report={'nominal_car_mm':[11,23,7],'player_car_compartments_checked':checked,'bounding_box_proxies_fit':True,'actual_print_fit_test':False}
(folder/'car-fit-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
App.closeDocument(doc.Name)
import sys
sys.stdout.flush();os._exit(0)
