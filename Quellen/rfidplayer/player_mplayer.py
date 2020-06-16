#!/usr/bin/env python
# -*- coding: utf8 -*-

import subprocess
import glob


message_level = 2

# Global variable with handle for current mplayer process
mplayer_process = None


def play(id, filename):
    global mplayer_process
    global message_level
    print("Starting Mplayer with " +id +" - " +filename)
    # MPlayer does not support playback of recursive directories
    # thus, we have to use a workaround with a playlist
    if filename.endswith("/*"):
        filename = filename[:-1]
        print("Starting Playback with playlist for " +filename)
        mplayer_cmd = "mplayer -playlist <(find '" +filename +"' -type f)"
        if message_level >= 3:
            print("MPlayer cmd: " +mplayer_cmd)
        mplayer_process = subprocess.Popen(mplayer_cmd, shell=True, executable='/bin/bash')
    else:
        print("Starting Playback for " +filename)
        mplayer_process = subprocess.Popen(["mplayer", filename])

def stop():
    global mplayer_process
    print("Stopping Mplayer")
    if mplayer_process is not None:
        print("Stopping")
        mplayer_process.terminate()
        mplayer_process = None
        return True
    else:
        return False
