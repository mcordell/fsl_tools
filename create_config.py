__author__ = 'Michael'
import ConfigParser

def main():
    config = ConfigParser.RawConfigParser()
    config.add_section('Analysis Directories')
    config.set('Analysis Directories', 'first_level_dir', "/Volumes/storage/TAF_fanal/FS/Ctrl/x305/r2")
    config.set('Analysis Directories', 'FE_dir', "/Volumes/storage/TAF_fanal/FS/FE2")
    config.set('Analysis Directories', 'ME_dir', '/Volumes/storage/TAF_fanal/FS/ME')
    with open('example.cfg', 'wb') as configfile:
        config.write(configfile)

if __name__ == "__main__":
    main()