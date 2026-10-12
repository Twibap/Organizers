from pathlib import Path
p=Path(r'C:\Users\Twibap\Workspace\Organizers\OpenHeatDraft.FCMacro')
s=p.read_text(encoding='utf-8-sig')
s=s.replace("startswith(('CarSampleP','GearSampleP'))", "startswith(('CarSampleP','GearSampleP','ScoreboardSample'))")
s=s.replace("obj.ViewObject.ShapeColor=sample_colors[int(obj.Name[-2:])-1]", "obj.ViewObject.ShapeColor=(0.65,0.64,0.55) if obj.Name=='ScoreboardSample' else sample_colors[int(obj.Name[-2:])-1]")
s=s.replace("    palette['WeatherLower']", "    palette['CarScoreTray']=(0.46,0.51,0.56)\n    palette['WeatherLower']")
p.write_text(s,encoding='utf-8')
