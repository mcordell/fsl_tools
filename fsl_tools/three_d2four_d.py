#! /Library/Frameworks/Python.framework/Versions/Current/bin/python
import re,os

if __name__ == "__main__":
    regex_phrase=raw_input('Enter match phrase for images:\n')
    print regex_phrase

    files=os.listdir(os.curdir)
    match_list=list()
    for file in files:
       match=re.search(regex_phrase,file)
       if match:
           match_list.append(file)
           print file

    sorted_match_list=sorted(match_list)

    out_name=raw_input('Enter output name:\n')
    output_string="fslmerge -t "+out_name
    for file_name in sorted_match_list:
        output_string=output_string+" "+file_name

    print output_string


