__author__ = 'michael'
from argparse import ArgumentParser
from os import path,getcwd
import ConfigParser
from subprocess import Popen

def overlay(standard,mask_name,out):
    Popen(['/usr/local/fsl/bin/overlay', '1', '0', standard, '-a', mask_name, '1', '100', out])

def slice(outname,color=None):
    if color:
        slicer_command=['/usr/local/fsl/bin/slicer',outname,'-l',color, '-L','-S','2','750',outname+'.png']
    else:
        slicer_command=['/usr/local/fsl/bin/slicer',outname, '-L','-S','2','750',outname+'.png']
    Popen(slicer_command)

if __name__ == "__main__":
    #Parse options
    parser = ArgumentParser()
    parser.add_argument('-p', '--configpath')
    parser.add_argument('-o', '--out')
    parser.add_argument('-c', '--color',help='COLOR Choices: g=green b=blue p=pink ')
    parser.add_argument('-m','--mask', required=True)
    args = parser.parse_args()
    config_file_path=args.configpath
    output_name=args.out
    color_arg=args.color
    mask=args.mask
    #Check if config file is specified
    if config_file_path is None:
        config_file_path="example.cfg"

    if output_name is None:
        output_name='masked_overlaid'

    # read configuration file
    try:
        f = open(config_file_path,'r')
        f.close()
    except IOError:
        print "Config file path not valid. Please specify a valid path"
        exit()


    config = ConfigParser.RawConfigParser()
    config.read(config_file_path)

    try:
        standard_image = config.get('fsl_directories', 'standard_brain')
    except ConfigParser.NoSectionError:
        print "Config file appears to be corrupt, regenerate with create_config or specify new path"
        exit()

    #test color input
    if color_arg:
        if color_arg is "g":
            color_path=path.join(getcwd(),'luts/green.lut')
    else:
        color_path=None

    overlay(standard_image,mask,output_name)
    slice(output_name,color_path)


