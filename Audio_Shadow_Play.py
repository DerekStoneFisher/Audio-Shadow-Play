import Recorder
import Sound
import threading
import time
import thread
from KeyPress import KeyPressManager
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

hold_to_play = False

soundCollection = Sound.SoundCollection()
soundCollection.ingestSoundboardJsonConfigFile("Board1.json")
for key_bind in soundCollection.key_bind_map:
    print key_bind, soundCollection.key_bind_map[key_bind].path_to_sound
keyPressManager = KeyPressManager(soundCollection)

# just grab any random sound so sound_entry doesn't start as null
sound_entry = next(iter(soundCollection.key_bind_map.values())) # type: Sound.SoundEntry
previous_sound_entry = sound_entry
pause_soundboard = False

pitch_modifiers = {'1':-.5, '2':-.4, '3':-.3, '4':-.2, '5':-.1, '6':0, '7':.1, '8':.2, '9':.3, '0':.4}

audioRecorder = Recorder.AudioRecorder()


def OnKeyboardEvent(event):
    global frames, cached_frames, extended_cache, record_start, record_end, hold_to_play, keyPressManager, sound_entry, previous_sound_entry, pause_soundboard, pitch_modifiers, audioRecorder

    keyPressManager.processKeyEvent(event)
    updateSoundboardConfiguration(keyPressManager, soundCollection)

    keys_down_tuple = tuple(keyPressManager.getKeysDown())
    last_keys_down_tuple = tuple(keyPressManager.getLastKeysDown())

    if len(keys_down_tuple) >= 2 and keys_down_tuple[0] == "menu" and keys_down_tuple[-1] in pitch_modifiers:
        sound_entry.pitch_modifier = pitch_modifiers[keys_down_tuple[-1]]
        thread.start_new_thread(sound_entry.jumpToMarkedFrameIndex, tuple()) # need to call via a thread so we don't get blocked by the .play() which can get called by this function

    if keyPressManager.key_state_changed and not pause_soundboard:
        temp_previous_sound_entry = sound_entry
        temp_sound_entry_or_null = soundCollection.getBestSoundEntryMatchOrNull(keys_down_tuple)

        if temp_sound_entry_or_null is not None:
            sound_entry = temp_sound_entry_or_null
            # update previous_sound_entry to match the new sound_entry if sound_entry has changed since the last time a sound was played
            if temp_previous_sound_entry.path_to_sound != sound_entry.path_to_sound:
                previous_sound_entry = temp_previous_sound_entry

            if not sound_entry.is_playing: # start playing it if it not playing
                thread.start_new_thread(sound_entry.play, tuple())
            elif not hold_to_play: # stop playing it if hold_to_play is off and the key was let go
                thread.start_new_thread(sound_entry.stop, tuple())
                counter = 0
                while sound_entry.stream_in_use and counter < 1000: # wait for the sound_entry to finish outputting its current chunk to the stream if it is in the middle of doing so
                    time.sleep(.001)
                    counter += 1
                thread.start_new_thread(sound_entry.play, tuple())
        elif hold_to_play and frozenset(last_keys_down_tuple) in soundCollection.key_bind_map: # if hold to play is on and we just let go of the key for a sound
            sound_entry = soundCollection.key_bind_map[frozenset(last_keys_down_tuple)]
            thread.start_new_thread(sound_entry.stop, tuple())


        if len(keys_down_tuple) >= 2:
            if keys_down_tuple[0] == "menu" and keys_down_tuple[1] == "pause":
                sys.exit()
            elif keys_down_tuple[0] == "menu" and keys_down_tuple[1] == "x":
                if audioRecorder.record_start is None: # if we aren't already recording
                    audioRecorder.startRecording()
                else:
                    audioRecorder.stopRecording()
                    recording_contents = audioRecorder.getLastRecordingContents()
                    recording_contents = Recorder.getFramesWithoutStartingSilence(recording_contents)
                    soundCollection.getSoundEntryByPath("x.wav").frames = recording_contents
                    Audio_Utils.writeFramesToFile(recording_contents, "x.wav")
            elif keys_down_tuple[0] in "1234567890" and keys_down_tuple[1] == "end":
                new_file_name = "x" + keys_down_tuple[0] + ".wav"
                shutil.copyfile("x.wav", new_file_name)
                soundCollection.key_bind_map[frozenset([keys_down_tuple[0], "next"])] = Sound.SoundEntry(new_file_name)
                subprocess.Popen(["audacity.exe", new_file_name], executable="D:/Program Files (x86)/Audacity/audacity.exe")
    return True

def updateSoundboardConfiguration(keyPressManager, soundCollection):
    global sound_entry, previous_sound_entry, pause_soundboard, hold_to_play
       # key binds that affect all sounds in the sound collection
    if keyPressManager.endingKeysEqual(["return"]): # enter -> stop all currently playing sounds
        soundCollection.stopAllSounds()
    elif keyPressManager.endingKeysEqual(["left", "right"]): # left + right -> reset pitch of all sounds
        soundCollection.resetAllPitches()
    elif keyPressManager.endingKeysEqual(["menu", "left"]): # alt + left -> shift down pitch of currently playing sound
        soundCollection.shiftAllPitches(-.1)
    elif keyPressManager.endingKeysEqual(["menu", "right"]): # alt + right (insert trump joke here xd) -> shift down pitch of currently playing sound
        soundCollection.shiftAllPitches(.1)
    elif keyPressManager.endingKeysEqual(["left"]): # left (without alt) -> shift down pitch of all sounds
        sound_entry.shiftPitch(-.1)
    elif keyPressManager.endingKeysEqual(["right"]): # right (without alt) -> shift up pitch of all sounds
        sound_entry.shiftPitch(.1)

    # non-sound specific configuration key binds
    elif keyPressManager.endingKeysEqual(["2","3","4"]):
        pause_soundboard = not pause_soundboard
        soundCollection.stopAllSounds()
    elif keyPressManager.endingKeysEqual(["1","2","3"]):
        hold_to_play = not hold_to_play



    # key binds that affect the last sound played
    elif keyPressManager.endingKeysEqual(["up"]):
        sound_entry.moveMarkedFrameIndex(.1)
    elif keyPressManager.endingKeysEqual(["down"]):
        sound_entry.moveMarkedFrameIndex(-.1)
    elif keyPressManager.endingKeysEqual(["1","3"]):
        sound_entry.markCurrentFrameIndex()
    elif keyPressManager.endingKeysEqual(["1","4"]):
        thread.start_new_thread(sound_entry.jumpToMarkedFrameIndex, tuple()) # need to call via a thread so we don't get blocked by the .play() which can get called by this function
    elif keyPressManager.endingKeysEqual(["1", "2"]):
        sound_entry, previous_sound_entry = previous_sound_entry, sound_entry # swap current sound with previous sound
    elif keyPressManager.endingKeysEqual(["1", "5"]) or keyPressManager.endingKeysEqual(["oem_3"]):
        sound_entry.stop() # no new thread needed

def runpyHookThread():
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
    global audioRecorder
    pyHook_t = threading.Thread(target=runpyHookThread)
    pyHook_t.start()

    thread.start_new_thread(audioRecorder.listen())
    listen_t = threading.Thread(target=listen)
    listen_t.start()

if __name__ == "__main__":
    main()