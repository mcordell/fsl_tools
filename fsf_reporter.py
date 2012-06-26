__author__ = 'Michael'
import argparse, os, re, ConfigParser
from utils import fsf_to_csv,fsf_to_one_column,write_report,fill_line,combine_for_csv
from fsf_file import fsf_file
from excel_results import excel_results

def main():
    global first_level_dir, ME_folders, first_fsf, FE_fsf, one_col, ME_csv, FE_csv, preproc_csv, first_csv, FE_dir, FE_dir, ME_dir, ME_dir
    #Parse options
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--featpath')
    parser.add_argument('-o', '--out')
    parser.add_argument('-a', '--analysis')
    parser.add_argument('-c', '--config')
    args=parser.parse_args()
    config_file_path=args.config
    feat_folder_path=args.featpath
    analysis=args.analysis
    out_path=args.out
    if config_file_path is None:
        config_file_path="example.cfg"
    if feat_folder_path and analysis:
        print "Please use either -p <path to single feat folder> or"
        print "or -a <analysis name>. Not both."
        exit()

    template_path="template2.xls"
    # read configuration file
    if os.path.isfile(config_file_path):
        config = ConfigParser.RawConfigParser()
        config.read(config_file_path)
        first_level_dir = config.get('Analysis Directories', 'first_level_dir')
        FE_dir = config.get('Analysis Directories', 'fe_dir')
        ME_dir = config.get('Analysis Directories', 'me_dir')
        template_path=config.get('Analysis Directories', 'template')

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
            FE_csv=None
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
        #prep fe names
        if hasattr(FE_fsf, 'cons'):
            fe_cope_names=dict()
            for item in FE_fsf.cons.items():
                key,contrast=item
                fe_cope_names[key]=contrast.name
        else:
            #TODO FE hack for the screwed up stroops. Remove after done.
            FE_fsf=fsf_file(os.path.join("/Volumes/storage/TAF_fanal/PV/FE2/x301fe_a5t.gfeat/design.fsf"))
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
            excel=excel_results(fe_cope_names,first_cope_names, ME_folders, template_path,excel_output_path)
            excel.main()
    elif feat_folder_path :
        fsf_single=fsf_file(os.path.join(feat_folder_path))
        fsf_csv=combine_for_csv(fsf_to_csv(fsf_single))
        one_lines=list()
        for row in fsf_to_one_column(fsf_single):
            one_lines.append(row+'\n')
        write_report(fsf_csv,out_path+'.csv')
        write_report(one_lines,out_path+'_one.csv')

if __name__ == "__main__":
    main()



