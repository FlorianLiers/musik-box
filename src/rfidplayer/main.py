#!/usr/bin/env python
# -*- coding: utf8 -*-

from lib import MFRC522
import RPi.GPIO as GPIO
import signal
import time
import subprocess
import glob
import sys
import getopt

import player_vlc as player
import mapping
import webui

message_level = 2


# Debug tests:
#player.play_vlc_playlist("id", "/mnt/diskflea/music/Alben/Neil Diamond/Millennium Edition/Millennium Edition-Neil Diamond-Both Sides Now.mp3")
#player.play("1", "/mnt/diskflea/music/Alben/Ole Edvard Antonsen/Antonsen, Ole Edvard- Nordic Trumpet Concertos/*")
#player.stop()

# Helper function for shutting down whole system
def shutdown():
    print "Shutting down"
    stop()
    subprocess.Popen("sleep 1s && sudo shutdown -h now", shell=True)


# ---------------------------------------------------------------------------
# Handler for chips added/removed
#
def chip_added(id):
    global gpio_out_chip
    print("---added: " +id)
    GPIO.output(gpio_out_chip, GPIO.HIGH)
    webui.set_latest_chip(id)
    file_to_play = mapping.get_pattern(id)
    if not file_to_play:
        print("chip " +id +" is not mapped to music")
    else:
        if file_to_play == "shutdown":
            shutdown()
        else:
            player.play(id, file_to_play)


def chip_removed(id):
    global gpio_out_chip
    print("---removed: " +id)
    GPIO.output(gpio_out_chip, GPIO.LOW)
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
# Setting up LEDs for signaling status
#
# 16 GPIO 23; Mode BOARD
# 18 GPIO 24; Mode BOARD
gpio_out_standby = 16
gpio_out_chip = 18

# configure pin for output and set it initial to zero
GPIO.setup(gpio_out_standby, GPIO.OUT)
GPIO.output(gpio_out_standby, GPIO.LOW)

GPIO.setup(gpio_out_chip, GPIO.OUT)
GPIO.output(gpio_out_chip, GPIO.LOW)



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
# Parsing command line args
# 

try:
    opts, args = getopt.getopt(sys.argv[1:], "", ["mapping="])
except getopt.GetoptError:
    print sys.argv[0] +" --mapping <mappingfilename>"
    sys.exit(2)

for o, a in opts:
    if o in ("-m", "--mapping"):
        print "Using mapping file: " +a
        mapping.set_mapping_file(a)


# ---------------------------------------------------------------------------
# Web GUI
# 
print "Start web ui on port 8080"
webui.start()


# ---------------------------------------------------------------------------
# Main loop for detecting chips
# 

print "Music box starting!"
print "Press Ctrl-C to stop."

current_chip_id = None
last_detection_time = None

GPIO.output(gpio_out_standby, GPIO.HIGH)

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
                print "No chip present any longer (for " + str(current_milli_time() - last_detection_time) +"ms)"
            if last_detection_time < current_milli_time() -1500:
                chip_removed(current_chip_id)
                current_chip_id = None
            time.sleep(0.2)
        else:
            # no chip and no chip previously
            time.sleep(0.5)


print "Exiting..."

GPIO.output(gpio_out_standby, GPIO.LOW)

webui.stop()

# Cleanup player before exiting
if current_chip_id:
	chip_removed(current_chip_id)

# Free access to GPIO
GPIO.cleanup()
