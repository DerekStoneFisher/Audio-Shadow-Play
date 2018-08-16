import Sound
import threading
import time
import thread
from KeyPress import KeyPressManager, SoundBoardState


import pyaudio
import Audio_Utils
import pythoncom
import pyHook
import sys
import subprocess
import psutil

from pydub import AudioSegment
import wave
import os
import shutil
import datetime

import pyaudio



frames = []
cached_frames = []
extended_cache = []
record_start = None
record_end = None
keys_down = []
last_keys_down = []
keyToExtendedSoundMap = dict()
hold_to_play = False

restart_after_stopping = True
restart_after_stopping_key = "tab"

mark_frame_index_of_last_sound = False
mark_frame_index_of_last_sound_key = "oem_3"
jump_to_frame_index_of_last_sound = False
jump_to_frame_index_of_last_sound_key = "q"
move_marked_frame_forward_key = "up"
move_marked_frame_backward_key = "down"

set_of_keys_to_ignore = {restart_after_stopping_key, mark_frame_index_of_last_sound_key, jump_to_frame_index_of_last_sound_key}

last_sound_entry = None


def updateLastKeysDown():
    global last_keys_down
    last_keys_down = []
    for key in keys_down:
        last_keys_down.append(key)

def updateKeysDown(event):
    global keys_down
    key = str(event.Key).lower()
    if "down" in event.MessageName and key not in keys_down:
        keys_down.append(key)
    if "up" in event.MessageName and key not in set_of_keys_to_ignore:
        keys_down.remove(key)

def secondsToFrames(seconds):
    return int(seconds*43)

def framesToSeconds(frames):
    return '%.2f' % (float(frames)/43)


soundExample1 = Sound.SoundEntry("x1.wav")
soundCollection = Sound.SoundCollection()
soundBoardState = SoundBoardState()
keyPressManager = KeyPressManager(soundBoardState)

def runpyHookThread():
    def OnKeyboardEvent(event):
        global frames, cached_frames, extended_cache, keys_down, record_start, record_end, hold_to_play, restart_after_stopping,\
        mark_frame_index_of_last_sound, mark_frame_index_of_last_sound_key, jump_to_frame_index_of_last_sound, jump_to_frame_index_of_last_sound_key,\
        last_sound_entry, move_marked_frame_backward_key, move_marked_frame_forward_key, keyPressManager

        keyPressManager.processKeyEvent(event)
        updateLastKeysDown()
        updateKeysDown(event)
        if len(keys_down) == 1:
            if keys_down[0] == restart_after_stopping_key:
                del(keys_down[0])
                restart_after_stopping = False
            elif keys_down[0] == mark_frame_index_of_last_sound_key:
                del(keys_down[0])
                last_sound_entry.mark_frame_index = True
            elif keys_down[0] == jump_to_frame_index_of_last_sound_key:
                del(keys_down[0])
                last_sound_entry.jump_to_marked_frame_index = True

        if last_sound_entry is not None:
            print last_sound_entry.path_to_sound
            print last_sound_entry.mark_frame_index, last_sound_entry.jump_to_marked_frame_index
                
                

        if keys_down != last_keys_down:
            print keys_down
            keys_down_tuple = tuple(keys_down)
            last_keys_down_tuple = tuple(last_keys_down)
            
            
            if mark_frame_index_of_last_sound:
                last_sound_entry.mark_frame_index = True
            if jump_to_frame_index_of_last_sound:
                last_sound_entry.jump_to_marked_frame_index = True
            if len(keys_down) == 1 and keys_down[0] == move_marked_frame_backward_key and last_sound_entry is not None: # if down pressed, move marked frame back by .1 sec
                last_sound_entry.marked_frame_index = max(0, last_sound_entry.marked_frame_index-secondsToFrames(.2))
            if len(keys_down) == 1 and keys_down[0] == move_marked_frame_forward_key and last_sound_entry is not None: # if up pressed, move marked frame forward by .1 sec
                last_sound_entry.marked_frame_index = max(0, last_sound_entry.marked_frame_index+secondsToFrames(.2))
            
            if keys_down_tuple in soundCollection.key_bind_map: # if the bind for a sound was pressed
                sound_entry = soundCollection.key_bind_map[keys_down_tuple]
                last_sound_entry = sound_entry
                if not sound_entry.is_playing: # start playing it if it not playing
                    thread.start_new_thread(sound_entry.play, tuple())
                elif not hold_to_play: # stop playing it if hold_to_play is off and the key was let go
                    thread.start_new_thread(sound_entry.stop, tuple())
                    if restart_after_stopping: # only start playing the sound over again if restart_after_stopping is true
                        while sound_entry.stream_in_use: # wait for the sound_entry to finish outputting its current chunk to the stream if it is in the middle of doing so
                            time.sleep(.001)
                        thread.start_new_thread(sound_entry.play, tuple())
                    else:
                        restart_after_stopping = True # toggling restart_after_stopping off only lasts for one sound-key-press
            elif hold_to_play and last_keys_down_tuple in soundCollection.key_bind_map: # if hold to play is on and we just let go of the key for a sound
                sound_entry = soundCollection.key_bind_map[last_keys_down_tuple]
                thread.start_new_thread(sound_entry.stop, tuple())

            if len(keys_down) == 3 and set(keys_down) == {"1","2","3"}:
                hold_to_play = not hold_to_play

            if len(keys_down) >= 2:
                if keys_down[0] == "lmenu" and keys_down[1] == "pause":
                    sys.exit()
                elif keys_down[0] == "lmenu" and keys_down[1] == "x":
                    if record_start is None: # if we aren't already recording
                        record_start = len(frames)-1 # save index of current frame
                        print "start recording at " + framesToSeconds(record_start) + "s in frame buffer of size " + framesToSeconds(len(frames)) + "s"
                    else: # if we are already recording
                        time.sleep(.25)
                        record_end = len(frames)-1 # save index of where we stopped recording
                        Audio_Utils.writeFramesToFile(frames[record_start:record_end], "x.wav")
                        print "stopped recording. recorded from " + str(framesToSeconds(record_start)) + "s to " + str(framesToSeconds(record_end)) + "s. Total recording size is " + framesToSeconds(record_end-record_start) + "s. total frame size so far is " + str(framesToSeconds(len(frames))) + "s"
                        record_start = None
                        record_end = None
                elif keys_down[0] in "1234567890" and keys_down[1] == "end":
                    new_file_name = "x" + keys_down[0] + ".wav"
                    shutil.copyfile("x.wav", new_file_name)
                    subprocess.Popen(["audacity.exe", new_file_name], executable="D:/Program Files (x86)/Audacity/audacity.exe")
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
    global frames, record_start
    stream = pyaudio.PyAudio().open(
        format=pyaudio.paInt16,
        channels=2,
        rate=44100,
        input=True,
        frames_per_buffer=1024,
        input_device_index=Audio_Utils.getIndexOfStereoMix()
    )

    while True:
        read_result = stream.read(1024)
        if len(frames) > secondsToFrames(60) and record_start is None: # every 60 seconds, reset the size of our frame array UNLESS we are currently recording something (record_start gets set to a number if we are)
            print "removing all but last 10 seconds of frames. Frame size went from " + str(len(frames)) + " to " + str(len(frames[-secondsToFrames(10):]))
            frames = frames[-secondsToFrames(10):]
        frames.append(read_result)




def main():
    pyHook_t = threading.Thread(target=runpyHookThread)
    pyHook_t.start()
    listen_t = threading.Thread(target=listen)
    listen_t.start()

if __name__ == "__main__":
    main()