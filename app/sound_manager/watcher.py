import time
import threading
import blinker
import openal

default_device_changed = blinker.Signal("The default sound output device just changed.")

ALC_ALL_DEVICES_SPECIFIER = 0x1013

def watch_device():
    devname = openal.alc.alcGetString(None, ALC_ALL_DEVICES_SPECIFIER)
    while True:
        time.sleep(1)
        maybe_new = openal.alc.alcGetString(None, ALC_ALL_DEVICES_SPECIFIER)
        if maybe_new != devname:
            devname = maybe_new
            default_device_changed.send(None, device_name=devname)

def start():
    thr = threading.Thread(target=watch_device)
    thr.daemon = True
    thr.start()