fsl_tools
======================

A suite of python tools/scripts for more efficient work within the FSL neuroimaging suite

Tools
---------------------------
* fsf_reporter.py - converts fsf files into an organized csv format
* run_to_atlas.py - convert "run space" coordinates to standard space, and give atlas information about that point in excel spreadsheet
* excel_results.py - organize output images from feat reports into a single excel spreadsheet
* create_config.py - script to create a configuration file for your experiment
* multithreader.py - using a list of fsfs run several at once, in sequence. Pseudo multithreading because control is by OS
* mask_to_image.py - overlays a standard space mask on a standard, and then produces a png of overlay

Dependencies by script
----------------------------
* fsf_reporter.py: none (std python library), however, fsf_reporter can use excel_results which has dependencies
* run_to_atlas.py: xlwt http://pypi.python.org/pypi/xlwt
* excel_results.py: xlwt,xlrd,xlutils www.python-excel.org and python imaging library (PIL) http://www.pythonware.com/products/pil/
* mask_to_image.py: requires the lut directory for custom colors


Supplementary files
--------------------------
* fsf_file.py - class for parsing and opening design.fsfs 
* utils.py - supplementary file that holds helper functions for many of the above scripts


