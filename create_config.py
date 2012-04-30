__author__ = 'Michael'
import ConfigParser

def main():
    config = ConfigParser.RawConfigParser()
    config.add_section('Analysis Directories')
    config.set('Analysis Directories', 'first_level_dir', "\\\\192.168.2.181\MyFiles\TAF_fanal\PV\Ctrl\\x305\\r2")
    config.set('Analysis Directories', 'FE_dir', "\\\\192.168.2.181\MyFiles\TAF_fanal\PV\FE2")
    config.set('Analysis Directories', 'ME_dir', '\\\\192.168.2.181\MyFiles\TAF_fanal\PV\ME\\')
    with open('example.cfg', 'wb') as configfile:
        config.write(configfile)

if __name__ == "__main__":
    main()