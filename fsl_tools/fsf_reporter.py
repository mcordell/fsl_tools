#! /usr/bin/env python
__author__ = 'Michael'
import argparse
import os
import re
from utils import fsf_to_csv,fsf_to_one_column,write_report,combine_for_csv, get_input_fsf,combine_left_right
from fsf_file import FsfFile
from excel_results import ExcelResults
from configuration import Configuration
def die(message):
    if message:
        print message
    else:
        print "Unexplained Exit"
    exit()

def main():
    global ME_folders, first_fsf, FE_fsf, one_col, ME_csv, FE_csv, preproc_csv, first_csv, FE_dir, FE_dir, ME_dir, ME_dir, out_lines
    template_path="template2.xls"
    height_of_all_lines=0

    #Parse options
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--featpath')
    parser.add_argument('-o', '--out')
    parser.add_argument('-a', '--analysis')
    parser.add_argument('-c', '--config')
    parser.add_argument('-m','--manual_search')
    parser.add_argument('-s','--simple_output')
    args=parser.parse_args()
    config_file_path=args.config
    feat_folder_path=args.featpath
    simple_output=args.simple_output
    analysis=args.analysis

    if args.manual_search:
        search_down_method=0
    else:
        search_down_method=1
    if args.out is None:
        if analysis:
            out_path=analysis
        else:
            out_path=''
            die("Need to set output prefix with -o arg when using path to fsf (-p) arg")
    else:
        out_path=args.out

    #Check config file before
    if config_file_path is None:
        config_file_path="example.cfg"
    if feat_folder_path and analysis:
        die("Please use either -p <path to single feat folder> or\n"+
            "or -a <analysis name>. Not both.")

    configuration=Configuration(config_file_path)

    #find the location of the feat folders within the directories from the config file
    if analysis:
        #Search down switch
        if search_down_method:
            #find ME directories that match analysis pattern
            ME_list=os.listdir(os.path.join(configuration.ME_dir))
            ME_folders=list()
            for folder in ME_list:
                analysis_match=re.search(analysis+configuration.me_pattern, folder)
                if analysis_match:
                    combined=os.path.join(configuration.ME_dir,folder)
                    if os.path.isdir(combined):
                        ME_folders.append(combined)

            #Catch bad analysis name at ME Level
            if not ME_folders:
                die("No analysis folders found at ME level. Do you have the right analysis name?")

            #load any ME directory
            ME_fsf=FsfFile(os.path.join(ME_folders[0],'design.fsf'))
            ME_inputs=ME_fsf.inputs
            fe_fsf_path=''
            me_input_count=1
            while not fe_fsf_path:
                try:
                    fe_fsf_path=ME_inputs[str(me_input_count)].strip('\"')+'/design.fsf'
                except KeyError:
                    break
                if not os.path.isfile(fe_fsf_path):
                    me_input_count+=1
                    fe_fsf_path=''
            FE_fsf=FsfFile(fe_fsf_path)
            FE_inputs=FE_fsf.inputs
            other_FES=list()
            input_fsf_path=get_input_fsf(FE_inputs)
            input_fsf=FsfFile(input_fsf_path)
            while input_fsf.type == input_fsf.FE_TYPE:
                other_FES.append(input_fsf)
                input_fsf_path=get_input_fsf(input_fsf.inputs)
                input_fsf=FsfFile(input_fsf_path)
            first_fsf=input_fsf
            one_col=list()
            if first_fsf.type == first_fsf.FIRST_TYPE:
                one_col.extend(fsf_to_one_column(first_fsf))
                one_col.append(",\n")
                first_csv=fsf_to_csv(first_fsf)
                if hasattr(first_fsf,'preproc'):
                    preprocdir=os.path.join(configuration.first_level_dir,first_fsf.preproc)
                    preproc_fsf=FsfFile((os.path.join(preprocdir,'design.fsf')))
                    preproc_csv=fsf_to_csv(preproc_fsf)
                    one_col.extend(fsf_to_one_column(preproc_fsf))
                    one_col.append(",\n")
                else:
                    preproc_csv=None
            else:
                first_csv=None
                preproc_csv=None
                print "First level not loaded or design file is corrupt. Not adding to output"

            if FE_fsf.type == FE_fsf.FE_TYPE:
                one_col.append(",\n")
                FE_csv=fsf_to_csv(FE_fsf)
                one_col.extend(fsf_to_one_column(FE_fsf))
                one_col.append(",\n")
            else:
                FE_csv=None
                print "No fixed effects loaded, data will not be included in output"

            if ME_fsf:
                ME_csv=fsf_to_csv(ME_fsf)
                one_col.extend(fsf_to_one_column(ME_fsf))
                one_col.append(",\n")
            else:
                ME_csv=None
                print "No Mixed effects loaded, data will not be included in output"

            #out_lines=combine_for_csv(first_csv,height_of_all_lines,preproc_csv,FE_csv,ME_csv)
            out_lines=list()
            if first_csv:
                if preproc_csv:
                    out_lines=combine_left_right(preproc_csv[0],first_csv[0])
                else:
                    out_lines=first_csv[0]
            if FE_csv:
                if other_FES:
                    size_of_others=len(other_FES)-1
                    print size_of_others
                    while size_of_others >= 0:

                        print size_of_others
                        temp_csv=fsf_to_csv(other_FES[size_of_others])
                        out_lines=combine_left_right(out_lines,temp_csv[0])
                        size_of_others -= 1

                out_lines=combine_left_right(out_lines,FE_csv[0])
            if ME_csv:
                out_lines=combine_left_right(out_lines,ME_csv[0])
        else:
            #Old method of searching
            ME_list=os.listdir(os.path.join(configuration.ME_dir))
            ME_folders=list()
            for folder in ME_list:
                analysis_match=re.search(analysis+"_cope", folder)
                if analysis_match:
                    combined=os.path.join(configuration.ME_dir,folder)
                    if os.path.isdir(combined):
                        ME_folders.append(combined)

            first_list=os.listdir(os.path.join(configuration.first_level_dir))
            first_folder=''
            for folder in first_list:
                analysis_match=re.search(analysis+'.feat', folder)
                if analysis_match:
                    combined=os.path.join(configuration.first_level_dir,folder)
                    if os.path.isdir(combined):
                        first_folder=combined
                        break

            FE_list=os.listdir(os.path.join(configuration.FE_dir))
            FE_folder=''
            for folder in FE_list:
                analysis_match=re.search(analysis+'.gfeat', folder)
                if analysis_match:
                    combined=os.path.join(configuration.FE_dir,folder)
                    if os.path.isdir(combined):
                        FE_folder=combined
                        break

            one_col=list()

            #load fsf files using FsfFile class
            first_fsf=FsfFile(os.path.join(first_folder,'design.fsf'))
            if first_fsf.type == first_fsf.FIRST_TYPE:
                one_col.extend(fsf_to_one_column(first_fsf))
                one_col.append(",\n")
                first_csv=fsf_to_csv(first_fsf)
                if first_csv[2] > height_of_all_lines:
                    height_of_all_lines=first_csv[2]
                if hasattr(first_fsf,'preproc'):
                    preprocdir=os.path.join(configuration.first_level_dir,first_fsf.preproc)
                    preproc_fsf=FsfFile((os.path.join(preprocdir,'design.fsf')))
                    preproc_csv=fsf_to_csv(preproc_fsf)
                    one_col.extend(fsf_to_one_column(preproc_fsf))
                    one_col.append(",\n")
            else:
                print "First level not loaded or design file is corrupt. Not adding to output"


            FE_fsf=FsfFile(os.path.join(FE_folder,'design.fsf'))
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

            ME_fsf=FsfFile(os.path.join(ME_folders[0],'design.fsf'))
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
            FE_fsf=FsfFile(os.path.join("/Volumes/storage/TAF_fanal/PV/FE2/x301fe_a5t.gfeat/design.fsf"))
            fe_cope_names=dict()
            for item in FE_fsf.cons.items():
                key,contrast=item
                fe_cope_names[key]=contrast.name

        first_cope_names=dict()
        for item in first_fsf.cons.items():
            key,contrast=item
            first_cope_names[key]=contrast.name

        if simple_output is None:
            excel=excel_results(fe_cope_names,first_cope_names, ME_folders, template_path,excel_output_path)
            excel.main()
    elif feat_folder_path :
        fsf_single=FsfFile(os.path.join(feat_folder_path))
        fsf_csv=combine_for_csv(fsf_to_csv(fsf_single))
        one_lines=list()
        for row in fsf_to_one_column(fsf_single):
            one_lines.append(row+'\n')
        write_report(fsf_csv,out_path+'.csv')
        write_report(one_lines,out_path+'_one.csv')

if __name__ == "__main__":
    main()
