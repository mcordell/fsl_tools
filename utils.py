__author__ = 'michael'
import re, subprocess, operator
from xlwt import easyxf

def parse_to_dict(fsf_lines):
    fsf_dict=dict()
    for line in fsf_lines:
        line=line.strip()
        if len(line) > 0 and line[0] != "#":
            set_line=re.search("set [^ ]* [^s]*",line.strip())
            if set_line:
                split_line=line.split(" ")
                if len(split_line) > 3:
                    #combine and strip mri values that have spaces in them
                    temp=list()
                    for i in range (2,len(split_line)):
                        temp.append(split_line[i])
                    cleaned=' '.join(temp)
                    cleaned=cleaned.strip('\"')
                    print cleaned
                else:
                    cleaned=split_line[2].strip('\"')
                fsf_dict[split_line[1]]=cleaned
    return fsf_dict

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

def fsf_to_csv(fsf_file):
    if fsf_file.type == fsf_file.FIRST_TYPE:
        return first_to_csv(fsf_file)
    elif fsf_file.type == fsf_file.FE_TYPE:
        return fe_to_csv(fsf_file)
    elif fsf_file.type == fsf_file.ME_TYPE:
        return me_to_csv(fsf_file)
    elif fsf_file.type == fsf_file.PRE_TYPE:
        return pre_to_csv(fsf_file)
    else:
        return None

def pre_to_csv(fsf_file):
    width=2
    out_lines=list()
    out_lines.append('Preproc')
    out_lines.append("Analysis Name:,"+fsf_file.analysis_name)
    out_lines.append("Input file:,"+fsf_file.input_file)
    out_lines.append(',')
    out_lines.append("TR:, "+fsf_file.tr)
    out_lines.append("Total Volumes:, "+fsf_file.number_volumes)
    out_lines.append("Deleted Volumes:, "+fsf_file.removed_volumes)
    out_lines.append("Motion Correction:, "+fsf_file.motion_correction)
    out_lines.append("Brain Thresholding:, "+fsf_file.brain_thresh)
    out_lines.append("Smoothing:, "+fsf_file.smoothing)
    height=len(out_lines)
    return out_lines,width,height

def first_to_csv(fsf_file):
    width=2
    out_lines=list()
    out_lines.append('First Level')
    out_lines.append("Analysis Name:,"+fsf_file.analysis_name)
    out_lines.append("Input file:,"+fsf_file.input_file)
    out_lines.append(',')
    out_lines.append('Regressors:')
    out_lines.append('Name,Convolution,Add Temporal Derivative,Apply Temporal Filtering,Path')
    for item in fsf_file.evs.items():
        key,ev=item
        name=check_for_none(ev.name)
        conv=check_for_none(ev.convolution)
        temporal_deriv=check_for_none(ev.temporal_deriv)
        filt=check_for_none(ev.temporal_filtering)
        path=check_for_none(ev.file_path)
        out_lines.append(",".join([name,conv,temporal_deriv,filt,path]))
    if width < 5:
        width = 5
    out_lines.append(",")
    out_lines.append('Contrast Matrix:')
    len_matrix=len(fsf_file.design_matrix[0])
    if len_matrix > width:
        width = len_matrix
    for row in fsf_file.design_matrix:
        row=",".join(row)
        out_lines.append(row)
    height=len(out_lines)
    return out_lines,width,height

def fe_to_csv(fsf_file):
    out_lines=list()
    width=2
    out_lines.append('Fixed Effects')
    out_lines.append("Analysis Name:,"+fsf_file.analysis_name)
    out_lines.append("Input Count:, "+fsf_file.number_inputs)
    out_lines.append("Outpath:,"+fsf_file.output_path)
    out_lines.append('Inputs:')
    for ind in range(1,int(fsf_file.number_inputs)+1):
        i=str(ind)
        line=fsf_file.inputs[i]
        out_lines.append(line)
    out_lines.append(',')
    out_lines.append('Regressor Matrix:')
    len_matrix=len(fsf_file.regressor_matrix[0])
    if len_matrix > width:
        width = len_matrix
    for row in fsf_file.regressor_matrix:
        row=",".join(row)
        out_lines.append(row)
    out_lines.append(',')
    out_lines.append('Contrast Matrix:')
    len_matrix=len(fsf_file.design_matrix[0])
    if len_matrix > width:
        width = len_matrix
    for row in fsf_file.design_matrix:
        row=",".join(row)
        out_lines.append(row)
    height=len(out_lines)
    return out_lines,width,height

