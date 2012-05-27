__author__ = 'michael'
from fsf_file import fsf_file
from utils import first_to_csv,fe_to_csv,me_to_csv,pre_to_csv
from utils import fsf_to_one_column
def load_file(file_path):
    """Loads file specified as path, returns lines as list"""
    try:
        with file(file_path, 'r') as original:
            return original.readlines()
    except:
        print "Could not open fsf"


if __name__ == "__main__":
    set_test=1

    if set_test==0:
        pre_file=fsf_file("/Volumes/storage/TAF_fanal/PV/Ctrl/x305/r1/preproc_8s.feat/design.fsf")
        pre_csv_lines,width=pre_to_csv(pre_file)
        for line in pre_csv_lines:
            print line
        pre_one=fsf_to_one_column(pre_file)
        for line in pre_one:
            print line

    if set_test==1:
        FilePath="/Volumes/storage/TAF_fanal/PV/Ctrl/x301/r1/a5t.feat/design.fsf"
        first_file=fsf_file(FilePath)
        first_csv_lines,first_width,height=first_to_csv(first_file)
        for line in first_csv_lines:
            print line
        first_one=fsf_to_one_column(first_file)
        for line in first_one:
            print line
    if set_test==2:
        FilePath="/Volumes/storage/TAF_fanal/PV/FE2/x301fe_a5t.gfeat/design.fsf"
        fe_file=fsf_file(FilePath)
        fe_csv_lines,first_width=fe_to_csv(fe_file)
        for line in fe_csv_lines:
            print line
        fe_one=fsf_to_one_column(fe_file)
        for line in fe_one:
            print line
    if set_test==3:
        FilePath="/Volumes/storage/TAF_fanal/PV/ME/a5t_cope1.gfeat/design.fsf"
        me_file=fsf_file(FilePath)
        me_csv_lines,first_width=me_to_csv(me_file)
        for line in me_csv_lines:
            print line
        me_one=fsf_to_one_column(fe_file)
        for line in fe_one:
            print line
