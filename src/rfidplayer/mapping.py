#!/usr/bin/env python
# -*- coding: utf8 -*-

import glob
import re
import json

chip_to_music_mapping_file = u"mapping.json"

def set_mapping_file(filename):
    global chip_to_music_mapping_file
    chip_to_music_mapping_file = filename


def get_all_mappings():
    global chip_to_music_mapping_file
    try:
        with open(chip_to_music_mapping_file, "r") as mappingfile:
            return json.load(mappingfile)
    except Exception as exc:
        print("Failed to load file '" +chip_to_music_mapping_file +"' due to " +str(exc))
        raise

def get_pattern(chip):
    try:
        mapping = get_all_mappings().get(chip, None)
        if mapping:
            return mapping.pattern
        else:
            return None
    except:
        return None

def set_mapping(chip, pattern, comment):
    global chip_to_music_mapping_file
    map = get_all_mappings()
    map[chip] = { "pattern": pattern }
    if comment and comment <> "":
        map[chip].comment = comment
    try:
        with open(chip_to_music_mapping_file, "w") as mappingfile:
            json.dump(map, mappingfile, indent=2)
    except Exception as exc:
        print("Failed to write file '" +chip_to_music_mapping_file +"' due to " +exc)
        raise
