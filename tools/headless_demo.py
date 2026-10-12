"""Run with FreeCADCmd, whose script loader imports this file as a module."""
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

project_root = Path(os.environ["ORGANIZER_PROJECT_ROOT"])
report = {"passed": False}
exit_code = 1
output = None
try:
    scope = runpy.run_path(str(project_root / "HeatOrganizerDemo.FCMacro"))
    doc, tray = scope["demo_document"], scope["demo_tray"]
    output, p = scope["demo_output"], scope["DEMO_PARAMETERS"]
    bounds = tray.Shape.BoundBox
    for actual, expected in zip((bounds.XLength, bounds.YLength, bounds.ZLength),
                               (p["length"], p["width"], p["height"])):
        assert math.isclose(actual, expected, abs_tol=1e-6), (actual, expected)
    expected_volume = (p["length"] * p["width"] * p["height"]
                       - (p["length"] - (p["compartments"] + 1) * p["wall"])
                       * (p["width"] - 2 * p["wall"]) * (p["height"] - p["base"]))
    assert math.isclose(tray.Shape.Volume, expected_volume, abs_tol=1e-5)
    report["geometry"] = {"valid": tray.Shape.isValid(), "solids": len(tray.Shape.Solids),
                          "volume_mm3": tray.Shape.Volume,
                          "outer_size_mm": [bounds.XLength, bounds.YLength, bounds.ZLength]}
    if os.environ.get("ORGANIZER_VERIFY") == "1":
        stl_mesh = Mesh.Mesh(str(output / "HeatOrganizerDemo.stl"))
        assert stl_mesh.CountFacets > 0
        assert stl_mesh.isSolid(), "Exported STL is not closed"
        report["stl"] = {"facets": stl_mesh.CountFacets, "closed": stl_mesh.isSolid()}
        step_shape = Part.Shape()
        step_shape.read(str(output / "HeatOrganizerDemo.step"))
        assert step_shape.isValid() and len(step_shape.Solids) == 1
        assert math.isclose(step_shape.Volume, expected_volume, abs_tol=1e-3)
        report["step"] = {"valid": step_shape.isValid(), "solids": len(step_shape.Solids)}
        App.closeDocument(doc.Name)
        reopened = App.openDocument(str(output / "HeatOrganizerDemo.FCStd"))
        reopened.recompute()
        assert reopened.Tray.Shape.isValid()
        assert math.isclose(reopened.Tray.Shape.Volume, expected_volume, abs_tol=1e-5)
        reopened.Parameters.set("B3", str(p["width"] + 5) + " mm")
        reopened.recompute()
        assert reopened.Tray.Shape.isValid()
        assert math.isclose(reopened.Tray.Shape.BoundBox.YLength, p["width"] + 5, abs_tol=1e-6)
        reopened.Parameters.set("B3", str(p["width"]) + " mm")
        reopened.recompute()
        assert math.isclose(reopened.Tray.Shape.Volume, expected_volume, abs_tol=1e-5)
        App.closeDocument(reopened.Name)
        report["fcstd"] = {"reopened": True, "parameter_edit_recomputed": True}
    report["passed"] = True
    report["output_directory"] = str(output)
    exit_code = 0
except BaseException:
    report["error"] = traceback.format_exc()
    traceback.print_exc()
finally:
    report_path = (output or project_root) / "verification.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(exit_code)
