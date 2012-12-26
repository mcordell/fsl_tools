import ConfigParser
from ConfigParser import NoSectionError, NoOptionError

class Configuration:
    """
        Object for reading and holding variables from the configuration file
    """
    name = "Configuration"

    def __init__(self, config_path):
        try:
            f = open(config_path,'r')
            f.close()
        except IOError:
            print ("Config file path not valid. Please specify a valid path")
            raise IOError
        self.config = ConfigParser.RawConfigParser()
        self.config.read(config_path)
        self.first_level_dir=self.read_option('Analysis Directories','first_level_dir') 
        self.FE_dir=self.read_option('Analysis Directories','fe_dir') 
        self.ME_dir=self.read_option('Analysis Directories','me_dir') 
        self.template_path=self.read_option('Analysis Directories','template')
        self.me_pattern=self.read_option('Match Patterns','me_pattern')
        
    def read_option(self,category, key):
        try:
            value = self.config.get(category,key)
        except NoSectionError as e: 
            print ("Config file appears to not have a section "+category)
            raise e
        except NoOptionError as e:
            print ("Config file appears to not have a value "+key+" in the section "+category)
            raise e
        return value
