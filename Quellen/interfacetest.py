#!/usr/bin/env python
# -*- coding: utf8 -*-

# ----------- Bibliotheken -----------

import RPi.GPIO as GPIO
import signal
import time
import glob


# ----------- Programmsteuerung -----------

# Variable, die angibt, ob Programm laufen soll
continue_loop = True

# Callback for signaling script to end
def end_read(signal, frame):
    global continue_loop
    print "Signal captured, ending!"
    continue_loop = False

# Capture SIGINT and run callback "end_read" if detected
signal.signal(signal.SIGINT, end_read)


# ----------- Pin Setup -----------

# Setup general IO pins:
# Ansprechung der Pins über Board-Namen
GPIO.setmode(GPIO.BOARD)


# ----------- Eingabe mit Registrierung von Tastendruck -----------

# 33 GPIO 13; Mode BOARD
gpio_input = 33

# Pin auf Eingang konfigurieren mit Widerstand
GPIO.setup(gpio_input, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

# Callback-Funktion
def interrupt_handler(channel):
	print "Interrupt - Button gedrueckt"

# Registriere Callback-Funktion für steigende/fallende Flanke für ein Pin
GPIO.add_event_detect(gpio_input, GPIO.BOTH, callback = interrupt_handler, bouncetime = 250)
#                                 -> nur steigende Flanke: GPIO.RAISING


# ----------- Ausgabe -----------

# 40 GPIO 21; Mode BOARD
gpio_output = 40

# Pin auf Ausgang konfigurieren
GPIO.setup(gpio_output, GPIO.OUT)
# Startwert auf Null
GPIO.output(gpio_output, GPIO.LOW)


# Willkommensnachricht
print "Interface test is starting!"
print "Press Ctrl-C to stop."

time_interval_sec = 1.5

# "Blink"-Schleife
while continue_loop:
	time.sleep(time_interval_sec)       # eine Zeitlang aus lassen
	GPIO.output(gpio_output, GPIO.HIGH) # anschalten
	print " - on  - "
	time.sleep(time_interval_sec)       # und eine Zeitlang an lassen
	GPIO.output(gpio_output, GPIO.LOW)  # dann wieder Ausschalten
	print " - off - "

# Programm beenden und aufräumen
print "Ending interface test"
GPIO.cleanup()
