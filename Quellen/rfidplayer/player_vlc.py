#!/usr/bin/env python
# -*- coding: utf8 -*-

import time
import vlc
import glob
import thread

import state


save_interval_sec = 20


vlc_playing = False
vlc_next_song = False


def vlc_callback(self, event):
    global vlc_next_song
    print("vlc song ended")
    vlc_next_song = True


def play_vlc_single(id, index, filename, start_position_ms):
    global vlc_playing
    global vlc_next_song
    global save_interval_sec
    p = vlc.MediaPlayer("file://" +filename)
    p.event_manager().event_attach(vlc.EventType.MediaPlayerEndReached, vlc_callback, 1)
    print("Created")
    result = p.play()
    if result == 0:
        vlc_next_song = False
        vlc_check_sec = 0
        if start_position_ms > 0:
            p.set_time(start_position_ms)
        while vlc_playing and not vlc_next_song:
            if vlc_check_sec <= 0:
                vlc_check_sec = save_interval_sec
                state = p.get_state()
                position = p.get_time()
                title = p.get_title()
                print(str(state) +" - time was " +str(position) +" (" +str(p.get_position()) +")")
                state.save_state(id, index, position)
            vlc_check_sec = vlc_check_sec -1
            time.sleep(1)
        p.stop()
        print("Stopped at " +str(p.get_time()) +" (" +str(vlc_playing) +"," +str(vlc_next_song) +")")
    else:
        print("Failed to start playback for " +filename)
    p.release()
    return result == 0


def play_vlc_playlist(id, filename):
    global vlc_playing
    vlc_playing = True
    (start_index, start_position_ms) = state.load_state(id)
    if filename.endswith("/*"):
        print("Play playlist for " +id)
        playlist = glob.glob(filename)
        print("number files found = " +str(len(playlist)))
    else:
        print("Play track " +id)
        playlist = [ filename ]
    index = 0
    for track in playlist:
        if vlc_playing:
            if index >= start_index:
                position_ms = 0
                if index == start_index:
                    position_ms = start_position_ms
                print("Playing " +str(index) +" = " +track +" (" +str(position_ms) +"ms)")
                play_vlc_single(id, index, track, position_ms)
        index = index +1
    if vlc_playing:
        print("Play list ended")
        state.remove_state(id)
    else:
        print("Play list stopped")


def play(id, filename):
    print("Starting VLC for " +id +" - " +filename)
    thread.start_new_thread(play_vlc_playlist, (id, filename, ))


def stop():
    global vlc_playing
    print("Stopping VLC - end signal to VLC")
    vlc_playing = False
