__author__ = 'Michael'
import argparse, os, re, ConfigParser
from fsf_file import fsf_file

def write_report(lines,path):
    with file(path, 'w') as out:
        return out.writelines(lines)

def fill_line(line,width):
    comma_count=line.count(',')
    for i in range(0,(width-comma_count)):
        line+=','
    return line

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


    first_list=os.listdir(os.path.join(first_level_dir))
    first_folder=''
    for folder in first_list:
        analysis_match=re.search(analysis, folder)
        if analysis_match:
            combined=os.path.join(first_level_dir,folder)
            if os.path.isdir(combined):
                first_folder=combined
                break

    FE_list=os.listdir(os.path.join(FE_dir))
    FE_folder=''
    for folder in FE_list:
        analysis_match=re.search(analysis, folder)
        if analysis_match:
            combined=os.path.join(FE_dir,folder)
            if os.path.isdir(combined):
                FE_folder=combined
                break
    ME_list=os.listdir(os.path.join(ME_dir))
    ME_folders=list()
    for folder in ME_list:
        analysis_match=re.search(analysis, folder)
        if analysis_match:
            combined=os.path.join(ME_dir,folder)
            if os.path.isdir(combined):
                ME_folders.append(combined)


    height_of_all_lines=0
    first_fsf=fsf_file(os.path.join(first_folder,'design.fsf'))
    if first_fsf.height > height_of_all_lines:
        height_of_all_lines=first_fsf.height
    if first_fsf.preproc:
        preprocdir=os.path.join(first_level_dir,first_fsf.preproc)
        preproc_fsf=fsf_file((os.path.join(preprocdir,'design.fsf')))
        if preproc_fsf.height > height_of_all_lines:
            height_of_all_lines=preproc_fsf.height
    FE_fsf=fsf_file(os.path.join(FE_folder,'design.fsf'))
    if FE_fsf.height > height_of_all_lines:
        height_of_all_lines=FE_fsf.height
    ME_fsf=fsf_file(os.path.join(ME_folders[0],'design.fsf'))
    if ME_fsf.height > height_of_all_lines:
        height_of_all_lines=FE_fsf.height



    preproc_lines=preproc_fsf.out_lines
    FE_lines=FE_fsf.out_lines
    first_lines=first_fsf.out_lines
    ME_lines=ME_fsf.out_lines
    out_lines=list()

    for index in range(0,height_of_all_lines):
        fullline=''
        if preproc_fsf:
            if index < len(preproc_lines):
                fullline+=fill_line(preproc_lines[index],preproc_fsf.width)
                fullline+=' ,'
            else:
                fullline+=fill_line('',preproc_fsf.width)
                fullline+=' ,'

        if first_fsf:
            if index < len(first_lines):
                fullline+=fill_line(first_lines[index],first_fsf.width)
                fullline+=' ,'
            else:
                fullline+=fill_line('',first_fsf.width)
                fullline+=' ,'
        if FE_fsf:
                if index < len(FE_lines):
                    fullline+=fill_line(FE_lines[index],FE_fsf.width)
                    fullline+=' ,'
                else:
                    fullline+=fill_line('',FE_fsf.width)
                    fullline+=' ,'
        if ME_fsf:
            if index < len(ME_lines):
                fullline+=fill_line(ME_lines[index],ME_fsf.width)
                fullline+=' ,'
            else:
                fullline+=fill_line('',ME_fsf.width)
                fullline+=' ,'
        fullline+='\n'
        out_lines.append(fullline)

    write_report(out_lines,out_path)

if __name__ == "__main__":
    main()



