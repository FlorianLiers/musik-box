#!/usr/bin/env python
# -*- coding: utf8 -*-

import glob
import re
import json


chip_to_music_mapping_file = u"mapping.txt"

# line in mapping file must look like this:
#    1-2-3-4 /my/path/to/files/*
mapping_regex = re.compile(r"^\s*(\d+-\d+-\d+-\d+) (.+)$")


def set_mapping_file(filename):
    global chip_to_music_mapping_file
    chip_to_music_mapping_file = filename


def get_mapping():
    global chip_to_music_mapping_file
    global mapping_regex
    map = []
    try:
        with open(chip_to_music_mapping_file, "r") as mappingfile:
            for line in mappingfile:
                line = line.strip()
                # ignore comments and search for lines starting with chip id
                if not line.startswith("#") and line is not "":
                    match = mapping_regex.match(line)
                    if match:
                        print("Found: " +match.group(1) +" - " +match.group(2))
                        map.append({ "chip": unicode(match.group(1), "utf-8"), "pattern": unicode(match.group(2), "utf-8") })
                    else:
                        print("Line '" +line +"' does not match format")
    except Exception as exc:
        print("Failed to load file '" +chip_to_music_mapping_file +"' due to " +exc)

    return map


def get_pattern(chip):
    global chip_to_music_mapping_file
    global mapping_regex
    prefix = str(chip) +" "
    try:
        with open(chip_to_music_mapping_file, "r") as mappingfile:
            for line in mappingfile:
                line = line.strip()
                # search for lines starting with chip id
                if line.startswith(prefix):
                    print("found mapping: " +line)
                    return line.replace(prefix, "").strip()
    except:
        print("Failed to load file '" +chip_to_music_mapping_file +"'")
    
    # if we reach here, nothing was found in file
    return None

