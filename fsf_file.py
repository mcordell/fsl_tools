__author__ = 'Michael'
import re
from utils import parse_to_dict

class fsf_file:

    Name = "FSF File"
    def __init__(self, path):
        #Define constants
        self.FE_TYPE=2
        self.ME_TYPE=3
        self.FIRST_TYPE=1
        self.PRE_TYPE=0
        self.FilePath=path
        self.fsf_lines=self.load_file()
        if self.fsf_lines:
            self.values_dict=parse_to_dict(self.fsf_lines)
            self.type=self.get_type()
            if type:
                #populate the values common to all fsf's
                self.output_path=self.get_value("outputdir")
                self.analysis_name=self.get_analysis_name(self.output_path)
                self.z_value=self.get_value("z_thresh")
                self.p_value=self.get_value("prob_thresh")
                self.fill_values_from_dict()

            self.parsed=self.parse_design_file(self.fsf_lines,self.type)
            self.out_lines=self.parsed_to_csv_lines(self.parsed,self.type)
            self.explode_parsed(self.parsed)
            self.one_col=self.get_one_column(self.parsed,self.type)


    def get_value(self,value_id):
        packaged_value="fmri("+value_id+")"
        if self.values_dict.has_key(value_id):
            return self.values_dict[value_id]
        elif self.values_dict.has_key(packaged_value):
            return self.values_dict[packaged_value]
        else:
            return None

    def get_type(self):
        #determine fsf file type
        high_value=self.get_value("level")
        analysis_type=self.get_value("analysis")
        type=None
        if (high_value != "1"):
            higher_level_type=self.get_value("mixed_yn")
            if higher_level_type == "0" or higher_level_type == "2" or higher_level_type == "1":
                type=self.ME_TYPE
            elif higher_level_type == "3":
                type=self.FE_TYPE
        elif (analysis_type == "6" or analysis_type == "7"):
            type=self.FIRST_TYPE
        elif (analysis_type == "1"):
            type=self.PRE_TYPE
        return type

    def load_file(self):
        """Loads file specified as path, returns lines as list"""
        try:
            with file(self.FilePath, 'r') as original:
                return original.readlines()
        except:
            print "Could not open fsf"

    def get_analysis_name(self,output_dir_string):
        analysis_name=None
        run=None
        if self.type == self.ME_TYPE:
            run=re.search("ME",output_dir_string)
        elif self.type == self.FIRST_TYPE or type == self.PRE_TYPE:
            run=re.search("r\d\/",output_dir_string)
        elif self.type == self.FE_TYPE:
            run=re.search("FE\d*",output_dir_string)
        if run:
            analysis_name=self.get_fsf_value(output_dir_string,run.end())
            if type == self.ME_TYPE:
                analysis_name=self.strip_cope(analysis_name)
        return analysis_name

    def binary_value_to_yes_no(self,value):
        if value == "1":
            value = "Y"
        elif value is not None:
            value = "N"
        return value

    def fill_pre(self):
        self.tr=self.get_value("tr")
        self.smoothing=self.get_value("smooth")
        self.number_volumes=self.get_value("npts")
        self.removed_volumes=self.get_value("ndelete")
        self.motion_correction=self.binary_value_to_yes_no(self.get_value("mc"))
        self.brain_thresh=self.get_value("brain_thresh")
        input_value=self.get_value("feat_files(1)")
        if input_value:
            self.input_file=self.strip_root()

    def fill_first_level(self):
        input_value=self.get_value("feat_files(1)")
        if input_value:
            self.input_file=self.strip_root(input_value)
        number_of_evs=int(self.get_value("evs_orig"))
        number_of_copes=int(self.get_value("ncon_orig"))
        design_matrix=[['0' for col in range(number_of_evs+2)] for row in range(number_of_copes+1)]
        design_matrix[0][0]="Cope #"
        design_matrix[0][1]="Cope Name"
        self.evs=dict()
        self.cons=dict()
        for ind in range(1,number_of_evs+1):
            index=str(ind)
            ev_1=ev()
            ev_1.name=self.get_value("evtitle"+index)
            ev_1.file_path=self.get_value("custom"+index)
            ev_1.set_convolution(self.get_value("convolve"+index))
            ev_1.temporal_deriv=self.binary_value_to_yes_no(self.get_value("deriv_yn"+index))
            ev_1.temporal_filtering=self.binary_value_to_yes_no(self.get_value("tempfilt_yn"+index))
            design_matrix[0][ind+1]=ev_1.name
            self.evs[index]=ev_1

        for ind in range(1,number_of_copes+1):
            index=str(ind)
            con=contrast()
            con.name=self.get_value("conname_orig."+index)
            con.ev_list=dict()
            real_cope_index=1
            design_matrix[ind][0]=index
            design_matrix[ind][1]=con.name
            for j in range (1,number_of_evs+1):
                ev_value=self.get_value("con_real"+index+"."+str(real_cope_index))
                con.ev_list[str(j)]=ev_value
                design_matrix[ind][j+1]=ev_value
                if self.evs[str(j)].temporal_deriv == "Y":
                    real_cope_index +=2
                else:
                    real_cope_index+=1
            self.cons[index]=con
        self.design_matrix=design_matrix

    def fill_FE(self):
        number_of_evs=int(self.get_value("evs_orig"))
        number_of_copes=int(self.get_value("ncon_orig"))
        self.number_inputs=self.get_value("npts")
        self.inputs=dict()
        self.stripped_inputs=dict()
        #prep matrices
        regress_matrix=[['0' for col in range(int(self.number_inputs)+1)] for row in range(number_of_evs+1)]
        design_matrix=[['0' for col in range(number_of_evs+2)] for row in range(number_of_copes+1)]
        design_matrix[0][0]="Cope #"
        design_matrix[0][1]="Cope Name"
        regress_matrix[0][0]="EV Name"
        #fill indices
        for ind in range(1,int(self.number_inputs)+1):
            index=str(ind)
            input_value=self.get_value("feat_files("+index+")")
            self.inputs[index]=input_value
            input_value=input_value.strip("\n")
            input_value=input_value.strip('\"')
            self.stripped_inputs[index]=input_value
            regress_matrix[0][ind]=index
        #populate evs and regressor matrix
        self.evs=dict()
        for ind in range(1,number_of_evs+1):
            index=str(ind)
            ev_temp=ev()
            ev_temp.name=self.get_value("evtitle"+index)
            regress_matrix[ind][0]=ev_temp.name
            design_matrix[0][ind+1]=ev_temp.name
            ev_temp.input_list=dict()
            for j in range(1,int(self.number_inputs)+1):
                jstr=str(j)
                input_val=self.get_value("evg"+jstr+"."+index)
                regress_matrix[ind][j]=input_val
                ev_temp.input_list[jstr]=input_val
            self.evs[index]=ev_temp

        #populate the copes and contrast matrix
        self.cons=dict()
        for ind in range(1,number_of_copes+1):
            index=str(ind)
            con=contrast()
            con.name=self.get_value("conname_orig."+index)
            con.ev_list=dict()
            real_cope_index=1
            design_matrix[ind][0]=index
            design_matrix[ind][1]=con.name
            for j in range (1,number_of_evs+1):
                ev_value=self.get_value("con_real"+index+"."+str(real_cope_index))
                con.ev_list[str(j)]=ev_value
                design_matrix[ind][j+1]=ev_value
                real_cope_index+=1
            self.cons[index]=con
        self.design_matrix=design_matrix
        self.regressor_matrix=regress_matrix

    def fill_ME(self):
        self.number_subjects=self.get_value("npts")
        self.inputs=dict()
        self.stripped_inputs=dict()
        for ind in range(1,int(self.number_subjects)+1):
            index=str(ind)
            input_value=self.get_value("feat_files("+index+")")
            self.inputs[index]=input_value
            input_value=input_value.strip("\n")
            input_value=input_value.strip('\"')
            input_value=self.strip_cope(input_value)
            self.stripped_inputs[index]=input_value

        
    def fill_values_from_dict(self):
        if self.type == self.PRE_TYPE:
            self.fill_pre()
        elif self.type == self.FIRST_TYPE:
            self.fill_first_level()
        elif self.type == self.FE_TYPE:
            self.fill_FE()
        elif self.type == self.ME_TYPE:
            self.fill_ME()



    def fill_matrix(self,def_lines, design_matrix, type, column_add, *real_copes):
        """Converts the cope lines/regressor lines into a more understandable matrix"""
        #unpack tuple
        if 'real_copes' in locals():
            if real_copes:
                print real_copes
                real_copes=real_copes[0]
        row=len(design_matrix)
        col=len(design_matrix[1])
        for line in def_lines:
            if type == self.FIRST_TYPE or type == self.FE_TYPE:
                match=re.search("fmri\(con_real\d+\.\d+\)", line)
            else:
                match=re.search("fmri\(evg\d+\.\d+\)", line)
            sub_match=re.findall("\d+",match.group())
            index=int(sub_match[0])
            sub_index=int(sub_match[1])
            value=self.get_fsf_value(line,match.end())
            if type == self.FIRST_TYPE:
                if 'real_copes' in locals():
                    if str(sub_index) in real_copes:
                        list_index=real_copes.index(str(sub_index))
                        list_index+=1
                        design_matrix[index][list_index+column_add]=value
            elif type == self.FE_TYPE:
                if sub_index < col and index < row:
                    design_matrix[index][sub_index+column_add]=value
            elif type == 5:
                design_matrix[sub_index][index]=value
        return design_matrix

    def get_one_column(self,parsed_data,type):
        """ Format parsed data as a single column for a csv
        """
        width = 2
        if type == self.FIRST_TYPE:
            analysis_name,output_path,in_file,design_matrix,ev_names,ev_paths,ev_convolves,ev_deriv,ev_temp,cope_names= parsed_data
        elif type == self.ME_TYPE:
            analysis_name,output_path,pvalue,zvalue,feat_paths,count,FE_example_dir = parsed_data
        elif type == self.FE_TYPE:
            analysis_name,output_path,feat_paths,count,design_matrix,regressor_matrix,ev_names,cope_names,first_example_dir=parsed_data
        elif type == self.PRE_TYPE:
            analysis_name,output_path,tr,total_volumes,deleted,in_file,motion_correction,brain_thresh,smoothing=parsed_data

        out_lines=list()
        if type == self.FIRST_TYPE:
            prepend='First Level'
        elif type == self.FE_TYPE:
            prepend='Fixed Effects'
        elif type == self.ME_TYPE:
            prepend='Mixed Effects'
        elif type == self.PRE_TYPE:
            prepend='Preproc'

        out_lines.append(prepend+" Name:,"+analysis_name)
        if type == self.FIRST_TYPE or self.PRE_TYPE:
            out_lines.append("Input file:,"+in_file);
            out_lines.append(',')
        if type == self.FE_TYPE:
            out_lines.append("Input Count:, "+count)
        if type == self.ME_TYPE or type == self.FE_TYPE:
            out_lines.append("Outpath:,"+output_path)
        if type == self.ME_TYPE:
            out_lines.append("p-value:,"+pvalue)
            out_lines.append("z-value:,"+zvalue)
            out_lines.append("Num subjects:,"+count)
            out_lines.append(',')

        if  type == self.FE_TYPE:
            out_lines.append('Inputs:')
            for ind in range(1,len(feat_paths)+1):
                i=str(ind)
                line=feat_paths[i]
                out_lines.append(','+line)

        #TODO: Subject pattern is hardcocded here
        if type == self.ME_TYPE:
            out_lines.append('Subjects:')
            for ind in range(1,len(feat_paths)+1):
                i=str(ind)
                line=feat_paths[i]
                value=re.search("x\d\d\d",line)
                out_lines.append(','+value.group(0))

        if type == self.FIRST_TYPE or type == self.FE_TYPE:
            out_lines.append('Regressors:')
            for ind in range(1,len(ev_names)+1):
                i=str(ind)
                line=','+ev_names[i]
                out_lines.append(line)
            out_lines.append(',')
        if type == self.FIRST_TYPE or type == self.FE_TYPE:
            out_lines.append('Contrasts:')
            for ind in range(1,len(cope_names)+1):
                i=str(ind)
                row=","+cope_names[i]
                out_lines.append(row)
        if type == self.PRE_TYPE:
           tr,total_volumes,deleted,in_file,motion_correction,brain_thresh,smoothing
           out_lines.append("TR:, "+tr)
           out_lines.append("Total Volumes:, "+total_volumes)
           out_lines.append("Deleted Volumes:, "+deleted)
           out_lines.append("Motion Correction:, "+motion_correction)
           out_lines.append("Brain Thresholding:, "+brain_thresh)
           out_lines.append("Smoothing:, "+smoothing)
        return out_lines





    def parse_design_file(self,fsf_lines, type):
        """
            Parses design file information and return information in parsed variables that can be used by the csv methods
        """
        analysis_name=''
        output_path=''
        zvalue=''
        pvalue=''

        if type == self.FIRST_TYPE or self.PRE_TYPE:
            in_file=''
        if type == self.FIRST_TYPE:
            ev_convolves=dict()
            ev_paths=dict()
            ev_deriv=dict()
            ev_temp=dict()
        if type == self.ME_TYPE or type == self.FE_TYPE:
            feat_paths=dict()
            count=''
        if type == self.FIRST_TYPE or type == self.FE_TYPE:
            ev_names=dict()
            evg_lines=list()
            cope_names=dict()
            cope_def_lines=list()
        if type == self.PRE_TYPE:
            tr=''
            total_volumes=''
            brain_thresh=''
            motion_correction=''
            smoothing=''
            deleted=''
        if type == self.FE_TYPE:
            first_example_dir=''
        if type == self.ME_TYPE:
            FE_example_dir=''

        for line in fsf_lines:
            #regex matching
            #all
            output_match=re.search("set fmri\(outputdir\)",line)
            feat_file_match=re.search("feat_files\(\d+\)",line)
            total_vols_match=re.search("fmri\(npts\)", line)
            z_match=re.search("set fmri\(z_thresh\)",line)
            p_match=re.search("set fmri\(prob_thresh\)",line)
    
            if output_match:
                output_path=self.get_fsf_value(line,output_match.end())
                #TODO hardcoded stripping here, make flexible
                if type == self.ME_TYPE:
                    run=re.search("ME",line)
                elif type == self.FIRST_TYPE or type == self.PRE_TYPE:
                    run=re.search("r\d\/",line)
                elif type == self.FE_TYPE:
                    run=re.search("FE\d*",line)
                if run:
                    analysis_name=self.get_fsf_value(line,run.end())
                if type == self.ME_TYPE:
                    analysis_name=self.strip_cope(analysis_name)
    
            if total_vols_match:
                value=self.get_fsf_value(line,total_vols_match.end())
                if type == self.ME_TYPE or type == self.FE_TYPE:
                    count=value
            if z_match:
                value=self.get_fsf_value(line,z_match.end())
                zvalue=value
    
            if p_match:
                value=self.get_fsf_value(line,p_match.end())
                pvalue=value
    
            if feat_file_match:
                if type == self.FIRST_TYPE or type == self.PRE_TYPE:
                    value=self.get_fsf_value(line,feat_file_match.end())
                    in_file=self.strip_root(value)
                    preproc_match=re.search("preproc.*feat",value)
                    #TODO inconsistent methodology here
                    if preproc_match:
                        self.preproc=value[preproc_match.start():preproc_match.end()]
                        print self.preproc
                elif type == self.ME_TYPE or type == self.FE_TYPE:
                    value=self.get_fsf_value(line,feat_file_match.end())
                    index=self.get_fsf_indice(feat_file_match.group())
                    stripped=self.strip_experiment_root(line)
                    feat_paths[index]=stripped
                    if (type == self.ME_TYPE and not FE_example_dir) or (type == self.FE_TYPE and not first_example_dir):
                        set_match=re.search("set feat_files\(\d+\) \"",line)
                        no_cope=line[set_match.end():len(line)]
                        no_cope=no_cope.strip('\n')
                        no_cope=no_cope.strip('\"')
                        no_cope=self.strip_cope(no_cope)
                        if type == self.ME_TYPE:
                            FE_example_dir=no_cope
                        else:
                            first_example_dir=no_cope

            if type == self.PRE_TYPE:
                tr_match=re.search("fmri\(tr\)", line)
                mc_match=re.search("set fmri\(mc\)",line)
                smooth_match=re.search("set fmri\(smooth\)",line)
                total_vols_match=re.search("fmri\(npts\)", line)
                removed_volumes=re.search("fmri\(ndelete\)", line)
                thresh_match=re.search("set fmri\(brain_thresh\)",line)

                if tr_match:
                    tr=self.get_fsf_value(line,tr_match.end())
                if mc_match:
                    value=self.get_fsf_value(line,mc_match.end())
                    if value == "1":
                        value = "Y"
                    else:
                        value = "N"
                    motion_correction=value
                if smooth_match:
                    smoothing=self.get_fsf_value(line,smooth_match.end())
                if removed_volumes:
                    deleted=self.get_fsf_value(line,removed_volumes.end())
                if total_vols_match:
                    total_volumes=self.get_fsf_value(line,total_vols_match.end())
                if thresh_match:
                    brain_thresh=self.get_fsf_value(line,thresh_match.end())


            if type == self.FIRST_TYPE:
                ev_conv_match=re.search("fmri\(convolve\d+\)", line)
                ev_path_match=re.search("fmri\(custom\d+\)", line)
                ev_deriv_match=re.search("fmri\(deriv_yn\d+\)", line)
                ev_temps_match=re.search("fmri\(tempfilt_yn\d+\)", line)
    
                if ev_conv_match:
                    conv=self.get_fsf_value(line,ev_conv_match.end())
                    index=self.get_fsf_indice(ev_conv_match.group())
                    conv_text={
                        "0" : "none",
                        "1" : "Gaussian",
                        "2" : "Gamma",
                        "3" : "Double-Gamma HRF",
                        "4" : "Gamma basis functions",
                        "5" : "Sine basis functions",
                        "6" : "FIR basis functions",
                        }
                    ev_convolves[index]=conv_text[conv]
    
                if ev_deriv_match:
                    value=self.get_fsf_value(line,ev_deriv_match.end())
                    index=self.get_fsf_indice(ev_deriv_match.group())
                    if value == "1":
                        value = "Y"
                    else:
                        value = "N"
                    ev_deriv[index]=value
                if ev_temps_match:
                    value=self.get_fsf_value(line,ev_temps_match.end())
                    index=self.get_fsf_indice(ev_temps_match.group())
                    if value == "1":
                        value = "Y"
                    else:
                        value = "N"
                    ev_temp[index]=value
                if ev_path_match:
                    value=self.get_fsf_value(line,ev_path_match.end())
                    index=self.get_fsf_indice(ev_path_match.group())
                    ev_paths[index]=self.strip_root(value)

            if type == self.FE_TYPE:
                evg_match=re.search("fmri\(evg\d+\.\d+\)", line)
                if evg_match:
                    evg_lines.append(line)
            if type == self.FE_TYPE or type == self.FIRST_TYPE:
                ev_name_match=re.search("fmri\(evtitle\d+\)", line)
                cope_name_match=re.search("fmri\(conname_real\.\d+\)", line)
                cope_def_match=re.search("fmri\(con_real\d+\.\d+\)", line)
                if cope_name_match:
                    name=self.get_fsf_value(line,cope_name_match.end())
                    index=self.get_fsf_indice(cope_name_match.group())
                    cope_names[index]=name
                if cope_def_match:
                    cope_def_lines.append(line)
                if ev_name_match:
                    name=self.get_fsf_value(line,ev_name_match.end())
                    index=self.get_fsf_indice(ev_name_match.group())
                    ev_names[index]=name
    
        if type == self.FIRST_TYPE or type == self.FE_TYPE:
            design_matrix=[['0' for col in range(len(ev_names)+2)] for row in range(len(cope_names)+1)]
            if 'ev_temp' in locals():
                real_copes=list()
                index_cope=1
                real_copes.append(str(index_cope))
                for i in range(1,len(ev_temp)+1):
                    ind=str(i)
                    if ev_temp[ind] == 'Y':
                        index_cope += 2
                    else:
                        index_cope += 1
                    real_copes.append(str(index_cope))
                real_copes.pop()
                design_matrix=self.fill_matrix(cope_def_lines,design_matrix,type,1,real_copes)
            else:
                design_matrix=self.fill_matrix(cope_def_lines,design_matrix,type,1)

            for i in range(1,len(cope_names)+1):
                ind=str(i)
                design_matrix[i][0]=ind
            for i in range(1,len(cope_names)+1):
                ind=str(i)
                design_matrix[i][1]=cope_names[ind]
            for i in range(2,len(ev_names)+2):
                ind=str(i-1)
                design_matrix[0][i]=ev_names[ind]
            design_matrix[0][0]='Cope #'
            design_matrix[0][1]='Cope Name'
        if type == self.PRE_TYPE:
            return analysis_name,output_path,tr,total_volumes,deleted,in_file,motion_correction,brain_thresh,smoothing
        elif type == self.FIRST_TYPE:
            return analysis_name,output_path,in_file,design_matrix,ev_names,ev_paths,ev_convolves,ev_deriv,ev_temp,cope_names
        elif type == self.ME_TYPE:
            return analysis_name,output_path,pvalue,zvalue,feat_paths,count, FE_example_dir
        elif type == self.FE_TYPE:
            regressor_matrix=[['0' for col in range(int(count)+1)] for row in range(len(ev_names)+1)]
            self.fill_matrix(evg_lines,regressor_matrix,5, 0)
            for i in range(1,len(ev_names)+1):
                ind=str(i)
                regressor_matrix[i][0]=ev_names[ind]
            for i in range(1,int(count)+1):
                ind=str(i)
                regressor_matrix[0][i]=ind
            return analysis_name,output_path,feat_paths,count,design_matrix,regressor_matrix,ev_names,cope_names,first_example_dir

    def strip_root(self,line):
        run=re.search("r\d\/",line)
        if run:
            out=self.get_fsf_value(line,run.end())
            out='./'+out
        else:
            out=line
        return out

    def strip_experiment_root(self,line):
        run=re.search("TAF_fanal\/",line)
        if run:
            out=self.get_fsf_value(line,run.end())
            out='./'+out
        else:
            out=line
        return out

    def strip_cope(self,line):
        cope=re.search("_*cope",line)
        if cope:
            out=line[0:cope.start()]
            out=out.strip()
        else:
            out=line
        return out

    def parsed_to_csv_lines(self,parsed_data,type):
        """
            format parsed data as a single csv sheet
        """
        width = 2
        if type == self.FIRST_TYPE:
            analysis_name,output_path,in_file,design_matrix,ev_names,ev_paths,ev_convolves,ev_deriv,ev_temp,cope_names= parsed_data
        elif type == self.ME_TYPE:
            analysis_name,output_path,pvalue,zvalue,feat_paths,count,FE_example_dir = parsed_data
        elif type == self.FE_TYPE:
            analysis_name,output_path,feat_paths,count,design_matrix,regressor_matrix,ev_names,cope_names,first_example_dir=parsed_data
        elif type == self.PRE_TYPE:
            analysis_name,output_path,tr,total_volumes,deleted,in_file,motion_correction,brain_thresh,smoothing=parsed_data

        out_lines=list()
        if type == self.FIRST_TYPE:
            out_lines.append('First Level');
        elif type == self.FE_TYPE:
            out_lines.append('Fixed Effects');
        elif type == self.ME_TYPE:
            out_lines.append('Mixed Effects');
        elif type == self.PRE_TYPE:
            out_lines.append('Preproc');

        out_lines.append("Analysis Name:,"+analysis_name)
        if type == self.FIRST_TYPE or self.PRE_TYPE:
            out_lines.append("Input file:,"+in_file);
            out_lines.append(',')
        if type == self.FE_TYPE:
            out_lines.append("Input Count:, "+count)
        if type == self.ME_TYPE or type == self.FE_TYPE:
            out_lines.append("Outpath:,"+output_path)
        if type == self.ME_TYPE:
            out_lines.append("p-value:,"+pvalue)
            out_lines.append("z-value:,"+zvalue)
            out_lines.append("Num subjects:,"+count)
            out_lines.append(',')

        if type == self.ME_TYPE or type == self.FE_TYPE:
            out_lines.append('Inputs:')
            for ind in range(1,len(feat_paths)+1):
                i=str(ind)
                line=feat_paths[i]
                out_lines.append(line)
        if type == self.FE_TYPE:
            out_lines.append(',')
            out_lines.append('Regressor Matrix:')
            len_matrix=len(regressor_matrix[0])
            if len_matrix > width:
                width = len_matrix
            regressor_matrix[0][0]=''
            for row in regressor_matrix:
                row=",".join(row)
                out_lines.append(row)
            out_lines.append(',')


        if type == self.FIRST_TYPE:
            out_lines.append('Regressors:')
            out_lines.append('Name,Convolution,Add Temporal Derivative,Apply Temporal Filtering,Path')

            for ind in range(1,len(ev_names)+1):
                i=str(ind)
                try:
                    line=[ev_names[i],ev_convolves[i],ev_deriv[i],ev_temp[i],ev_paths[i]]
                except:
                    line=[ev_names[i],'','','','']
                    print "malformed ev?"
                if width < 5:
                    width = 5

        out_lines.append(",".join(line))
        out_lines.append(',')
        if type == self.FIRST_TYPE or type == self.FE_TYPE:
            out_lines.append('Contrast Matrix:')
            #design_matrix[0][0]=''
            len_matrix=len(design_matrix[0])
            if len_matrix > width:
                width = len_matrix
            for row in design_matrix:
                row=",".join(row)
                out_lines.append(row)
        if type == self.PRE_TYPE:
            tr,total_volumes,deleted,in_file,motion_correction,brain_thresh,smoothing
            out_lines.append("TR:, "+tr)
            out_lines.append("Total Volumes:, "+total_volumes)
            out_lines.append("Deleted Volumes:, "+deleted)
            out_lines.append("Motion Correction:, "+motion_correction)
            out_lines.append("Brain Thresholding:, "+brain_thresh)
            out_lines.append("Smoothing:, "+smoothing)
        self.width=width
        self.height=len(out_lines)
        return out_lines

    def explode_parsed(self, parsed_data ):
        if self.type == self.FIRST_TYPE:
            self.analysis_name,self.output_path,self.in_file,self.design_matrix,self.ev_names,self.ev_paths,self.ev_convolves,self.ev_deriv,self.ev_temp,self.cope_names = parsed_data
        elif self.type == self.ME_TYPE:
            self.analysis_name,self.output_path,self.pvalue,self.zvalue,self.feat_paths,self.count, self.FE_example_dir = parsed_data
        elif self.type == self.FE_TYPE:
            self.analysis_name,self.output_path,self.feat_paths,self.count,self.design_matrix,self.regressor_matrix,self.ev_names,self.cope_names,self.first_example_dir=parsed_data
        elif self.type == self.PRE_TYPE:
            self.analysis_name,self.output_path,self.tr,self.total_volumes,self.deleted,self.in_file,self.motion_correction,self.brain_thresh,self.smoothing=parsed_data

    def get_fsf_value(self,fsf_line, end):
        """ return a value from an fsf line
            fsf lines have a perdictable structure, where vaiable is defined and then value follows
            this function returns of a clean copy of the variable in supplied fsf_line, where value is everything in the
            line after the supplied variable end. newline characters, " , and leading spaces are stripped
        """
        value=fsf_line[end:len(fsf_line)]
        value=value.strip("\n")
        value=value.strip()
        value=value.replace('"','')
        return value

    def get_fsf_indice(self,fsf_variable_def):
        """ return a the variable indice from an fsf line variable declaration
            fsf variables are defined as set fmri(***variable type***#indice)
            this function returns the indice of the supplied variable definition
        """
        match=re.search('\d+', fsf_variable_def)
        return match.group()

class ev:
    Name = "EV"
    def set_convolution(self,convolution_value):
        conv_text={
            "0" : "none",
            "1" : "Gaussian",
            "2" : "Gamma",
            "3" : "Double-Gamma HRF",
            "4" : "Gamma basis functions",
            "5" : "Sine basis functions",
            "6" : "FIR basis functions",
            }
        if convolution_value is None:
            self.convolution=None
        else:
            self.convolution=conv_text[convolution_value]
class contrast:
    Name = "Contrast"


