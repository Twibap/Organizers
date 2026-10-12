from pathlib import Path
import hashlib,json,zipfile
root=Path.cwd()
f=Path((root/'output/latest-heat-draft.txt').read_text(encoding='utf-8-sig').strip())
files=['HeatOrganizerDraft.FCStd','HeatOrganizerReview.FCStd','CarGearTray-Compact.FCStd','CarGearTray-Compact-Exploded.FCStd']
result=[]
for name in files:
 p=f/name
 with zipfile.ZipFile(p) as z:
  has_gui='GuiDocument.xml' in z.namelist()
 result.append({'file':name,'bytes':p.stat().st_size,'gui_metadata':has_gui})
assert all(r['gui_metadata'] for r in result)
assert hashlib.sha256((f/files[0]).read_bytes()).digest()==hashlib.sha256((f/files[1]).read_bytes()).digest()
m=json.loads((f/'manifest.json').read_text(encoding='utf-8-sig'))
assert len(m['stl_files'])==16 and sum(v['quantity'] for v in m['stl_files'])==30
assert (f/'Draft-notes.md').exists()
print(json.dumps({'files':result,'draft_matches_review':True,'stl_types':16,'print_quantity':30},ensure_ascii=False,indent=2))
