__author__ = 'Michael'
import argparse, os, re, ConfigParser
from utils import fsf_to_csv,fsf_to_one_column
from fsf_file import fsf_file
from excel_results import excel_results

def write_report(lines,path):
    """
        Helper text write function
    """
    with file(path, 'w') as out:
        return out.writelines(lines)

def fill_line(line,width):
    """ helper function for making a csv line have a fixed number (width) of commas
        this is helpful for evening out all of the csv lines in a set to have equal
        "width"
    """
    comma_count=line.count(',')
    for i in range(0,(width-comma_count)):
        line+=','
    return line

def combine_for_csv(first_csv,height_of_all_lines=0,preproc_csv=None,FE_csv=None,ME_csv=None):
    """ given atleast one fsf file, format fsf_file.out_lines into a csv file
        if more than one fsf_file is given. They will be organized according to stage
        preproc, first level, fixed effects, mixed effects
    """
    first_csv_lines,first_width,first_height=first_csv
    if preproc_csv is not None:
        preproc_csv_lines, preproc_width,preproc_height=preproc_csv
    if FE_csv is not None:
        FE_csv_lines, FE_width,FE_height=FE_csv
    if ME_csv is not None:
        ME_csv_lines, ME_width,ME_height=ME_csv

    if height_of_all_lines == 0:
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

def main():
    config_file_path="example.cfg"
    #Parse options
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--featpath')
    parser.add_argument('-o', '--out')
    parser.add_argument('-a', '--analysis')
    args=parser.parse_args()
    feat_folder_path=args.featpath
    analysis=args.analysis
    out_path=args.out

    if (feat_folder_path and analysis):
        print "Please use either -p <path to single feat folder> or"
        print "or -a <analysis name>. Not both."
        exit()

    # read configuration file
    if os.path.isfile(config_file_path):
        config = ConfigParser.RawConfigParser()
        config.read(config_file_path)
        first_level_dir = config.get('Analysis Directories', 'first_level_dir')
        FE_dir = config.get('Analysis Directories', 'fe_dir')
        ME_dir = config.get('Analysis Directories', 'me_dir')

    height_of_all_lines=0

    #find the location of the feat folders within the directories from the config file
    if analysis:
        ME_list=os.listdir(os.path.join(ME_dir))
        ME_folders=list()
        for folder in ME_list:
            analysis_match=re.search(analysis+"_cope", folder)
            if analysis_match:
                combined=os.path.join(ME_dir,folder)
                if os.path.isdir(combined):
                    ME_folders.append(combined)

        first_list=os.listdir(os.path.join(first_level_dir))
        first_folder=''
        for folder in first_list:
            analysis_match=re.search(analysis+'.feat', folder)
            if analysis_match:
                combined=os.path.join(first_level_dir,folder)
                if os.path.isdir(combined):
                    first_folder=combined
                    break

        FE_list=os.listdir(os.path.join(FE_dir))
        FE_folder=''
        for folder in FE_list:
            analysis_match=re.search(analysis+'.gfeat', folder)
            if analysis_match:
                combined=os.path.join(FE_dir,folder)
                if os.path.isdir(combined):
                    FE_folder=combined
                    break
                    
        one_col=list()

        #load fsf files using fsf_file class
        first_fsf=fsf_file(os.path.join(first_folder,'design.fsf'))
        if first_fsf.type == first_fsf.FIRST_TYPE:
            one_col.extend(fsf_to_one_column(first_fsf))
            one_col.append(",\n")
            first_csv=fsf_to_csv(first_fsf)
            if first_csv[2] > height_of_all_lines:
                height_of_all_lines=first_csv[2]
            if hasattr(first_fsf,'preproc'):
                preprocdir=os.path.join(first_level_dir,first_fsf.preproc)
                preproc_fsf=fsf_file((os.path.join(preprocdir,'design.fsf')))
                preproc_csv=fsf_to_csv(preproc_fsf)
                one_col.extend(fsf_to_one_column(preproc_fsf))
                one_col.append(",\n")
        else:
            print "First level not loaded or design file is corrupt. Not adding to output"


        FE_fsf=fsf_file(os.path.join(FE_folder,'design.fsf'))
        if FE_fsf.type == FE_fsf.FE_TYPE:
            one_col.append(",\n")
            FE_csv=fsf_to_csv(FE_fsf)
            if FE_csv[2] > height_of_all_lines:
                height_of_all_lines=FE_csv[2]
            one_col.extend(fsf_to_one_column(FE_fsf))
            one_col.append(",\n")
        else:
            print "No fixed effects loaded, data will not be included in output"

        ME_fsf=fsf_file(os.path.join(ME_folders[0],'design.fsf'))
        if ME_fsf:
            ME_csv=fsf_to_csv(ME_fsf)
            if ME_csv[2] > height_of_all_lines:
                height_of_all_lines=ME_csv[2]
            one_col.extend(fsf_to_one_column(ME_fsf))
            one_col.append(",\n")
        else:
            print "No Mixed effects loaded, data will not be included in output"
    
    out_lines=combine_for_csv(first_csv,height_of_all_lines,preproc_csv,FE_csv,ME_csv)



    new_one=list()
    for row in one_col:
        new_one.append(row+'\n')

    write_report(out_lines,out_path+".csv")
    write_report(new_one,out_path+"_one.csv")

    excel_output_path=out_path+'.xls'


#    #prep fe names
    fe_cope_names=dict()
    for item in FE_fsf.cons.items():
        key,contrast=item
        fe_cope_names[key]=contrast.name

    first_cope_names=dict()
    for item in first_fsf.cons.items():
        key,contrast=item
        first_cope_names[key]=contrast.name

    #TODO need to figure out logic for not double FEs
    if excel_output_path:
        #TODO need to make template file more flexible
        template_path="template2.xls"
        excel=excel_results(fe_cope_names,first_cope_names, ME_folders, template_path,excel_output_path)
        excel.main()

if __name__ == "__main__":
    main()



