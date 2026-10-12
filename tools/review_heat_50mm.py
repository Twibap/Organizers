"""Read-only CAD capacity review for all pairs of the four 2026 Heat expansions.

Run with FreeCADCmd. Existing FCStd files and design parameters are not saved.
Cards, measured token bundles, cars and nominal gear cylinders are checked.
A separate token-fit candidate is saved without overwriting the source CAD.
Common mat footprints and press pieces remain explicit fit conditions.
"""
from pathlib import Path
from itertools import combinations
import json
import math
import os
import traceback
import FreeCAD as App
import Part
import Mesh

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output' / 'heat_50mm_review'
OUT.mkdir(parents=True, exist_ok=True)
LATEST = Path((ROOT / 'output' / 'latest-heat-draft.txt').read_text().strip())
EXPANSIONS = {
    'Heavy Rain': dict(basic=12, starting=3, heat=15, stress=5,
                      garage=12, other=6, sponsor=7, legends_extra=0,
                      cars=1, scorepads=1),
    'Tunnel Vision': dict(basic=12, starting=3, heat=9, stress=6,
                         garage=12, other=6, sponsor=7, legends_extra=0,
                         cars=1, scorepads=1),
    'Rocky Roads': dict(basic=12, starting=3, heat=15, stress=5,
                       garage=12, other=6, sponsor=7, legends_extra=0,
                       cars=1, scorepads=1),
    'Legends': dict(basic=0, starting=0, heat=0, stress=0,
                   garage=0, other=0, sponsor=21, legends_extra=84,
                   cars=0, scorepads=0),
}

result = {
    'date': '2026-10-12',
    'scope': 'Base + any two distinct currently listed official expansions; '
             'maps, rulebooks and player mats excluded; common mats and scorepads included.',
    'source_fcstd': str(LATEST / 'HeatOrganizerDraft.FCStd'),
    'status': 'conditional_feasibility_review_not_full_component_fit_validation',
    'assumed_sleeved_card_mm': [58, 89],
    'measured_sample': {'cards': 24, 'height_mm': 9},
    'pitch_estimate_mm': 0.375,
    'assumed_stack_removal_clearance_mm': 1,
    'organizer_body_envelope_mm': [288, 288, 44],
    'source_card_layer_height_mm': 38,
    'proposed_total_height_mm': 49,
    'paper_layer_condition': {
        'maximum_combined_thickness_mm': 4,
        'contents': ['Legends mat', 'Championship mat'],
        'top_headroom_mm': 1,
        'formula': '44 + common mats <= 4 + 1 headroom <= 49 < 50',
        'common_mats_combined_upper_bound_mm': 4,
        'common_mats_upper_bound_basis': 'They are a subset of the user-measured 4 mm base mats/rules stack.',
        'scorepads_storage': 'v0.5 CarScoreTray; user-measured whole bundle100x60x7mm; design capacity10mm',
        'xy_condition': 'Paper pieces must lie flat inside the actual box above the organizer lids.',
        'physical_measurements_available': False,
    },
    'unverified_components': [
        'common mats: individual footprint and combined thickness',
        'whether measured whole scoreboard bundle covers all scorepads of the selected expansions',
        'press standees and their bases',
        'entire gear upper outline beyond measured base diameter',
        'new expansion card sleeve exterior and actual large-deck thickness',
    ],
    'original_fcstd_modified': False,
    'measurement_and_allocation_files_updated': True,
    'cases': [],
}

