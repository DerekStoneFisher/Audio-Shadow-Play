import threading
import time


import pyaudio
import Audio_Utils
import pythoncom
import pyHook
import sys
import datetime

frames = []
cached_frames = []
extended_cache = []

keys_down = []
keyToExtendedSoundMap = dict()

def updateKeysDown(event):
    key = str(event.Key).lower()
    if "down" in event.MessageName and key not in keys_down:
        keys_down.append(key)
    if "up" in event.MessageName:
        keys_down.remove(key)

def secondsToFrames(n):
    return int(n*43)

def runpyHookThread():
    def OnKeyboardEvent(event):
        global frames, cached_frames, extended_cache, keys_down
        updateKeysDown(event)
        key = str(event.Key).lower()

        if len(keys_down) == 2:
            if keys_down[0] in "qwer" and str(keys_down[1]) in "123456789":
                letter = keys_down[0]
                number = str(float(keys_down[1])/2)
                Audio_Utils.swapAudioFileOutForExtendedVersion(letter+".wav", number)
            elif keys_down[0] == "lmenu" and keys_down[1] in "qwer":
                time.sleep(.25)
                print "SAVED " + keys_down[1]
                cached_frames = frames[-secondsToFrames(1):]
                extended_cache = frames[-secondsToFrames(5):]
                Audio_Utils.writeFramesToFile(cached_frames, key + ".wav")
                for i in range(1,10):
                    half_i = float(i)/2
                    Audio_Utils.writeFramesToFile(extended_cache[-secondsToFrames(half_i):], "Extended_Audio" + "/" + key + "-" + str(half_i) + ".wav")
            elif keys_down[0] in "qwer" and keys_down[1] == "oem_3": # oem_3 is tilde
                Audio_Utils.copyFileToBackupFolder(keys_down[0]+".wav", "Favorites")
            elif keys_down[0] == "lmenu" and keys_down[1] == "pause":
                sys.exit()

        return True



    hm = pyHook.HookManager()
    hm.KeyDown = OnKeyboardEvent
    hm.KeyUp = OnKeyboardEvent
    hm.HookKeyboard()
    try:
        pythoncom.PumpMessages()
    except KeyboardInterrupt:
        pass

def listen():
    global frames
    stream = pyaudio.PyAudio().open(
        format=pyaudio.paInt16,
        channels=2,
        rate=44100,
        input=True,
        frames_per_buffer=1024,
    )

    while True:
        read_result = stream.read(1024)
        if len(frames) > secondsToFrames(60):
            frames = frames[-secondsToFrames(10):]
        frames.append(read_result)




def main():
    pyHook_t = threading.Thread(target=runpyHookThread)
    pyHook_t.start()
    listen_t = threading.Thread(target=listen)
    listen_t.start()

if __name__ == "__main__":
    main()