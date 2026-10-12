"""Save FreeCAD view providers without opening a visible application window."""
from pathlib import Path
import json
import os
import sys
import traceback
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import FreeCAD as App
import FreeCADGui as Gui
import Part
Gui.setupWithoutGUI()
output = Path(os.environ['ORGANIZER_DRAFT_OUTPUT'])
manifest = json.loads((output / 'manifest.json').read_text(encoding='utf-8'))
report = {'saved': False}
try:
    doc = App.openDocument(str(output / 'HeatOrganizerDraft.FCStd'))
    doc.recompute()
    final_names = {obj.Name for obj in doc.OrganizerParts.Group}
    palette = {}
    for module in manifest['layout']:
        color = tuple(module['color'])
        name = module['name']
        for suffix in ('Lower', 'Upper', 'Body', 'Lid', ''):
            palette[name + suffix] = color
    for obj in doc.Objects:
        if obj.ViewObject is None:
            continue
        obj.ViewObject.Visibility = obj.Name in final_names and not obj.Name.endswith('Lid')
        if obj.Name in final_names:
            obj.ViewObject.ShapeColor = palette.get(obj.Name, (0.35, 0.52, 0.60))
            obj.ViewObject.LineColor = (0.12, 0.15, 0.18)
            obj.ViewObject.DisplayMode = 'Flat Lines'
    doc.OrganizerParts.ViewObject.Visibility = True
    doc.Construction.ViewObject.Visibility = False
    doc.References.ViewObject.Visibility = False
    assert all(obj.Shape.isValid() for obj in doc.OrganizerParts.Group)
    doc.save()
    App.closeDocument(doc.Name)
    import zipfile
    with zipfile.ZipFile(output / 'HeatOrganizerDraft.FCStd') as archive:
        report['gui_document_present'] = 'GuiDocument.xml' in archive.namelist()
    assert report['gui_document_present'], 'GUI visibility was not saved'
    report['saved'] = True
    (output / 'view-verification.json').write_text(json.dumps(report), encoding='utf-8')
    print(json.dumps(report))
    sys.stdout.flush()
    os._exit(0)
except BaseException:
    report['error'] = traceback.format_exc()
    (output / 'view-verification.json').write_text(json.dumps(report), encoding='utf-8')
    traceback.print_exc()
    sys.stderr.flush()
    os._exit(1)
