__author__ = 'Michael'
import re

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
            self.values_dict,self.fsf_line_key=parse_to_dict(self.fsf_lines)
            self.type=self.get_type()
            if type:
                #populate the values common to all fsf's
                self.output_path=self.get_value("outputdir")
                self.analysis_name=self.get_analysis_name(self.output_path)
                self.z_value=self.get_value("z_thresh")
                self.p_value=self.get_value("prob_thresh")
                self.fill_values_from_dict()
                self.set_input_type()

    def parse_to_dict(fsf_lines):
        fsf_dict=dict()
        fsf_line_key=list()
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
                        #cleaned=cleaned.strip('\"')
                        print cleaned
                    else:
                        cleaned=split_line[2]#.strip('\"')
                    fsf_dict[split_line[1]]=cleaned
                    fsf_line_key.append(split_line[1])
        return fsf_dict,fsf_line_key

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
        if high_value is None or analysis_type is None:
            raise BadFsfException("Type of fsf not found. Fsf file probably corrupt.")
        else:
            if high_value != "1":
                higher_level_type=self.get_value("mixed_yn")
                if higher_level_type == "0" or higher_level_type == "2" or higher_level_type == "1":
                    type=self.ME_TYPE
                elif higher_level_type == "3":
                    type=self.FE_TYPE
            elif analysis_type == "6" or analysis_type == "7":
                type=self.FIRST_TYPE
            elif analysis_type == "1":
                type=self.PRE_TYPE
        return type

    def load_file(self):
        """Loads file specified as path, returns lines as list"""
        try:
            with file(self.FilePath, 'r') as original:
                return original.readlines()
        except IOError:
            print "Could not open fsf"
            raise

    def set_input_type(self):
        input_type=self.get_value('inputtype')
        if input_type == "2":
            if self.type == self.ME_TYPE or self.type == self.FE_TYPE:
                self.input_type=2
            else:
                print "I found a strange value at fmri(inputtype), this value should be 1 for first levels/preprocs.\n"
                print "I will assume it should actually be 1"
                self.input_type=1
        else:
            self.input_type=1


    def get_analysis_name(self,output_dir_string):
        analysis_name=None
        run=None
        if self.type == self.ME_TYPE:
            run=re.search("ME",output_dir_string)
        elif self.type == self.FIRST_TYPE or self.type == self.PRE_TYPE:
            run=re.search("r\d/",output_dir_string)
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
            self.input_file=self.strip_root(input_value)

    def fill_first_level(self):
        input_value=self.get_value("feat_files(1)")
        if input_value:
            self.input_file=self.strip_root(input_value)
            preproc_match=re.search("preproc.*feat",input_value)
            #TODO inconsistent methodology here
            if preproc_match:
                self.preproc=input_value[preproc_match.start():preproc_match.end()]

        number_of_evs=int(self.get_value("evs_orig"))
        number_of_copes=int(self.get_value("ncon_orig"))
        #noinspection PyUnusedLocal
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
        number_of_copes=int(self.get_value("ncon_real"))
        self.number_inputs=self.get_value("npts")
        self.inputs=dict()
        self.stripped_inputs=dict()
        #prep matrices
        #noinspection PyUnusedLocal
        regress_matrix=[['0' for col in range(int(self.number_inputs)+1)] for row in range(number_of_evs+1)]
        #noinspection PyUnusedLocal
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
            con.name=self.get_value("conname_real."+index)
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
        subject_pattern="x\d\d\d"
        self.number_subjects=self.get_value("npts")
        self.inputs=dict()
        self.stripped_inputs=dict()
        self.subjects=dict()
        for ind in range(1,int(self.number_subjects)+1):
            index=str(ind)
            input_value=self.get_value("feat_files("+index+")")
            self.inputs[index]=input_value
            input_value=input_value.strip("\n")
            input_value=input_value.strip('\"')
            input_value=self.strip_cope(input_value)
            self.stripped_inputs[index]=input_value

            subject_match=re.search(subject_pattern,input_value)
            if subject_match:
                self.subjects[index]=subject_match.group()

        
    def fill_values_from_dict(self):
        if self.type == self.PRE_TYPE:
            self.fill_pre()
        elif self.type == self.FIRST_TYPE:
            self.fill_first_level()
        elif self.type == self.FE_TYPE:
            self.fill_FE()
        elif self.type == self.ME_TYPE:
            self.fill_ME()

    def strip_root(self,line):
        run=re.search("r\d/",line)
        if run:
            out=self.get_fsf_value(line,run.end())
            out='./'+out
        else:
            out=line
        return out

    def strip_experiment_root(self,line):
        run=re.search("TAF_fanal/",line)
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

class BadFsfException(BaseException):
    pass

