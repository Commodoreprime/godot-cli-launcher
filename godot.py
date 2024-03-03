#!/usr/bin/env python3
from os import environ as env
from pathlib import Path
from sys import argv
import os
import re

try:
    data_path_parent: str = env["XDG_DATA_HOME"]
except KeyError:
    data_path_parent = f"{os.path.expanduser('~')}/.local/share"

GODOT_BINS_DIRECTORY = Path(f"{data_path_parent}/godot-bin")

def godot_bin_indexer(bin_search_path: str|Path) -> list:
    return_list = []
    for directory in bin_search_path.iterdir():
        file_path: Path = None
        if directory.is_dir():
            for subdir in directory.iterdir():
                if subdir.is_file():
                    file_path = subdir
        elif directory.is_file():
            file_path = directory
        
        bin_basename = os.path.basename(file_path)
        
        # TODO: Probably best to eliminate the RegEx, if possible
        godot_version = re.findall(r'v[0-9].+-', bin_basename)[0][1:-1]
        godot_release_class = re.findall(r'-\w+_', bin_basename)[0][1:-1]
        godot_is_mono = godot_release_class.count("mono") >= 1
        
        return_list.append({
            "bin_path": file_path,
            "version": godot_version,
            "release_class": godot_release_class.split('_')[0],
            "is_mono": godot_is_mono
            })
    return return_list

godots_index: list = sorted(godot_bin_indexer(GODOT_BINS_DIRECTORY), key=lambda k: k["version"])

def reverse_search_value_dict(source_list: list, target_key: str, target_value: str) -> list:
    """ Iterate over a list of dicts and given a key and value, return list of index positions that point to matching dict items.
    target_value can be any amount of precision, given a use-case.
    The returned list is reversed so the last found appears first, second-to-last appears second, etc...
    """
    return_list = []
    for i, item in enumerate(source_list):
        if item[target_key].startswith(target_value) == True:
            return_list.append(i)
    return_list.reverse()
    return return_list

def gather_version(parsing_list: list, get_startidx: bool = False) -> dict:
    return_object: dict = {}
    release_class_found: bool = False
    for i, arg in enumerate(parsing_list):
        return_object.update({"argv_startidx": i})
        if arg == "--":
            return_object["argv_startidx"] += 1
            break
        elif arg.replace('.', '').isdigit() == True:
            if return_object.get("version") == None:
                return_object.update({"version": ""})
            return_object["version"] += f"{arg}."
        elif arg == "mono":
            return_object.update({"using_mono": True})
        elif (arg.count("stable") + arg.count("rc") + arg.count("beta") + arg.count("alpha")) == 1 and release_class_found == False:
            return_object.update({"release_class": arg})
            release_class_found = True
        elif arg == "--list" or arg == "-l":
            return { "list_bins": True }
        else:
            break
    
    if return_object["argv_startidx"] > -1:
        return_object["argv_startidx"] += 1
    elif get_startidx == False or return_object["argv_startidx"] <= -1:
        return_object["argv_startidx"] = None

    if return_object.get("version") != None:
        return_object["version"] = return_object["version"].strip('.')
    
    return return_object

# Doubles as "default" arguments
target_godot: dict = {
    "version": godots_index[len(godots_index) - 1]["version"], # i.e. 4.2
    "release_class": "stable",
    "using_mono": False,
    "argv_startidx": -1,
    "list_bins": False
}

script_name = os.path.basename(argv[0])[5:]
if len(script_name) != 0 or script_name != ".py":
    target_godot.update(gather_version(script_name.split('-'), get_startidx=False))

if len(argv[1:]) > 0:
    target_godot.update(gather_version(argv[1:], get_startidx=True))

if target_godot["list_bins"] == True:
    for gd_entry in godots_index:
        print(f'{gd_entry["version"]} {gd_entry["release_class"]}', end='')
        if gd_entry["is_mono"] == True:
            print(" mono", end='')
        print("")
    exit(0)

highest_match_idxs = reverse_search_value_dict(godots_index, "version", target_godot["version"])

godot_launch_args = argv[target_godot["argv_startidx"]:]

print(f'Launching Godot {target_godot["version"]} {target_godot["release_class"]}', end='')
if target_godot["using_mono"] == True:
    print(f" with mono", end='')
if len(godot_launch_args) > 0:
    print(f". With the following args: {' '.join(godot_launch_args)}", end='')
print("")

for idx in highest_match_idxs:
    item = godots_index[idx]
    if item["release_class"] == target_godot["release_class"] and \
       item["is_mono"] == target_godot["using_mono"]:
            exec_path = item["bin_path"]
            executable_args = [exec_path]
            executable_args.extend(godot_launch_args)
            os.execvp(exec_path, executable_args)

print(f"Was unable to locate the Godot binary in {GODOT_BINS_DIRECTORY}")

exit(1)
