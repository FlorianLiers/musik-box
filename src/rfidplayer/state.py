#!/usr/bin/env python
# -*- coding: utf8 -*-

import os


def load_state(id):
    try:
        statefile = open("/tmp/" +id +".state", "r")
        data = statefile.readlines()
        statefile.close()
        return int(data[0].strip()), int(data[1].strip())
    except:
        print("Failed to load state for " +id)
    return 0, 0

def save_state(id, index, position_ms):
    try:
        statefile = open("/tmp/" +id +".state", "w")
        statefile.write(str(index) +"\n" +str(position_ms))
        statefile.close()
    except:
        print("Failed to save state for " +id)

def remove_state(id):
    try:
        os.remove("/tmp/" +id +".state")
    except:
        print("Failed to remove state for " +id)


