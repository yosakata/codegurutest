import re
import sys

label_dict = {}

filename = sys.argv[1]
#pattern = '(\d+)\.jpg.+cx:(\d).+cy:(\d+).+type:(.+).+'
pattern = '(\d+)\.jpg.+cx.+?(\d+).+cy.+?(\d+).+type:(.+)\}'
pattern_golf = '.+golf.+'
with open(filename,'r') as inputfile:
    for line in inputfile.readlines():
        m = re.search(pattern_golf, line)
        if m:
            continue
        m = re.search(pattern, line)
        if m:
            pic_id = m.group(1)
            cx = int((m.group(2)))
            cy = int((m.group(3)))
            label = (m.group(4))
            if pic_id not in label_dict:
                label_dict[pic_id] = { 'cx_min': cx, 'cy_min' : cx, 'cx_max': cy, 'cy_max': cy}
            if cx > label_dict[pic_id]['cx_max']:
                label_dict[pic_id]['cx_max'] = cx
            if cx < label_dict[pic_id]['cx_min']:
                label_dict[pic_id]['cx_min'] = cx

            if cy > label_dict[pic_id]['cy_max']:
                label_dict[pic_id]['cy_max'] = cy
            if cy < label_dict[pic_id]['cy_min']:
                label_dict[pic_id]['cy_min'] = cy

    for pic_id in label_dict:
        print(f"{pic_id}.jpg {label_dict[pic_id]['cx_min']},{label_dict[pic_id]['cy_min']},{label_dict[pic_id]['cx_max']},{label_dict[pic_id]['cy_max']}")




