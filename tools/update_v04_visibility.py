from pathlib import Path
root=Path(r'C:\Users\Twibap\Workspace\Organizers')
p=root/'HeatOrganizerCDraft.FCMacro';s=p.read_text(encoding='utf-8')
s=s.replace("    parts, lids, colors, layout = [], [], {}, []", "    component_group = doc.addObject('App::DocumentObjectGroup', 'ComponentSamples')\n    component_group.Label = 'Measured car / nominal gear envelopes - not printable'\n    parts, lids, colors, layout = [], [], {}, []")
s=s.replace("        reference_group.addObject(ref)\n        ref.addProperty", "        (component_group if ref.Name.startswith(('CarSample','GearSample')) else reference_group).addObject(ref)\n        ref.addProperty")
p.write_text(s,encoding='utf-8')
p=root/'OpenHeatDraft.FCMacro';s=p.read_text(encoding='utf-8-sig')
s=s.replace("    final_names = {obj.Name for obj in parts}", """    final_names = {obj.Name for obj in parts}
    sample_names = {o.Name for o in doc.Objects if o.Name.startswith(('CarSampleP','GearSampleP'))}
    component_group = doc.getObject('ComponentSamples')
    if sample_names:
        if component_group is None:
            component_group=doc.addObject('App::DocumentObjectGroup','ComponentSamples')
        component_group.Label='Measured car / nominal gear envelopes - not printable'
        for name in sample_names:
            obj=doc.getObject(name)
            if obj in doc.References.Group: doc.References.removeObject(obj)
            component_group.addObject(obj)
        component_group.ViewObject.Visibility=True
    sample_colors=[(0.78,0.22,0.18),(0.16,0.43,0.70),(0.91,0.66,0.15),(0.18,0.58,0.43),
                   (0.30,0.33,0.37),(0.72,0.70,0.65),(0.90,0.40,0.16),(0.52,0.32,0.65)]""")
s=s.replace("obj.ViewObject.Visibility = obj.Name in final_names and not obj.Name.endswith('Lid')", "obj.ViewObject.Visibility = (obj.Name in final_names and not obj.Name.endswith('Lid')) or obj.Name in sample_names\n        if obj.Name in sample_names:\n            obj.ViewObject.ShapeColor=sample_colors[int(obj.Name[-2:])-1]\n            obj.ViewObject.Transparency=55 if obj.Name.startswith('Gear') else 25\n            obj.ViewObject.LineColor=(0.15,0.17,0.20)")
s=s.replace("'valid_parts': sum(obj.Shape.isValid() for obj in parts)", "'valid_parts': sum(obj.Shape.isValid() for obj in parts),\n              'visible_component_reference_envelopes':len(sample_names)")
p.write_text(s,encoding='utf-8')
p=root/'VerifyHeatReview.FCMacro';s=p.read_text(encoding='utf-8-sig')
s=s.replace("        assert len(visible)==15,visible", "        expected=len(doc.OrganizerParts.Group)-sum(o.Name.endswith('Lid') for o in doc.OrganizerParts.Group)\n        assert len(visible)==expected,visible\n        samples=doc.getObject('ComponentSamples')\n        if samples:\n            assert len(samples.Group)==16 and all(o.ViewObject.Visibility for o in samples.Group)")
s=s.replace("visible_parts=len(visible),hidden_lids=14)", "visible_parts=len(visible),hidden_lids=14,visible_component_envelopes=16 if samples else 0)")
p.write_text(s,encoding='utf-8')
print('native visibility adapted for V0.4 reference envelopes')
