__author__ = 'michael'
import argparse, os, re

fanal="/Volumes/storage/TAF_fanal/"


studies = {
                'A': ("Food Stroop","FS","r1"),
                'B': ("Food Stroop","FS","r2"),
                'C': ("Passive","PV","r1"),
                'D': ("Passive","PV","r2"),
                'E': ("Go-NoGo","GNG","r1"),
                'F': ("Go-NoGo","GNG","r2"),
                'G': ("Delay Discount","DD","r1"),
                'H': ("Delay Discount","DD","r2"),
                }

def main():
    #Parse options
    parser = argparse.ArgumentParser()
    parser.add_argument('input')
    parser.add_argument('-c','--condition')
    args=parser.parse_args()
    condition=args.condition
    file_input=os.path.join(args.input)
    subject_files=os.listdir(file_input)
    if condition == "C":
        condition="Ctrl"
    elif condition == "E":
        condition="Exr"
    else:
        print "Condition malformed. Exiting."
        quit()
    subjects_inorder=list()
    subjects_byrun=list()
    for subject_file in subject_files:
        sub_path=os.path.join(file_input,subject_file)
        try:
            with file(sub_path, 'r') as original:
                subject_lines=original.readlines()
        except:
            print "Input file does not appear to be valid"

        if subject_lines:
            subject=os.path.splitext(subject_file)[0]
            inorder=subject+":, "
            print "Assuming subject= "+subject+" from filename."
            subject_spikes={'A': '','B': '','C': '','D': '','E': '','F': '','G': '','H': ''}
            for index in range(1,len(subject_lines)):
                run=subject_lines[index].strip()
                proper_name,study_code,run_name=studies.get(run)
                print "Run "+str(index)+": "+proper_name+" "+study_code+" "+run_name
                run_path=os.path.join(fanal,study_code,condition,subject,run_name)
                motion_ouliers_path=os.path.join(run_path,"b","motion_outlier")
                spikes=os.path.join(motion_ouliers_path,"spikes.txt")
                print spikes
                if os.path.exists(spikes):
                    try:
                        with file(spikes, 'r') as original:
                            spike_line=original.readline()
                            print spike_line
                            inorder+=str(spike_line.count(","))+","
                            subject_spikes[run]=str(spike_line.count(","))
                    except:
                        print "spike file missing?"
            subjects_inorder.append(inorder)
            subjects_byrun.append(subject+":, " + ",".join((subject_spikes['A'],subject_spikes['B'],subject_spikes['C'],subject_spikes['D'],subject_spikes['E'],subject_spikes['F'],subject_spikes['G'],subject_spikes['H'])))


    for s in subjects_inorder:
        print s
    for s in subjects_byrun:
        print s

if __name__ == "__main__":
    main()





