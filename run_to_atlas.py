__author__ = 'michael'
import argparse, os, ConfigParser
from utils import *
from atlas_loc import atlas_loc
config_file_path='example.cfg'
def main():
    #Parse options
    parser = argparse.ArgumentParser()
    parser.add_argument('input')
    parser.add_argument('-s', '--study')
    parser.add_argument('-o', '--output')
    parser.add_argument('-hc', dest='harvard_cor',help="Harvard cortical flag",default=False,action="store_true")
    parser.add_argument('-hs', dest='harvard_sub',help="Harvard sub-cortical flag",default=False,action="store_true")
    parser.add_argument('-j', dest='jeulich',help="Harvard cortical flag",default=False,action="store_true")
    parser.add_argument('--add',dest='new_atlas',default=False)

    if os.path.isfile(config_file_path):
        config = ConfigParser.RawConfigParser()
        config.read(config_file_path)
        #noinspection PyUnusedLocal
        structure=config.get('run_to_atlas','structure').strip('/').split('/')
        reg_path=config.get('run_to_atlas','reg_path').strip('/').split('/')
        reg_name=config.get('run_to_atlas','reg_name')
        experiment_root=config.get('run_to_atlas','experiment_root')
        standard_brain=config.get("run_to_atlas","standard_brain")
        study_code=config.get("run_to_atlas","study_code")
    else:
        print "No Config file found"
        quit()

    args = parser.parse_args()
    atlases=dict()

    if args.harvard_cor:
        atlases['Harvard-Oxford Cortical Structural Atlas']=dict()
    if args.harvard_sub:
        atlases['Harvard-Oxford Subcortical Structural Atlas']=dict()
    if args.new_atlas:
        atlases[args.new_atlas]=dict()
    if args.jeulich:
        atlases['Juelich Histological Atlas']=dict()

    out_name=args.output
    study = args.study
    file_input = os.path.join(args.input)
    try:
        with file(file_input, 'r') as original:
            seed_lines = original.readlines()
    except IOError:
        print "Input file does not appear to be valid"
        seed_lines=None
        quit()

    wb = xlwt.Workbook()
    ws = wb.add_sheet('Sheet 1')
    atlas_locations = list()


    for seed_line in seed_lines:
        parsed_line = seed_line.strip().split(',')
        condition = parsed_line[0]
        subject = parsed_line[1]
        run = parsed_line[2]
        print subject+" "+run
        x = parsed_line[3]
        y = parsed_line[4]
        z = parsed_line[5]
        f = open('temp.txt', 'w')
        f.write(x + " " + y + " " + z)
        f.close()
        registration_path=''
        for item in reg_path:
                try:
                    path_part=eval(item)
                    registration_path=os.path.join(registration_path,path_part)
                except NameError:
                    registration_path=''
        if registration_path:
            example_func = os.path.join(registration_path, 'example_func')
            xfm = os.path.join(registration_path, 'example_func2standard.mat')
            if os.path.exists(xfm):
                command = ["img2stdcoord", "-img", example_func, "-xfm", xfm, "-std",standard_brain, "temp.txt"]
                p = subprocess.Popen(command, stdout=subprocess.PIPE)
                std_space_coords = p.stdout.readline().strip().split()
                std_x = std_space_coords[0]
                std_y = std_space_coords[1]
                std_z = std_space_coords[2]
                std_coords=(std_x,std_y,std_z)

                ##Have Standard Coordinates
                atlas_percentages=dict()
                for atlas in atlases:
                    atlas_dict=atlases[atlas]
                    percentages,atlas_dict=get_atlas_location(atlas, std_coords, atlas_dict)
                    atlas_percentages[atlas]=percentages
                    atlases[atlas]=atlas_dict
                atlas_location = atlas_loc(condition, subject, run, x, y, z, std_x, std_y, std_z, atlas_percentages)
                atlas_locations.append(atlas_location)

    os.remove('temp.txt')
    sorted_atlases=sort_atlas_locations(atlases)
    atlas_points,start_point = prep_worksheet(ws, sorted_atlases)
    count = start_point
    for atlas_location in atlas_locations:
        write_atlas_line(ws,atlas_location,count,atlas_points)
        count += 1

    wb.save(out_name)


if __name__ == "__main__":
    main()




