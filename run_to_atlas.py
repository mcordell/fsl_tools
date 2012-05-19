__author__ = 'michael'
import argparse, os, re, subprocess, xlwt, operator
from xlwt import easyxf

fanal = "/mnt/Storage/TAF_fanal/"

class atlas_loc:
    Name = "Atlas Location"
    def __init__(self, condition, subject, run, x, y, z, std_x, std_y, std_z, atlas_cort, atlas_sub_cort):
        self.condition = condition
        self.subject = subject
        self.run = run
        self.x = x
        self.y = y
        self.z = z
        self.std_x = std_x
        self.std_y = std_y
        self.std_z = std_z
        self.atlas_cort = atlas_cort
        self.atlas_sub_cort = atlas_sub_cort


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


def prep_workbook(ws, sorted_cort, sorted_sub):
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
    atlas_count = 10
    cort_points = dict()
    for atlas_tuple in sorted_cort:
        key, value = atlas_tuple
        ws.write(1, atlas_count, key)
        cort_points[key] = atlas_count
        atlas_count += 1

    end_value = atlas_count-1
    ws.write_merge(0, 0, 10, end_value, 'Harvard Cortical', green_style)
    sub_cort_points = dict()
    for atlas_tuple in sorted_sub:
        key, value = atlas_tuple
        ws.write(1, atlas_count, key)
        sub_cort_points[key] = atlas_count
        atlas_count += 1
    ws.write_merge(0, 0, end_value + 1, atlas_count, 'Harvard Sub-Cortical', yellow_style)
    return cort_points, sub_cort_points


def main():
    #Parse options
    parser = argparse.ArgumentParser()
    parser.add_argument('input')
    parser.add_argument('-s', '--study')
    parser.add_argument('-o', '--output')
    args = parser.parse_args()
    out_name=args.output
    study = args.study
    file_input = os.path.join(args.input)
    try:
        with file(file_input, 'r') as original:
            seed_lines = original.readlines()
    except:
        print "Input file does not appear to be valid"
        quit()
    wb = xlwt.Workbook()
    ws = wb.add_sheet('Sheet 1')
    atlas_locations = list()
    sub_cort_locations = dict()
    cort_locations = dict()
    for seed_line in seed_lines:
        parsed_line = seed_line.strip().split(',')
        condition = parsed_line[0]
        subject = parsed_line[1]
        run = parsed_line[2]
        x = parsed_line[3]
        y = parsed_line[4]
        z = parsed_line[5]
        f = open('temp.txt', 'w')
        f.write(x + " " + y + " " + z)
        f.close()
        print condition + " " + subject + " " + run
        qreg_path = os.path.join(fanal, study, condition, subject, run, 'qreg_8s')
        example_func = os.path.join(qreg_path, 'example_func')
        xfm = os.path.join(qreg_path, 'example_func2standard.mat')

        command = ["img2stdcoord", "-img", example_func, "-xfm", xfm, "-std",
                   "/usr/share/fsl/data/standard/MNI152_T1_2mm_brain", "temp.txt"]
        p = subprocess.Popen(command, stdout=subprocess.PIPE)
        std_space_coords = p.stdout.readline().strip().split()
        print std_space_coords
        std_x = std_space_coords[0]
        std_y = std_space_coords[1]
        std_z = std_space_coords[2]
        print std_x + " " + std_y + " " + std_z
        command_2 = ["atlasquery", "-a", "Harvard-Oxford Cortical Structural Atlas", "-c",
                     str(std_x) + "," + str(std_y) + "," + str(std_z)]
        p_one = subprocess.Popen(command_2, stdout=subprocess.PIPE)
        atlas_one_lines = p_one.stdout.readlines()
        command_3 = ["atlasquery", "-a", "Harvard-Oxford Subcortical Structural Atlas", "-c",
                     str(std_x) + "," + str(std_y) + "," + str(std_z)]
        p_two = subprocess.Popen(command_3, stdout=subprocess.PIPE)
        atlas_two_lines = p_two.stdout.readlines()
        atlas_1 = atlas_one_lines[0].split("<b>Harvard-Oxford Cortical Structural Atlas</b><br>")[1]
        atlas_2 = atlas_two_lines[0].split("<b>Harvard-Oxford Subcortical Structural Atlas</b><br>")[1]
        cort_percentages,cort_locations = add_to_dict(atlas_1, cort_locations)
        sub_cort_percentages,sub_cort_locations = add_to_dict(atlas_2, sub_cort_locations)
        atlas_location = atlas_loc(condition, subject, run, x, y, z, std_x, std_y, std_z, cort_percentages,
            sub_cort_percentages)
        atlas_locations.append(atlas_location)

    sorted_cort_locations = sorted(cort_locations.iteritems(), key=operator.itemgetter(1), reverse=True)
    sorted_sub_locations = sorted(sub_cort_locations.iteritems(), key=operator.itemgetter(1), reverse=True)
    cort_points, sub_cort_points = prep_workbook(ws, sorted_cort_locations, sorted_sub_locations)
    for val in cort_points.keys():
        print val
    count = 2
    sty_atlas=easyxf(num_format_str="0%")
    for atlas_location in atlas_locations:
        ws.write(count, 1, atlas_location.condition)
        ws.write(count, 2, atlas_location.subject)
        ws.write(count, 3, atlas_location.run)
        ws.write(count, 4, int(atlas_location.x))
        ws.write(count, 5, int(atlas_location.y))
        ws.write(count, 6, int(atlas_location.z))
        ws.write(count, 7, float(atlas_location.std_x))
        ws.write(count, 8, float(atlas_location.std_y))
        ws.write(count, 9, float(atlas_location.std_z))
        cortical_values = atlas_location.atlas_cort
        print cortical_values
        sub_cortical_values = atlas_location.atlas_sub_cort
        print sub_cortical_values
        for cort_key in cortical_values.keys():
            cort_point = cort_points[cort_key]
            cort_value = float(cortical_values[cort_key].strip().strip("%"))/100
            ws.write(count, cort_point, cort_value,sty_atlas)
        for sub_cort_key in sub_cortical_values.keys():
            sub_cortical_value=float(sub_cortical_values[sub_cort_key].strip().strip("%"))/100
            ws.write(count, sub_cort_points[sub_cort_key], sub_cortical_value,sty_atlas)
        count += 1

    wb.save(out_name)

if __name__ == "__main__":
    main()




