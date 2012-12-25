#! /Library/Frameworks/Python.framework/Versions/Current/bin/python
import shutil,os



if __name__ == "__main__":
    base_path="/Volumes/TAF2/Leptin/"
    subs={'Pre'}
    for sub in subs:
        subjects={'x4','x5'}
        for subject in subjects:
            path=os.path.join(base_path,sub,subject)
            runs={'r1','r2','r3','r4'}
            for run in runs:
                run_path=os.path.join(path,run)
                pre_reg=os.path.join(run_path,"preproc_no_st.feat/reg")
                analysis_path=os.path.join(run_path,"ppi_hyp_a_no_st.feat/reg")
                #reg_old=os.path.join(run_path,"qreg_no_st")

                if os.path.exists(reg_old):
                    #os.rename(reg_old,os.path.join(run_path,"old_qreg_8s"))
                    print reg_old
                #if os.path.exists(pre_reg):
                    #shutil.move(pre_reg,reg_old)
                if os.path.exists(analysis_path):
                    print analysis_path

                    os.remove(analysis_path)
                    #os.symlink(reg_old,analysis_path)
                    #shutil.move(analysis_path, os.path.join(run_path,"qreg_no_st"))



