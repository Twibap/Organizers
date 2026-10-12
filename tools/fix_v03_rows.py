from pathlib import Path
f=Path('HeatOrganizerReferenceDraft.FCMacro');s=f.read_text(encoding='utf-8-sig');a=s.index("        ('ModuleW',");b=s.index("        ('SampleCards',",a);s=s[:a]+s[b:];f.write_text(s,encoding='utf-8')
