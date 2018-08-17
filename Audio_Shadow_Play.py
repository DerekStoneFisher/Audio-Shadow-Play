import Sound
import threading
import time
import thread
from KeyPress import KeyPressManager, SoundBoardState
from pyHook.HookManager import KeyboardEvent, HookConstants


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
keyToExtendedSoundMap = dict()




soundCollection = Sound.SoundCollection()
soundCollection.ingestSoundboardJsonConfigFile("C:/Users/C17050/Documents/default soundboard.json")
for key_bind in soundCollection.key_bind_map:
    print key_bind, soundCollection.key_bind_map[key_bind]
soundBoardState = SoundBoardState()
keyPressManager = KeyPressManager(soundBoardState, soundCollection)
sound_entry = None

def runpyHookThread():
    def OnKeyboardEvent(event):
        global frames, cached_frames, extended_cache, keys_down_tuple, record_start, record_end, hold_to_play, restart_after_stopping,\
        mark_frame_index_of_last_sound, mark_frame_index_of_last_sound_key, jump_to_frame_index_of_last_sound, jump_to_frame_index_of_last_sound_key,\
        move_marked_frame_backward_key, move_marked_frame_forward_key, keyPressManager, sound_entry

        keyPressManager.processKeyEvent(event)

        if keyPressManager.endingKeysEqual(["return"]):
            soundCollection.stopAllSounds()
        if keyPressManager.endingKeysEqual(["left"]):
            keyPressManager.soundCollection.shiftAllPitches(-.1)
        if keyPressManager.endingKeysEqual(["right"]):
            soundCollection.shiftAllPitches(.1)
        if keyPressManager.endingKeysEqual(["left", "right"]):
            soundCollection.resetAllPitches()


                
                

        if keyPressManager.key_state_changed:
            keys_down_tuple = tuple(keyPressManager.getKeysDown())
            last_keys_down_tuple = tuple(keyPressManager.getLastKeysDown())

            state = keyPressManager.soundBoardState


            if sound_entry is not None:
                thread.start_new_thread(sound_entry.updateFromState, tuple([state]))
            
            if keys_down_tuple in soundCollection.key_bind_map: # if the bind for a sound was pressed
                sound_entry = soundCollection.key_bind_map[keys_down_tuple]
                if not sound_entry.is_playing: # start playing it if it not playing
                    thread.start_new_thread(sound_entry.play, tuple())
                elif not state.hold_to_play: # stop playing it if hold_to_play is off and the key was let go
                    thread.start_new_thread(sound_entry.stop, tuple())
                    if state.restart_after_stopping: # only start playing the sound over again if restart_after_stopping is true
                        counter = 0
                        while sound_entry.stream_in_use and counter < 1000: # wait for the sound_entry to finish outputting its current chunk to the stream if it is in the middle of doing so
                            time.sleep(.001)
                            counter += 1
                        thread.start_new_thread(sound_entry.play, tuple())
                    else:
                        state.restart_after_stopping = True # toggling restart_after_stopping off only lasts for one sound-key-press
            elif state.hold_to_play and last_keys_down_tuple in soundCollection.key_bind_map: # if hold to play is on and we just let go of the key for a sound
                sound_entry = soundCollection.key_bind_map[last_keys_down_tuple]
                thread.start_new_thread(sound_entry.stop, tuple())


            if len(keys_down_tuple) >= 2:
                if keys_down_tuple[0] == "menu" and keys_down_tuple[1] == "pause":
                    sys.exit()
                elif keys_down_tuple[0] == "menu" and keys_down_tuple[1] == "x":
                    if record_start is None: # if we aren't already recording
                        record_start = len(frames)-1 # save index of current frame
                        print "start recording at " + Audio_Utils.framesToSeconds(record_start) + "s in frame buffer of size " + Audio_Utils.framesToSeconds(len(frames)) + "s"
                    else: # if we are already recording
                        time.sleep(.25)
                        record_end = len(frames)-1 # save index of where we stopped recording
                        Audio_Utils.writeFramesToFile(frames[record_start:record_end], "x.wav")
                        print "stopped recording. recorded from " + str(Audio_Utils.framesToSeconds(record_start)) + "s to " + str(Audio_Utils.framesToSeconds(record_end)) + "s. Total recording size is " + Audio_Utils.framesToSeconds(record_end-record_start) + "s. total frame size so far is " + str(Audio_Utils.framesToSeconds(len(frames))) + "s"
                        record_start = None
                        record_end = None
                elif keys_down_tuple[0] in "1234567890" and keys_down_tuple[1] == "end":
                    new_file_name = "x" + keys_down_tuple[0] + ".wav"
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
        if len(frames) > Audio_Utils.secondsToFrames(60) and record_start is None: # every 60 seconds, reset the size of our frame array UNLESS we are currently recording something (record_start gets set to a number if we are)
            print "removing all but last 10 seconds of frames. Frame size went from " + str(len(frames)) + " to " + str(len(frames[-Audio_Utils.secondsToFrames(10):]))
            frames = frames[-Audio_Utils.secondsToFrames(10):]
        frames.append(read_result)




def main():
    pyHook_t = threading.Thread(target=runpyHookThread)
    pyHook_t.start()
    listen_t = threading.Thread(target=listen)
    listen_t.start()

if __name__ == "__main__":
    main()