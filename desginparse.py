__author__ = 'Michael'
import argparse, os, ConfigParser,re
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
    #Parse options
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--featpath')
    parser.add_argument('-o', '--out')
    #parser.add_argument('-t', '--type')
    args=parser.parse_args()
    feat_folder_path=args.featpath
    #type=args.type
    out_path=args.out

    FIRST_dir="\\\\192.168.2.181\MyFiles\TAF_fanal\PV\Ctrl\\x305\\r2"
    FE_dir='\\\\192.168.2.181\MyFiles\TAF_fanal\PV\FE2\\'
    ME_dir='\\\\192.168.2.181\MyFiles\TAF_fanal\PV\ME\\'


    analysis='a8_csf'
    first_list=os.listdir(os.path.join(FIRST_dir))
    first_folder=''
    for folder in first_list:
        analysis_match=re.search(analysis, folder)
        if analysis_match:
            combined=os.path.join(FIRST_dir,folder)
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
        preprocdir=os.path.join(FIRST_dir,first_fsf.preproc)
        preproc_fsf=fsf_file((os.path.join(preprocdir,'design.fsf')))
        if preproc_fsf.height > height_of_all_lines:
            height_of_all_lines=preproc_fsf.height
    FE_fsf=fsf_file(os.path.join(FE_folder,'design.fsf'))
    if FE_fsf.height > height_of_all_lines:
        height_of_all_lines=preproc_fsf.height
    ME_fsf=fsf_file(os.path.join(ME_folders[0],'design.fsf'))
    if ME_fsf.height > height_of_all_lines:
        height_of_all_lines=preproc_fsf.height



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

    # Writing our configuration file to 'example.cfg'
    with open('example.cfg', 'wb') as configfile:
        config.write(configfile)


if __name__ == "__main__":
    main()



