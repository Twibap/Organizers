"""FreeCADCmd entry point: generate draft and verify real solids and exports."""
from pathlib import Path
import json
import math
import os
import runpy
import sys
import traceback
import FreeCAD as App
import Mesh
import Part

root = Path(os.environ['ORGANIZER_PROJECT_ROOT'])
report = {'passed': False}
output = None
exit_code = 1
try:
    scope = runpy.run_path(str(root / 'HeatOrganizerDraft.FCMacro'))
    doc, parts, output = scope['draft_document'], scope['draft_parts'], scope['draft_output']
    p = scope['draft_parameters']
    for obj in parts:
        assert obj.Shape.isValid() and len(obj.Shape.Solids) == 1, obj.Name
        bb = obj.Shape.BoundBox
        assert bb.XMin >= 1 - 1e-6 and bb.YMin >= 1 - 1e-6 and bb.ZMin >= -1e-6, obj.Name
        assert bb.XMax <= 289 + 1e-6 and bb.YMax <= 289 + 1e-6 and bb.ZMax <= p['TotalH'] + 1e-6, obj.Name
    checks = 0
    for index, first in enumerate(parts):
        a = first.Shape.BoundBox
        for second in parts[index + 1:]:
            b = second.Shape.BoundBox
            if min(a.XMax, b.XMax) - max(a.XMin, b.XMin) <= 1e-6 or min(a.YMax, b.YMax) - max(a.YMin, b.YMin) <= 1e-6 or min(a.ZMax, b.ZMax) - max(a.ZMin, b.ZMin) <= 1e-6:
                continue
            overlap = first.Shape.common(second.Shape).Volume
            assert overlap < 1e-6, (first.Name, second.Name, overlap)
            checks += 1
    card = doc.getObject('SleevedCardSample24').Shape
    assert doc.getObject('P01Lower').Shape.common(card).Volume < 1e-6
    assert card.BoundBox.ZMax <= p['LowerH'] - 1, 'Sample cards touch upper tray'
    report['geometry'] = {'valid_solids': len(parts), 'organizer_envelope_mm': [p['Span'], p['Span'], p['TotalH']],
                          'overlapping_bounds_pairs_checked': checks, 'part_collisions': 0, 'sample_cards_fit': True}
    manifest = json.loads((output / 'manifest.json').read_text(encoding='utf-8'))
    stl_checks = []
    for item in manifest['stl_files']:
        mesh = Mesh.Mesh(str(output / item['file']))
        assert mesh.CountFacets > 0 and mesh.isSolid(), item['file']
        assert math.isclose(abs(mesh.Volume), item['volume_mm3'], rel_tol=0.003), item['file']
        stl_checks.append({'file': item['file'], 'closed': True, 'facets': mesh.CountFacets})
    report['stl'] = stl_checks
    shape = Part.Shape()
    shape.read(str(output / 'HeatOrganizerDraft-assembled.step'))
    assert shape.isValid() and len(shape.Solids) == len(parts)
    assert math.isclose(shape.Volume, sum(obj.Shape.Volume for obj in parts), rel_tol=1e-5)
    report['step'] = {'valid': True, 'solids': len(shape.Solids)}
    cad_path = output / 'HeatOrganizerDraft.FCStd'
    App.closeDocument(doc.Name)
    reopened = App.openDocument(str(cad_path))
    reopened.recompute()
    assert len(reopened.OrganizerParts.Group) == 34
    sleeve_cell = scope['draft_cells']['SleeveW']
    reopened.Parameters.set(sleeve_cell, str(p['SleeveW'] + 0.5) + ' mm')
    reopened.recompute()
    assert math.isclose(reopened.P01Lower.Shape.BoundBox.XLength, p['PlayerW'] + 0.5, abs_tol=1e-6)
    assert math.isclose(reopened.Rail01.Shape.BoundBox.XLength, p['RailW'] - 2, abs_tol=1e-6)
    reopened.Parameters.set(sleeve_cell, str(p['SleeveW']) + ' mm')
    reopened.recompute()
    assert math.isclose(reopened.P01Lower.Shape.BoundBox.XLength, p['PlayerW'], abs_tol=1e-6)
    assert all(obj.Shape.isValid() for obj in reopened.OrganizerParts.Group)
    App.closeDocument(reopened.Name)
    assert 48 * p['CardPitch'] + 1 <= p['BodyH'] - p['Base'] - p['LipD']
    assert 60 * p['CardPitch'] + 1 <= p['BodyH'] - p['Base'] - p['LipD']
    assert 85 * p['CardPitch'] + 1 <= p['BodyH'] - p['Base'] - p['LipD']
    assert 2 * (p['SleeveW'] + 2*p['EdgeClear']) <= 2*p['PlayerW'] + p['Gap'] - 2*p['Wall']
    report['allocation'] = {'player_sets': 8, 'player_cards_each': 24, 'reserve_cards': 48, 'garage_cards': 120, 'garage_stacks': [60,60], 'championship_and_sponsor_cards': 85, 'estimated_card_clearance_passed': True}
    report['fcstd'] = {'reopened': True, 'sleeve_parameter_recomputed': True}
    report['passed'], exit_code = True, 0
    report['output_directory'] = str(output)
except BaseException:
    report['error'] = traceback.format_exc()
    traceback.print_exc()
finally:
    (output or root).joinpath('draft-verification.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(exit_code)
