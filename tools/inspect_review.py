from pathlib import Path
import zipfile,xml.etree.ElementTree as ET
root=Path(r'C:\Users\Twibap\Workspace\Organizers')
folder=Path((root/'output/latest-heat-draft.txt').read_text().strip())
with zipfile.ZipFile(folder/'HeatOrganizerReview.FCStd') as z:
    assert 'GuiDocument.xml' in z.namelist()
    t=ET.fromstring(z.read('GuiDocument.xml'))
    vp=t.find('ViewProviderData')
    print('GUI view providers:',len(vp))
    for o in vp:
        name=o.get('name')
        if name in ['P01Lower','P01Upper','C02Body','Construction','References','OrganizerParts','P01Lid']:
            visibility=o.find("./Properties/Property[@name='Visibility']/Bool")
            print(name,ET.tostring(visibility,encoding='unicode') if visibility is not None else 'no visibility')
