from pathlib import Path
p=Path(r'C:\Users\Twibap\Workspace\Organizers\MakeHeatCReview.FCMacro')
s=p.read_text(encoding='utf-8-sig')
s=s.replace("            target.Shape=source.Shape.copy();target.Shape.translate(origin)", "            shape=source.Shape.copy();shape.translate(origin)\n            if source.Name=='CarGearDrawer': shape.translate(App.Vector(0,-32,0))\n            target.Shape=shape")
s=s.replace("                target.Shape.translate(App.Vector(0,-32,0))\n", "")
p.write_text(s,encoding='utf-8')