def me_to_csv(fsf_file):
    out_lines=list()
    width=2
    out_lines.append('Mixed Effects')
    out_lines.append("Analysis Name:,"+fsf_file.analysis_name)
    out_lines.append("Outpath:,"+fsf_file.output_path)
    out_lines.append("p-value:,"+fsf_file.p_value)
    out_lines.append("z-value:,"+fsf_file.z_value)
    out_lines.append(',')
    out_lines.append('Inputs:')
    for ind in range(1,int(fsf_file.number_subjects)+1):
        i=str(ind)
        line=fsf_file.inputs[i]
        out_lines.append(line)
    out_lines.append(',')
    height=len(out_lines)
    return out_lines,width,height


def fsf_to_one_column(fsf_file):
    if fsf_file.type == fsf_file.FIRST_TYPE:
        return first_to_csv_one_coloumn(fsf_file)
    elif fsf_file.type == fsf_file.FE_TYPE:
        return fe_to_csv_one_coloumn(fsf_file)
    elif fsf_file.type == fsf_file.ME_TYPE:
        return me_to_csv_one_coloumn(fsf_file)
    elif fsf_file.type == fsf_file.PRE_TYPE:
        return pre_to_csv_one_coloumn(fsf_file)
    else:
        return None

def pre_to_csv_one_coloumn(fsf_file):
    out_lines=list()
    out_lines.append("Preproc Name:,"+fsf_file.analysis_name)
    out_lines.append("Input file:,"+fsf_file.input_file)
    out_lines.append(',')
    out_lines.append("TR:, "+fsf_file.tr)
    out_lines.append("Total Volumes:, "+fsf_file.number_volumes)
    out_lines.append("Deleted Volumes:, "+fsf_file.removed_volumes)
    out_lines.append("Motion Correction:, "+fsf_file.motion_correction)
    out_lines.append("Brain Thresholding:, "+fsf_file.brain_thresh)
    out_lines.append("Smoothing:, "+fsf_file.smoothing)
    return out_lines

def first_to_csv_one_coloumn(fsf_file):
    out_lines=list()
    out_lines.append("First level Name:,"+fsf_file.analysis_name)
    out_lines.append("Input file:,"+fsf_file.input_file)
    out_lines.append(',')
    out_lines.append('Regressors:')
    for ind in range(1,len(fsf_file.evs)+1):
        out_lines.append(','+fsf_file.evs[str(ind)].name)
    out_lines.append('Contrasts:')
    for ind in range(1,len(fsf_file.cons)+1):
        out_lines.append(','+fsf_file.cons[str(ind)].name)
    return out_lines

def fe_to_csv_one_coloumn(fsf_file):
    out_lines=list()
    out_lines.append("FE Name:,"+fsf_file.analysis_name)
    out_lines.append("Input Count:, "+fsf_file.number_inputs)
    out_lines.append("Outpath:,"+fsf_file.output_path)
    out_lines.append('Inputs:')
    for ind in range(1,len(fsf_file.inputs)+1):
            out_lines.append(','+fsf_file.inputs[str(ind)])
    out_lines.append('Regressors:')
    for ind in range(1,len(fsf_file.evs)+1):
        out_lines.append(','+fsf_file.evs[str(ind)].name)
    out_lines.append('Contrasts:')
    for ind in range(1,len(fsf_file.cons)+1):
        out_lines.append(','+fsf_file.cons[str(ind)].name)
    return out_lines

def me_to_csv_one_coloumn(fsf_file):
    out_lines=list()
    out_lines.append("ME Name:,"+fsf_file.analysis_name)
    out_lines.append("Outpath:,"+fsf_file.output_path)
    out_lines.append("p-value:,"+fsf_file.p_value)
    out_lines.append("z-value:,"+fsf_file.z_value)
    out_lines.append("Num subjects:,"+fsf_file.number_subjects)
    out_lines.append(',')
    out_lines.append('Subjects:')
    for ind in range(1,len(fsf_file.inputs)+1):
        out_lines.append(','+fsf_file.inputs[str(ind)])
    return out_lines

def check_for_none(value):
    if value is None:
        return ""
    else:
        return value



