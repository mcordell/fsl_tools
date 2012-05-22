__author__ = 'michael'
import re, subprocess, xlwt, operator
from xlwt import easyxf


def add_to_dict(atlas, dictionary):
    atlas_percentages = dict()
    matches = re.finditer("\d+% ", atlas)
    matches = list(matches)
    length_matches = len(matches)
    string_length = len(atlas)
    for i in range(0, length_matches):
        if i + 1 == length_matches:
            key = atlas[matches[i].end():string_length]
        else:
            key = atlas[matches[i].end():matches[i + 1].start()]
        key=key.strip().strip(",").strip()
        if key in dictionary:
            dictionary[key] += 1
        else:
            dictionary[key] = 1
        atlas_percentages[key] = matches[i].group(0)
    return atlas_percentages,dictionary

def prep_worksheet(ws, sorted_atlases):
    red_style = easyxf(
        'pattern: pattern solid, fore_colour red;'
        'align: vertical center, horizontal center;'
    )
    blue_style = easyxf(
        'pattern: pattern solid, fore_colour blue;'
        'align: vertical center, horizontal center;'
    )
    green_style = easyxf(
        'pattern: pattern solid, fore_colour green;'
        'align: vertical center, horizontal center;'
    )
    yellow_style = easyxf(
        'pattern: pattern solid, fore_colour yellow;'
        'align: vertical center, horizontal center;'
    )
    pink_style = easyxf(
        'pattern: pattern solid, fore_colour pink;'
        'align: vertical center, horizontal center;'
    )
    colors=[green_style,yellow_style,pink_style]
    ws.write(1, 1, 'Condition')
    ws.write(1, 2, 'Subject')
    ws.write(1, 3, 'Run')
    ws.write(1, 4, 'x')
    ws.write(1, 5, 'y')
    ws.write(1, 6, 'z')
    ws.write(1, 7, 'x')
    ws.write(1, 8, 'y')
    ws.write(1, 9, 'z')
    ws.write_merge(0, 0, 4, 6, 'Run Space', red_style)
    ws.write_merge(0, 0, 7, 9, 'Std Space', blue_style)
    start_value = 10
    atlas_loc_pointer=10
    atlas_points=dict()
    color_index=0
    for atlas in sorted_atlases:
        points=dict()
        for atlas_tuple in sorted_atlases[atlas]:
            print atlas_tuple
            key, value = atlas_tuple
            ws.write(1, atlas_loc_pointer, key)
            points[key]=atlas_loc_pointer
            atlas_loc_pointer += 1
        ws.write_merge(0, 0, start_value, atlas_loc_pointer-1, atlas, colors[color_index])
        start_value=atlas_loc_pointer
        atlas_points[atlas]=points
        if color_index == len(colors):
            color_index=0
        else:
            color_index+=1


    start_row=2
    return atlas_points, start_row

def get_atlas_location(atlas_name,std_coords,atlas_dict):
    std_x,std_y,std_z=std_coords
    command = ["atlasquery", "-a", atlas_name, "-c", str(std_x) + "," + str(std_y) + "," + str(std_z)]
    p_one = subprocess.Popen(command, stdout=subprocess.PIPE)
    atlas_lines = p_one.stdout.readlines()
    atlas = atlas_lines[0].split("<b>"+atlas_name+"</b><br>")[1]
    percentages,atlas_dict = add_to_dict(atlas, atlas_dict)
    return percentages, atlas_dict

def write_atlas_line(worksheet,atlas_location,row_number,atlas_points):
    sty_atlas=easyxf(num_format_str="0%")
    worksheet.write(row_number, 1, atlas_location.condition)
    worksheet.write(row_number, 2, atlas_location.subject)
    worksheet.write(row_number, 3, atlas_location.run)
    worksheet.write(row_number, 4, int(atlas_location.x))
    worksheet.write(row_number, 5, int(atlas_location.y))
    worksheet.write(row_number, 6, int(atlas_location.z))
    worksheet.write(row_number, 7, float(atlas_location.std_x))
    worksheet.write(row_number, 8, float(atlas_location.std_y))
    worksheet.write(row_number, 9, float(atlas_location.std_z))
    atlas_percentages = atlas_location.atlas_percentages
    for atlas in atlas_percentages:
        percentages=atlas_percentages[atlas]
        points=atlas_points[atlas]
        for atlas_key in percentages.keys():
            point=points[atlas_key]
            value=float(percentages[atlas_key].strip().strip("%"))/100
            worksheet.write(row_number, point, value,sty_atlas)

def sort_atlas_locations(atlases):
    sorted_atlases=dict()
    for atlas in atlases:
        atlas_dict=atlases[atlas]
        sorted_locations=sorted(atlas_dict.iteritems(),key=operator.itemgetter(1),reverse=True)
        sorted_atlases[atlas]=sorted_locations
    return sorted_atlases
