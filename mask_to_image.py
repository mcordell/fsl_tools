__author__ = 'michael'
from argparse import *
from os import path,getcwd
import ConfigParser
from subprocess import Popen
import textwrap

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
    parser = ArgumentParser(
        prog='mask_to_image',
        formatter_class=RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
        Mask to image overlays a standard space mask on a standard nifti image. This overlaid image is then sliced with
        the fsl tool slicer to create a png of the overlay.

        '''),
        epilog=textwrap.dedent('''\
            Example usage:
                mask_to_image -m \'FOC84.nii.gz\' -c p -o \'pink_overlay\'

                This would create two files:
                        pink_overlay.nii.gz - The nifti file of the overlay
                        pink_overlay.png - the png version of the overlay. The color of the mask in this picture would be pink

                Other Notes:
                ------------
                The standard image is specified in the configuration file. The default path is "example.cfg", however a
                different path can be specified with the "-c" option. Make sure this points to the standard image you want
                and the mask is in the same coordinate space.

        ''')
    )
    parser.add_argument('-p', '--configpath', help='Default=example.cfg' )
    parser.add_argument('-o', '--out', help='Output name base, do not include extension. Default=masked_overlaid')
    parser.add_argument('-c', '--color',help='Mask color in image. Default=yellow. COLOR Choices: g=green b=blue p=pink r=red')
    parser.add_argument('-m','--mask', help='Mask path',required=True)
    parser.print_help()
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
        elif color_arg is "b":
            color_path=path.join(getcwd(),'luts/blue.lut')
        elif color_arg is "p":
            color_path=path.join(getcwd(),'luts/pink.lut')
        elif color_arg is "r":
            color_path=path.join(getcwd(),'luts/red.lut')
    else:
        color_path=None

    overlay(standard_image,mask,output_name)
    slice(output_name,color_path)