doc = None
try:
    doc = App.openDocument(str(LATEST / 'HeatOrganizerDraft.FCStd'))
    doc.recompute()
    parts = list(doc.OrganizerParts.Group)
    assert all(obj.Shape.isValid() for obj in parts)
    assert doc.getObject('CarScoreTray') is not None, 'Token candidate requires the compact v0.5 layout'
    measurements = json.loads((ROOT / 'heat-measurements.json').read_text(encoding='utf-8-sig'))
    token_group = doc.addObject('App::DocumentObjectGroup', 'TokenFitCandidate')
    token_group.Label = 'Measured weather/road bundles - 44mm token candidate'
    token_refs = doc.addObject('App::DocumentObjectGroup', 'TokenFitSamples')
    token_refs.Label = 'Measured token bundles - references, not printable'
    token_parts = []
    token_proxies = []
    token_bins = []
    tx, ty, tw, tl = 195.4, 112.6, 85.0, 66.0
    floor, wall, lid_t, lip_d, lip_wall, lip_clear = 1.2, 2.0, 1.2, 0.6, 0.8, 0.2
    for name, measured, z, module_h in [
        ('WeatherFit', measurements['weather_tokens_bundle'], 0.0, 16.0),
        ('RoadFit', measurements['road_condition_tokens_bundle'], 16.0, 28.0),
    ]:
        body_h = module_h - lid_t
        outer = Part.makeBox(tw, tl, body_h, App.Vector(tx, ty, z))
        cavity = Part.makeBox(tw-2*wall, tl-2*wall, body_h,
                              App.Vector(tx+wall, ty+wall, z+floor))
        body = doc.addObject('PartDesign::Feature', name+'Body')
        body.Shape = outer.cut(cavity).removeSplitter()
        body.Label = name+' / body'
        body.addProperty('App::PropertyString', 'Contents', 'FitReview').Contents = json.dumps(measured)
        token_group.addObject(body)
        plate_z = z + body_h
        plate = Part.makeBox(tw, tl, lid_t, App.Vector(tx, ty, plate_z))
        lip_x, lip_y = tx+wall+lip_clear, ty+wall+lip_clear
        lip_w, lip_l = tw-2*(wall+lip_clear), tl-2*(wall+lip_clear)
        skirt_outer = Part.makeBox(lip_w, lip_l, lip_d,
                                   App.Vector(lip_x, lip_y, plate_z-lip_d))
        skirt_inner = Part.makeBox(lip_w-2*lip_wall, lip_l-2*lip_wall, lip_d+0.1,
                                   App.Vector(lip_x+lip_wall, lip_y+lip_wall, plate_z-lip_d-0.05))
        lid = doc.addObject('PartDesign::Feature', name+'Lid')
        lid.Shape = plate.fuse(skirt_outer.cut(skirt_inner)).removeSplitter()
        lid.Label = name+' / lid - clearance skirt, retention unverified'
        token_group.addObject(lid)
        for part in [body, lid]:
            assert part.Shape.isValid() and len(part.Shape.Solids)==1, part.Name
            token_parts.append(part)
        # A solid bounding box of the entire measured bundle is conservative.
        shape = Part.makeBox(measured['width'], measured['length'], measured['height'],
                             App.Vector(tx+wall+1, ty+wall+1, z+floor))
        reference = doc.addObject('PartDesign::Feature', name+'BundleSample')
        reference.Shape = shape
        reference.Label = name+' measured '+str(measured['count'])+'-piece bundle'
        token_refs.addObject(reference)
        token_proxies.append((name+'Bundle', shape))
        usable = body_h-floor-lip_d
        assert usable >= measured['height']+1-1e-6
        token_bins.append(dict(name=name, count=measured['count'],
                               measured_bundle_mm=[measured['width'], measured['length'], measured['height']],
                               outer_module_mm=[tw, tl, module_h],
                               position_mm=[tx, ty, z],
                               usable_under_lip_mm=[tw-2*wall, tl-2*wall, round(usable,3)],
                               vertical_removal_headroom_mm=round(usable-measured['height'],3)))
    parts.extend(token_parts)
    doc.recompute()
    for i, one in enumerate(parts):
        a = one.Shape.BoundBox
        assert a.XMin>=1-1e-6 and a.XMax<=289+1e-6
        assert a.YMin>=1-1e-6 and a.YMax<=289+1e-6
        assert a.ZMin>=-1e-6 and a.ZMax<=44+1e-6
        for two in parts[i+1:]:
            b = two.Shape.BoundBox
            if (min(a.XMax,b.XMax)-max(a.XMin,b.XMin)<=1e-6 or
                min(a.YMax,b.YMax)-max(a.YMin,b.YMin)<=1e-6 or
                min(a.ZMax,b.ZMax)-max(a.ZMin,b.ZMin)<=1e-6):
                continue
            assert one.Shape.common(two.Shape).Volume<1e-6, (one.Name,two.Name)
    result['token_fit'] = dict(
        current_weather_lower_compartment_mm=[89.6,45.2,11],
        measured_bundles_fit_original_weather_lower=False,
        candidate_bins=token_bins, candidate_parts_collisions=0,
        added_weather_and_road_tokens_by_expansion={name: {'weather':0, 'road_conditions':0} for name in EXPANSIONS},
        two_expansion_total_weather=6, two_expansion_total_road_conditions=12,
        original_press_module_retained=True,
        footprint_of_added_token_stack_mm=[85,66],
        total_stack_height_mm=44,
        measured_bundle_geometry_passed=True)
    max_scoreboard = Part.makeBox(60,100,10,App.Vector(0,0,0))
    # The source proxy already carries the compact tray's rotated placement.
    score_ref = doc.getObject('ScoreboardSample')
    assert score_ref is not None
    sb = score_ref.Shape.BoundBox
    max_scoreboard = Part.makeBox(sb.XLength,sb.YLength,10,
                                  App.Vector(sb.XMin,sb.YMin,sb.ZMin))
    for part in parts:
        assert part.Shape.common(max_scoreboard).Volume<1e-6, ('scoreboard10mm',part.Name)
    result['scoreboard_maximum10mm_geometry_passed'] = True
    for pair in combinations(EXPANSIONS, 2):
        extra = {key: sum(EXPANSIONS[name][key] for name in pair)
                 for key in next(iter(EXPANSIONS.values()))}
        players = 6 + extra['cars']
        reserve_heat = 48 + extra['heat'] - players * 6
        reserve_stress = 37 + extra['stress'] - players * 3
        garage = 96 + extra['garage']
        sponsor = 35 + extra['sponsor']
        other = 24 + extra['other']
        legends = 'Legends' in pair
        allocations = []
        for index in range(1, players + 1):
            allocations.append(('P%02dBody' % index, 24, 'player ready set'))
        if legends:
            other += 36 + 12  # New Legend + Rival; original base Legend cards retained.
        allocations.extend([
            ('ReserveBody', reserve_heat + reserve_stress + (36 if legends else 0),
             'reserve Heat/Stress + Legends Power Up' if legends else 'reserve Heat/Stress'),
            ('SponsorBody', sponsor, 'sponsorship'),
            ('OtherBody', other, 'Legends/Event/Track/Rival'),
            ('GarageBody', garage // 2, 'garage first stack'),
            ('GarageBody', garage - garage // 2, 'garage second stack'),
        ])
        proxies = list(token_proxies) + [('scoreboard_max10mm',max_scoreboard)]
        bins = []
        garage_index = 0
        for name, count, contents in allocations:
            body = doc.getObject(name)
            box = body.Shape.BoundBox
            px, py, pz = box.XMin + 3, box.YMin + 3, box.ZMin + 2
            if name == 'GarageBody':
                if garage_index:
                    px = box.XMin + (128.8 + 2) / 2 + 1
                garage_index += 1
            depth = box.ZLength - 2 - 0.8
            stack = count * 0.375
            separator = 1 if legends and name == 'ReserveBody' else 0
            assert stack + separator + 1 <= depth + 1e-6, (pair, name, count, depth)
            shape = Part.makeBox(58, 89, stack + separator, App.Vector(px, py, pz))
            proxies.append((contents + ' / ' + name, shape))
            bins.append(dict(body=name, contents=contents, cards=count,
                             estimated_stack_height_mm=stack,
                             assumed_separator_thickness_mm=separator,
                             available_depth_under_lip_mm=round(depth, 3),
                             remaining_after_1mm_clearance_mm=round(depth - stack - separator - 1, 3)))
        for index in range(1, players + 1):
            for kind in ['Car', 'Gear']:
                name = '%sSampleP%02d' % (kind, index)
                proxies.append((name, doc.getObject(name).Shape))
        for name, shape in proxies:
            for part in parts:
                overlap = part.Shape.common(shape).Volume
                assert overlap < 1e-6, (pair, name, part.Name, overlap)
        for i, (name, shape) in enumerate(proxies):
            for other_name, other_shape in proxies[i + 1:]:
                overlap = shape.common(other_shape).Volume
                assert overlap < 1e-6, (pair, name, other_name, overlap)
        count = sum(bin['cards'] for bin in bins)
        # Independent sum of official printed card inventory, without storage allocation.
        printed = 330 + sum(sum(EXPANSIONS[name][key] for key in [
            'basic', 'starting', 'heat', 'stress', 'garage', 'other',
            'sponsor', 'legends_extra']) for name in pair)
        assert count == printed, (pair, count, printed)
        result['cases'].append(dict(
            expansions=list(pair), total_cards=count, player_sets=players,
            reserve_heat=reserve_heat, reserve_stress=reserve_stress,
            garage_cards=garage, sponsorship_cards=sponsor,
            common_cards_in_other=other, powerup_cards_in_reserve=36 if legends else 0,
            unused_player_bins=['P08Body'] if legends else [],
            cars=players, gears=players, scorepads=1 + extra['scorepads'],
            bins=bins, card_and_car_and_nominal_gear_proxy_collisions=0,
            measured_token_bundle_collisions=0,
            weather_tokens=6, road_condition_tokens=12,
            nominal_card_car_gear_geometry_passed=True,
            all_components_physically_verified=False))
    result['nominal_card_car_gear_geometry_passed_all_cases'] = True
    result['all_components_fit_verified'] = False
    candidate_path = OUT / 'HeatTokenFitCandidate.FCStd'
    doc.Label = 'Heat - 50mm feasibility / measured token candidate'
    doc.recompute()
    doc.saveAs(str(candidate_path))
    Part.export(parts,str(OUT/'HeatTokenFitCandidate.step'))
    stl_dir = OUT/'token-stl'
    stl_dir.mkdir(exist_ok=True)
    for part in token_parts:
        Mesh.export([part],str(stl_dir/(part.Name+'.stl')))
        assert Mesh.Mesh(str(stl_dir/(part.Name+'.stl'))).isSolid(),part.Name
    result['candidate_fcstd'] = str(candidate_path)
    result['candidate_stl_closed'] = True
    result['candidate_total_parts'] = len(parts)
except BaseException:
    result['nominal_card_car_gear_geometry_passed_all_cases'] = False
    result['error'] = traceback.format_exc()
finally:
    if doc is not None:
        App.closeDocument(doc.Name)
    (OUT / 'capacity-review.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({key: result[key] for key in [
        'status', 'nominal_card_car_gear_geometry_passed_all_cases']}, ensure_ascii=False))
    print('Cases: ' + str([(case['expansions'], case['total_cards']) for case in result['cases']]))
    if 'error' in result:
        print(result['error'])
    import sys
    sys.stdout.flush()
    os._exit(0 if result['nominal_card_car_gear_geometry_passed_all_cases'] else 1)
