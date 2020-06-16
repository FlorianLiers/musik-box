#!/usr/bin/env python
# -*- coding: utf8 -*-

import RPi.GPIO as GPIO
from lib import MFRC522
import signal
import time
import subprocess
import glob

import player_vlc as player

message_level = 2
chip_to_music_mapping_file = "mapping.txt"


# Debug tests:
#player.play_vlc_playlist("id", "/mnt/diskflea/music/Alben/Neil Diamond/Millennium Edition/Millennium Edition-Neil Diamond-Both Sides Now.mp3")
#player.play(1, "/mnt/diskflea/music/Alben/Ole Edvard Antonsen/Antonsen, Ole Edvard- Nordic Trumpet Concertos/*")
#player_volumio.play("test")


# Helper function for shutting down whole system
def shutdown():
    print "Shutting down"
    stop()
    subprocess.Popen("sleep 1s && sudo shutdown -h now", shell=True)


# ---------------------------------------------------------------------------
# Handler for chips added/removed
#
def chip_added(id):
	global chip_to_music_mapping_file
	found = False

    print("---added: " +id)
    try:
		prefix = id +" "
        mappingfile = open(chip_to_music_mapping_file, "r")
        data = mappingfile.readlines()
        mappingfile.close()
		for line in data:
			# ignore comments and search for lines starting with chip id
			if not line.startswith("#") and line.startswith(prefix):
				print("found mapping: " +line)
				found = True
				file_to_play = line.replace(prefix, "")
				if file_to_play == "shutdown":
					player.play(id, file_to_play)
				else:
					shutdown()
    except:
        print("Failed to load mapping from file '" +chip_to_music_mapping_file +"'")
	
	if not found:
		print("no mapping found for " +id)	
    return found


def chip_removed(id):
    print("---removed: " +id)
    player.stop()


# ---------------------------------------------------------------------------
# Button for switching off music
#

# Callback-Funktion für Button
def button_off_pressed(channel):
    print "Interrupt - Button gedrueckt"
    player.stop()

gpio_no = 33
# 33 GPIO 13; Mode BOARD
# 40 GPIO 21; Mode BOARD

GPIO.setmode(GPIO.BOARD)
GPIO.setup(gpio_no, GPIO.IN, pull_up_down = GPIO.PUD_UP)

GPIO.add_event_detect(gpio_no, GPIO.BOTH, callback = button_off_pressed, bouncetime = 250)


# ---------------------------------------------------------------------------
# Setting up RFID reader

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

# Helper function for getting system time
current_milli_time = lambda: int(round(time.time() * 1000))

def uid_to_string(id):
    return str(uid[0])+"-"+str(uid[1])+"-"+str(uid[2])+"-"+str(uid[3])


# ---------------------------------------------------------------------------
# Handler for leaving main loop
# 

continue_reading = True

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    print "Ctrl+C captured, ending read."
    continue_reading = False

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)


# ---------------------------------------------------------------------------
# Main loop for detecting chips
# 

print "Music box starting!"
print "Press Ctrl-C to stop."

current_chip_id = None
last_detection_time = None


# This loop keeps checking for chips. If one is near it will get the UID and authenticate
while continue_reading:
    
    # Scan for cards    
    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    # If a card is found
    if status == MIFAREReader.MI_OK:
        if message_level >= 3:
            print "Card detected"
        # Get the UID of the card
        (status,uid) = MIFAREReader.MFRC522_Anticoll()

    # If we have the UID, continue
    if status == MIFAREReader.MI_OK:
        uid_str = uid_to_string(uid)

        if message_level >= 3:
            print "Card read UID: "+uid_str
		
        if current_chip_id == None:
			# New chip detected and no previous chip
            current_chip_id = uid_str
            last_detection_time = current_milli_time() 
            chip_added(uid_str);
        else:
            if current_chip_id == uid_str:
				# same chip detected again
                last_detection_time = current_milli_time()
            else:
				# New different chip detected (previous one gone)
                chip_removed(current_chip_id)
                current_chip_id = uid_str
                last_detection_time = current_milli_time()
                chip_added(uid_str)
        # Sleep, to make it more robust
        time.sleep(0.3)
    else:
        if current_chip_id:
			# no chip any longer (previous one gone)
            if message_level >= 3:
                print "No chip present any more"
            if last_detection_time < current_milli_time() -1500:
                chip_removed(current_chip_id)
                current_chip_id = None
            time.sleep(0.2)
        else:
			# no chip and no chip previously
            time.sleep(0.5)


print "Exiting..."

# Cleanup player before exiting
if current_chip_id:
	chip_removed(current_chip_id)

# Free access to GPIO
GPIO.cleanup()
