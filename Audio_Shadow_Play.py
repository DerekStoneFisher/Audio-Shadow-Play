import threading


import pyaudio
import Audio_Utils
import pythoncom
import pyHook
import sys
import datetime

frames = []
cached_frames = []
extended_cache = []

keys_down = set()

def updateKeysDown(event):
    if "down" in event.MessageName:
        keys_down.add(str(event.Key).lower())
    if "up" in event.MessageName:
        keys_down.remove(str(event.Key).lower())

def secondsToFrames(n):
    return n*43

def runpyHookThread():
    def OnKeyboardEvent(event):
        global frames, cached_frames, extended_cache, keys_down
        updateKeysDown(event)
        if event.MessageName != 'key up' and event.Alt != 0 and event.Key != 'Lmenu':

            key = str(event.Key).lower()
            if key in "123456789":
                number = int(key)
                frames_to_save = number * 43
                cached_frames = frames[-frames_to_save:]
                extended_cache = frames[-secondsToFrames(5):]
                Audio_Utils.writeFramesToFile(cached_frames, "manual_record.wav");
                print str(datetime.datetime.now()).split('.')[0] + ": " + str(len(cached_frames)/43) + " seconds of audio to 'manual_record.wav' because of user input 'alt + " + key + "'"


            elif key in "qwer":
                Audio_Utils.writeFramesToFile(cached_frames, key + ".wav")
                for i in range(1,6):
                    Audio_Utils.writeFramesToFile(extended_cache[-secondsToFrames(i):], "Extended_Audio" + "/" + key + "-" + str(i) + ".wav")
                print str(datetime.datetime.now()).split('.')[0] + ": saved " + str(len(cached_frames)/43) + " seconds of audio to '" + key + ".wav' because of user input 'alt + " + key + "'"
            elif key == "pause":
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
        if len(frames) % 43 == 0:
            print str(len(frames)/43) + " ",




def main():
    pyHook_t = threading.Thread(target=runpyHookThread)
    pyHook_t.start()
    listen_t = threading.Thread(target=listen)
    listen_t.start()

main()