"""Native parametric compact car/gear + scorepad tray. All lengths mm."""
import FreeCAD as App

def build_compact(doc,construction,final_group,component_group,measurements,anchor_x='0 mm',anchor_y='0 mm',rotated=False):
    s=doc.addObject('Spreadsheet::Sheet','CompactParameters');s.Label='자동차·기어·점수판 트레이 치수 (mm)'
    rows=[('AnchorX','='+anchor_x if 'Parameters' in anchor_x else anchor_x),('AnchorY','='+anchor_y if 'Parameters' in anchor_y else anchor_y),('Wall',1.6),('Floor',1.2),('Divider',1.2),
          ('CarL',measurements['race_car']['length']),('CarW',measurements['race_car']['width']),('CarH',measurements['race_car']['height']),
          ('GearD',measurements['gear_pawn']['base_diameter']),('GearH',measurements['gear_pawn']['height']),
          ('CarClear',1),('GearClear',0.5),('BoardW',100),('BoardL',60),('BoardMeasuredH',7),('BoardCap',10),
          ('LowerHead',0.6),('TopClear',1),('LidT',1.2),('LipD',0.6),('LipWall',0.8),('LipClear',0.2),
          ('CarWellL','=CarL + 2 * CarClear'),('CarWellW','=CarW + 2 * CarClear'),
          ('GearWellD','=GearD + 2 * GearClear'),('GearChannelL','=GearH + 2 * GearClear'),
          ('CellW','=GearChannelL'),('CellL','=CarWellW + Divider + GearWellD'),
          ('OuterW','=4 * CellW + 3 * Divider + 2 * Wall'),('OuterL','=2 * CellL + Divider + 2 * Wall'),
          ('LowerH','=Floor + BoardCap + LowerHead'),('UpperH','=Floor + GearD + TopClear'),
          ('LidZ','=LowerH + UpperH'),('TotalH','=LowerH + UpperH + LidT'),('SeatFloor','=LowerH + Floor')]
    cells={}
    for i,(alias,value) in enumerate(rows,2):
        cell='B'+str(i);cells[alias]=cell;s.set('A'+str(i),alias)
        s.set(cell,str(value) if isinstance(value,str) else str(value)+' mm');s.setAlias(cell,alias)
    s.setColumnWidth('A',210);s.setColumnWidth('B',300)
    doc.recompute()
    values={alias:float(App.Units.Quantity(s.get(cell)).Value) for alias,cell in cells.items()}
    assert values['CellW']>=values['CarWellL']
    assert values['OuterW']-2*values['Wall']>=values['BoardW']+1
    assert values['OuterL']-2*values['Wall']>=values['BoardL']+1
    P='CompactParameters.'
    def exp(obj,prop,value): obj.setExpression(prop,str(value))
    def pos(x,y):
        if rotated: return '('+P+'AnchorX) + '+P+'OuterL - ('+y+')','('+P+'AnchorY) + ('+x+')'
        return '('+P+'AnchorX) + ('+x+')','('+P+'AnchorY) + ('+y+')'
    def box(name,w,l,h,x,y,z):
        o=doc.addObject('Part::Box',name);gx,gy=pos(x,y)
        if rotated:o.Placement.Rotation=App.Rotation(App.Vector(0,0,1),90)
        for prop,v in [('Length',w),('Width',l),('Height',h),('Placement.Base.x',gx),('Placement.Base.y',gy),('Placement.Base.z',z)]:exp(o,prop,v)
        construction.addObject(o);return o
    def cyl(name,r,h,x,y,z,horizontal=False):
        o=doc.addObject('Part::Cylinder',name);gx,gy=pos(x,y)
        if horizontal:o.Placement.Rotation=App.Rotation(App.Vector(0,0,1),App.Vector(0,1,0) if rotated else App.Vector(1,0,0))
        for prop,v in [('Radius',r),('Height',h),('Placement.Base.x',gx),('Placement.Base.y',gy),('Placement.Base.z',z)]:exp(o,prop,v)
        construction.addObject(o);return o
    def boolean(name,typ,a,b):
        o=doc.addObject(typ,name);o.Base=a;o.Tool=b;o.Refine=True;construction.addObject(o);return o
    def fuse(name,shapes):
        o=doc.addObject('Part::MultiFuse',name);o.Shapes=shapes;o.Refine=True;construction.addObject(o);return o
    parts=[];refs=[];colors={}
    def finish(o,label,role,color):
        construction.removeObject(o);final_group.addObject(o);o.Label=label
        o.addProperty('App::PropertyString','DraftRole','Draft').DraftRole=role
        o.addProperty('App::PropertyString','FitStatus','Draft').FitStatus='CAD envelopes verified separately; physical fit unverified'
        parts.append(o);colors[o.Name]=color;return o
    lower=box('CompactScoreOuter',P+'OuterW',P+'OuterL',P+'LowerH','0 mm','0 mm','0 mm')
    pocket=box('CompactScorePocket',P+'OuterW - 2 * '+P+'Wall',P+'OuterL - 2 * '+P+'Wall',P+'LowerH',P+'Wall',P+'Wall',P+'Floor')
    lower=boolean('CompactScoreHollow','Part::Cut',lower,pocket)
    upper=box('CompactSeatOuter',P+'OuterW',P+'OuterL',P+'UpperH','0 mm','0 mm',P+'LowerH')
    car_positions=[];gear_positions=[]
    for row in range(2):
        ys=P+'Wall + %d * ('%row+P+'CellL + '+P+'Divider)'
        gy='('+ys+') + '+P+'CarWellW + '+P+'Divider + '+P+'GearWellD / 2'
        for col in range(4):
            idx=row*4+col+1;name='CompactSeat%02d'%idx
            xs=P+'Wall + %d * ('%col+P+'CellW + '+P+'Divider)'
            car_x='('+xs+') + ('+P+'CellW - '+P+'CarWellL) / 2'
            car=box(name+'CarCut',P+'CarWellL',P+'CarWellW',P+'UpperH',car_x,ys,P+'SeatFloor')
            upper=boolean(name+'CarHollow','Part::Cut',upper,car)
            groove=box(name+'GearPocket',P+'GearChannelL',P+'GearWellD',P+'UpperH',xs,
                       '('+gy+') - '+P+'GearWellD / 2',P+'SeatFloor')
            upper=boolean(name+'GearHollow','Part::Cut',upper,groove)
            car_positions.append((idx,car_x,ys));gear_positions.append((idx,xs,gy))
        # Lower the car-region dividers so the cars can be picked up by their sides.
        relief=box('CompactCarAccess'+str(row),P+'OuterW',P+'CarWellW + 2 * '+P+'Wall',P+'UpperH',
                   '0 mm','('+ys+') - '+P+'Wall',P+'SeatFloor + 4 mm')
        upper=boolean('CompactCarRelief'+str(row),'Part::Cut',upper,relief)
    # Lower tray locator keys align the two independently removable trays.
    keys=[]
    for side in range(2):
        for row in range(2):
            idx=side*2+row
            x='%d * ('%side+P+'OuterW - '+P+'Wall)'
            y=P+'Wall + '+P+'CarWellW + '+P+'Divider + 4 mm + %d * ('%row+P+'CellL + '+P+'Divider)'
            keys.append(box('CompactLocator'+str(idx),P+'Wall','4 mm','1 mm',x,y,P+'LowerH'))
            gap=box('CompactLocatorGap'+str(idx),P+'Wall + 0.4 mm','4.4 mm','1.2 mm','('+x+') - 0.2 mm','('+y+') - 0.2 mm',P+'LowerH')
            upper=boolean('CarGearBody' if idx==3 else 'CompactLocatorFit'+str(idx),'Part::Cut',upper,gap)
    lower=fuse('CarScoreTray',[lower]+keys)
    finish(lower,'점수판 트레이 - 100x60 / 묶음7mm, 최대10mm',( 'scoreboard_tray'),(0.46,0.51,0.56))
    finish(upper,'자동차·기어8쌍 - 4열x2행 / 기어 눕힘','car_gear_carrier',(0.31,0.38,0.44))
    plate=box('CompactLidPlate',P+'OuterW',P+'OuterL',P+'LidT','0 mm','0 mm',P+'LidZ')
    ox=P+'Wall + '+P+'LipClear';oy=ox
    rim=box('CompactLipOuter',P+'OuterW - 2 * ('+ox+')',P+'OuterL - 2 * ('+oy+')',P+'LipD + 0.05 mm',ox,oy,P+'LidZ - '+P+'LipD')
    inner=box('CompactLipInner',P+'OuterW - 2 * ('+ox+' + '+P+'LipWall)',P+'OuterL - 2 * ('+oy+' + '+P+'LipWall)',P+'LipD + 0.1 mm',ox+' + '+P+'LipWall',oy+' + '+P+'LipWall',P+'LidZ - '+P+'LipD')
    rim=boolean('CompactLipRing','Part::Cut',rim,inner)
    for col in range(1,4):
        x=P+'Wall + %d * '%col+P+'CellW + %d * '%(col-1)+P+'Divider - '+P+'LipClear'
        gap=box('CompactLipColumnGap'+str(col),P+'Divider + 2 * '+P+'LipClear',P+'OuterL',P+'LipD + 0.1 mm',x,'0 mm',P+'LidZ - '+P+'LipD')
        rim=boolean('CompactLipColumnClear'+str(col),'Part::Cut',rim,gap)
    rowgap=box('CompactLipRowGap',P+'OuterW',P+'Divider + 2 * '+P+'LipClear',P+'LipD + 0.1 mm',
               '0 mm',P+'Wall + '+P+'CellL - '+P+'LipClear',P+'LidZ - '+P+'LipD')
    rim=boolean('CompactLipRowClear','Part::Cut',rim,rowgap)
    finish(boolean('CarGearLid','Part::Fuse',plate,rim),'자동차 트레이 덮개 - 1.2mm','lid',(0.31,0.38,0.44))
    for idx,x,y in car_positions:
        o=box('CarSampleP%02d'%idx,P+'CarL',P+'CarW',P+'CarH','('+x+') + '+P+'CarClear','('+y+') + '+P+'CarClear',P+'SeatFloor')
        refs.append(o);o.Label='P%02d 자동차 외곽11x23x7 - 출력 제외'%idx
    for idx,x,y in gear_positions:
        o=cyl('GearSampleP%02d'%idx,P+'GearD / 2',P+'GearH','('+x+') + '+P+'GearClear',y,P+'SeatFloor + '+P+'GearD / 2',True)
        refs.append(o);o.Label='P%02d 기어 기준원통D15x25 - 출력 제외'%idx
    board=box('ScoreboardSample',P+'BoardW',P+'BoardL',P+'BoardCap','('+P+'OuterW - '+P+'BoardW) / 2','('+P+'OuterL - '+P+'BoardL) / 2',P+'Floor')
    board.Label='점수판100x60 / 최대10mm 수납 범위 (실측 묶음7mm)';refs.append(board)
    for o in refs:
        construction.removeObject(o);component_group.addObject(o)
        o.addProperty('App::PropertyString','DraftRole','Draft').DraftRole='reference_not_printable'
    doc.recompute()
    return {'parts':parts,'lids':[doc.CarGearLid],'refs':refs,'colors':colors,'parameters':values,'cells':cells,'rotated':rotated}
