__author__ = 'michael'
import os
from fsl_tools_exceptions import MalformedStructure

def determine_struct(structure_string):
    split_up_structure=structure_string.split("/")
    if split_up_structure[0] != "experiment_root":
        raise MalformedStructure("Bad structure line. Should begin with 'Experiment Root'")
    else:
        print len(split_up_structure)
    return split_up_structure[1:len(split_up_structure)]

def walk_dir(path,level,ignore_words,end_level):
    directory_list=os.listdir(path)
    main=list()
    for dir_list_item in directory_list:
        path_dir=os.path.join(path,dir_list_item)
        if ignore_words.count(dir_list_item) == 0 and os.path.isdir(path_dir):
            if level == end_level:
                main.append(dir_list_item)
            else:
                main.append([dir_list_item,walk_dir(path_dir,level+1,ignore_words,end_level)])
    return main

def atomize_directory(directory_lists,level_count,end_level,directory_hierarchy, passed_dict=dict(),atoms=None):
    if level_count == end_level:
        item_type=directory_hierarchy[level_count]
        for item in directory_lists:
            atom=dict(passed_dict)
            atom[item_type]=item
            atoms.append(atom)
    elif level_count < end_level:
        if level_count == 0:
            atoms=list()
            for item in directory_lists:
                label=item[0]
                item_type=directory_hierarchy[level_count]
                passed_dict[item_type]=label
                atomize_directory(item[1],level_count+1,end_level,directory_hierarchy,passed_dict=passed_dict,atoms=atoms)
            return atoms
        else:
            for item in directory_lists:
                label=item[0]
                item_type=directory_hierarchy[level_count]
                passed_dict[item_type]=label
                atomize_directory(item[1],level_count+1,end_level,directory_hierarchy,passed_dict=passed_dict,atoms=atoms)


def experiment_walk(config_line,root_dir,ignore_list):
    #TODO config parsing here
    directory_hierarchy=determine_struct(config_line)
    directory_by_type=dict()
    for type in directory_hierarchy:
        directory_by_type[type]=list()
    level_count=len(directory_hierarchy)-1
    directory_listing=walk_dir(root_dir,0,ignore_list,level_count)
    atoms=atomize_directory(directory_listing,0,2,directory_hierarchy)
    for atom in atoms:
        count=0
        for type in directory_hierarchy:
            directory_list=directory_by_type[type]
            atom_value_for_type=atom[type]
            if directory_list.count(atom_value_for_type) == 0:
                directory_list.append(atom_value_for_type)
    return atoms,directory_by_type
#    split_root_dir=root_dir.split("/")
#    for root,dir,folder in os.walk(root_dir):
#        root_stripped=root[len(root_dir):len(root)]
#        split_sub_dir=root_stripped.split('/')
#        if len(split_sub_dir) == len(directory_hierarchy):
#            print split_sub_dir







