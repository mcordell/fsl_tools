__author__ = 'michael'
import re, subprocess, operator, os
from xlwt import easyxf

#Exceptions
class MalformedStructure(Exception):
    def __init__(self,value):
        super(MalformedStructure, self).__init__()
        self.value = value
    def __str__(self):
        return repr(self.value)

#Supplementary Classes
class atlas_loc:
    Name = "Atlas Location"
    def __init__(self, condition, subject, run, x, y, z, std_x, std_y, std_z, atlas_percentages):
        self.condition = condition
        self.subject = subject
        self.run = run
        self.x = x
        self.y = y
        self.z = z
        self.std_x = std_x
        self.std_y = std_y
        self.std_z = std_z
        self.atlas_percentages = atlas_percentages


#Supplementary functions
def get_input_fsf(inputs):
    valid_path=''
    input_count=1
    while not valid_path:
        raw_input=inputs[str(input_count)].strip('\"')
        input_path=get_feat_directory(raw_input)
        valid_path=input_path+'design.fsf'
        if not os.path.isfile(valid_path):
            input_count+=1
            valid_path=''
    if valid_path:
        return valid_path
    else:
        return None

def get_feat_directory(in_string):
    dir_match=re.search('\.(g)*feat',in_string)
    if dir_match:
        full_match_start,full_match_end=dir_match.regs[0]
        return in_string[0:full_match_end]+'/'
    else:
        return None

def write_report(lines,path):
    """
        Helper text write function
    """
    out_lines=list()
    for line in lines:
        line=line.strip('\n')
        line+='\n'
        out_lines.append(line)
    with file(path, 'w') as out:
        return out.writelines(out_lines)

def fill_line(line,width):
    """ helper function for making a csv line have a fixed number (width) of commas
        this is helpful for evening out all of the csv lines in a set to have equal
        "width"
    """
    comma_count=line.count(',')
    for i in range(0,(width-comma_count)):
        line+=','
    return line

def combine_left_right(left_csv, right_csv):
    left_width=find_width_of_csv(left_csv)
    left_height=len(left_csv)
    right_width=find_width_of_csv(right_csv)
    right_height=len(right_csv)
    out_lines=list()
    if left_height > right_height:
        total_height=left_height
    else:
        total_height=right_height
    for index in range(0,total_height):
        fullline=''
        if left_height > 0:
            if index < left_height:
                fullline+=fill_line(left_csv[index],left_width)
                fullline+=' , ,'
            else:
                fullline+=fill_line('',left_width)
                fullline+=' , ,'
        if right_height > 0:
            if index < right_height:
                fullline+=fill_line(right_csv[index],right_width)
            else:
                fullline+=fill_line('',right_width)
        out_lines.append(fullline)
    return out_lines


def find_width_of_csv(csv_lines):
    max_width=1
    for line in csv_lines:
        comma_count=line.count(',')
        if comma_count > max_width:
            max_width=comma_count
    return max_width
def combine_for_csv(first_csv,height_of_all_lines=0,preproc_csv=None,FE_csv=None,ME_csv=None):
    """ given atleast one fsf file, format fsf_file.out_lines into a csv file
        if more than one fsf_file is given. They will be organized according to stage
        preproc, first level, fixed effects, mixed effects
    """
    global preproc_csv_lines, preproc_csv_lines, ME_width, ME_width, ME_csv_lines, ME_csv_lines, FE_width, FE_width, FE_csv_lines, FE_csv_lines, preproc_width, preproc_width
    first_csv_lines,first_width,first_height=first_csv
    if preproc_csv is not None:
        preproc_csv_lines, preproc_width,preproc_height=preproc_csv
    if FE_csv is not None:
        FE_csv_lines, FE_width,FE_height=FE_csv
    if ME_csv is not None:
        ME_csv_lines, ME_width,ME_height=ME_csv

    if not height_of_all_lines:
        height_of_all_lines=first_height
    out_lines=list()
    for index in range(0,height_of_all_lines):
        fullline=''
        if preproc_csv is not None:
            if index < len(preproc_csv_lines):
                fullline+=fill_line(preproc_csv_lines[index],preproc_width)
                fullline+=' ,'
            else:
                fullline+=fill_line('',preproc_width)
                fullline+=' ,'

        if first_csv:
            if index < len(first_csv_lines):
                fullline+=fill_line(first_csv_lines[index],first_width)
                fullline+=' ,'
            else:
                fullline+=fill_line('',first_width)
                fullline+=' ,'
        if FE_csv:
            if index < len(FE_csv_lines):
                fullline+=fill_line(FE_csv_lines[index],FE_width)
                fullline+=' ,'
            else:
                fullline+=fill_line('',FE_width)
                fullline+=' ,'
        if ME_csv:
            if index < len(ME_csv_lines):
                fullline+=fill_line(ME_csv_lines[index],ME_width)
                fullline+=' ,'
            else:
                fullline+=fill_line('',ME_width)
                fullline+=' ,'
        fullline+='\n'
        out_lines.append(fullline)
    return out_lines


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
    #out_lines.append("Input file:,"+fsf_file.input_file)
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
    out_lines.append(',')
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
#    for ind in range(1,len(fsf_file.inputs)+1):
#        out_lines.append(','+fsf_file.subjects[str(ind)])
    return out_lines

def check_for_none(value):
    if value is None:
        return ""
    else:
        return value



