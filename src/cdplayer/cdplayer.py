import os
import dbus
from dbus.mainloop.glib import DBusGMainLoop
import gobject
import subprocess
import signal
import sys
import RPi.GPIO as GPIO

mplayer_process = None
gpio_no = 21 # unterer Knopf im Boden
looping = True


GPIO.setmode(GPIO.BCM)
GPIO.setup(gpio_no, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Callback-Funktion
def Interrupt(channel):
    print "Interrupt erkannt - Button gedrueckt"
    stop_cd()

# Interrupt-Event hinzufuegen, steigende Flanke
GPIO.add_event_detect(gpio_no, GPIO.BOTH, callback = Interrupt, bouncetime = 250)

def device_added(device):
    print("---added: " +device)
    
def device_removed(device):
    print("---removed: " +device)
    
def device_changed(device):
    print("---changed: " +device)
    if is_media_inserted(device):
      print("Media was inserted")
      play_cd()
    else:
      print("Media was removed")
      stop_cd()
    
def is_media_inserted(device):
    device_obj = system_bus.get_object("org.freedesktop.UDisks", device)
    device_props = dbus.Interface(device_obj, dbus.PROPERTIES_IFACE)
    try:
        is_media_available = device_props.Get('org.freedesktop.UDisks.Device', "DeviceIsMediaAvailable")
        if is_media_available:
            return True
        else:
            return False
    except:
        print("DeviceIsMediaAvailable is not set")
        return False
        
def play_cd():
    global mplayer_process
    print("Starting CD Playback")
    mplayer_process = subprocess.Popen(["mplayer", "-cdrom-device", "/dev/cdrom", "cdda://"])

def stop_cd():
    global mplayer_process
    if mplayer_process is not None:
        print("Stopping CD Playback")
        mplayer_process.terminate()
        mplayer_process = None
        # eject cd AFTER terminating mplayer, since mplayer will crash the system
        subprocess.Popen(["eject", "/dev/cdrom"])
        return True
    else:
        return False

if __name__ == '__main__':
    print("Starting automatic CD player")

    DBusGMainLoop(set_as_default=True)
    system_bus = dbus.SystemBus()
    udisk_proxy = system_bus.get_object("org.freedesktop.UDisks", "/org/freedesktop/UDisks")
    udisk_iface = dbus.Interface(udisk_proxy, "org.freedesktop.UDisks")
    udisk_iface.connect_to_signal('DeviceAdded', device_added)
    udisk_iface.connect_to_signal('DeviceRemoved', device_removed)
    udisk_iface.connect_to_signal('DeviceChanged', device_changed)
    
    # Start playback if a CD is inserted
    if is_media_inserted("/org/freedesktop/UDisks/devices/sr0"):
        play_cd()

    # Important, otherwise the interrupt won't work in parallel to the main loop
    gobject.threads_init()
    loop = gobject.MainLoop()
    while looping:
        try:
            loop.run()
        except:
            # stop music if it is playing and
            # terminate program if nothing was playing
            looping = stop_cd()
    
    GPIO.cleanup()
