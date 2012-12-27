__author__ = 'Michael'
import ConfigParser

def main():
    config = ConfigParser.RawConfigParser()
    
    config.add_section('directory structure')
    config.set('directory structure','experiment_root',"/mnt/Storage/TAF_fanal/")

    config.add_section('Analysis Directories')
    config.set('Analysis Directories', 'first_level_dir', "/Volumes/storage/TAF_fanal/FS/Ctrl/x305/r2")
    config.set('Analysis Directories', 'FE_dir', "/Volumes/storage/TAF_fanal/FS/FE2")
    config.set('Analysis Directories', 'ME_dir', '/Volumes/storage/TAF_fanal/FS/ME')
    config.set('Analysis Directories', 'template', 'template.xls')

    config.add_section('run_to_atlas')
    config.set('run_to_atlas','reg_name','qreg_8s')
    config.set('run_to_atlas','structure','experiment_root/study_code/condition/subject/run/')
    config.set('run_to_atlas','reg_path','experiment_root/study_code/condition/subject/run/reg_name')
    config.set('run_to_atlas','study_code','PV')
    config.set('run_to_atlas','experiment_root',"/mnt/Storage/TAF_fanal/")

    config.add_section('fsl_directories')
    config.set("fsl_directories",'standard_brain',"/usr/local/fsl/data/standard/MNI152_T1_2mm_brain")

    config.add_section('Match Patterns')
    config.set('Match Patterns','me_pattern', "_cope")
    config.set('Match Patterns','cope_pattern', "cope\d+")

    with open('example.cfg', 'wb') as configfile:
        config.write(configfile)

if __name__ == "__main__":
    main()
