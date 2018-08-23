import Audio_Utils
import pyaudio
import json
from Audio_Proj_Const import KEY_ID_TO_NAME_MAP, convertJavaKeyIDToRegularKeyID
import os
import time, thread



class SoundCollection:
    def __init__(self, key_bind_map=None):
        self.key_bind_map = key_bind_map
        if self.key_bind_map is None:
            self.key_bind_map = dict()
            for number in "1234567890":
                file_name = "x" + number + ".wav"
                if os.path.exists(file_name):
                    self.key_bind_map[frozenset([number, "next"])] = SoundEntry(file_name)

    def ingestSoundboardJsonConfigFile(self, config_file_path):
        with open(config_file_path) as config_file:
            config_object = json.load(config_file)
            soundboard_entries = config_object["soundboardEntries"]
            for soundboard_entry in soundboard_entries:
                try:
                    path_to_sound_file = soundboard_entry["file"]
                    activation_key_codes = soundboard_entry["activationKeysNumbers"]
                    if os.path.exists(path_to_sound_file):
                        activation_key_names = [KEY_ID_TO_NAME_MAP[convertJavaKeyIDToRegularKeyID(key_code)].lower() for key_code in activation_key_codes]
                        soundEntry_to_add = SoundEntry(path_to_sound_file, activation_keys=activation_key_names)
                        self.key_bind_map[frozenset(activation_key_names)] = soundEntry_to_add
                except:
                    print "failed to ingest", soundboard_entry["file"]


    def addSoundEntry(self, soundEntry):
        copy = frozenset(soundEntry.activation_keys)
        self.key_bind_map[copy] = soundEntry

    def stopAllSounds(self):
        for soundEntry in self.key_bind_map.values():
            soundEntry.stop()

    def resetAllPitches(self):
        for soundEntry in self.key_bind_map.values():
            soundEntry.pitch_modifier = 0

    def shiftAllPitches(self, shift_amount):
        for soundEntry in self.key_bind_map.values():
            soundEntry.pitch_modifier += shift_amount

    def addSoundEntries(self, soundEntries):
        for soundEntry in soundEntries:
            self.addSoundEntry(soundEntry)

    def playSound(self, keys_down_tuple, last_keys_down_tuple, hold_to_play=Fal, restart_instead_of_stop=True):
        if frozenset(keys_down_tuple) in self.key_bind_map: # if the bind for a sound was pressed
            #temp_previous_sound_entry = sound_entry
            sound_entry = self.key_bind_map[frozenset(keys_down_tuple)]
            #if temp_previous_sound_entry.path_to_sound != sound_entry.path_to_sound:
            #    previous_sound_entry = temp_previous_sound_entry


            if not sound_entry.is_playing: # start playing it if it not playing
                thread.start_new_thread(sound_entry.play, tuple())
            elif not hold_to_play: # stop playing it if hold_to_play is off and the key was let go
                thread.start_new_thread(sound_entry.stop, tuple())
                if restart_instead_of_stop: # only start playing the sound over again if restart_after_stopping is true
                    counter = 0
                    while sound_entry.stream_in_use and counter < 1000: # wait for the sound_entry to finish outputting its current chunk to the stream if it is in the middle of doing so
                        time.sleep(.001)
                        counter += 1
                    thread.start_new_thread(sound_entry.play, tuple())
                else:
                    restart_instead_of_stop = True # toggling restart_after_stopping off only lasts for one sound-key-press
        elif hold_to_play and frozenset(last_keys_down_tuple) in self.key_bind_map: # if hold to play is on and we just let go of the key for a sound
            sound_entry = self.key_bind_map[frozenset(last_keys_down_tuple)]
            thread.start_new_thread(sound_entry.stop, tuple())



class SoundEntry:
    def __init__(self, path_to_sound, frames=None, activation_keys=[], is_playing=False, continue_playing=True, pitch_modifier=0):
        self.path_to_sound = path_to_sound
        self.activation_keys = activation_keys,
        self.frames = frames
        self.is_playing = is_playing
        self.continue_playing = continue_playing
        self.pitch_modifier = pitch_modifier
        self.p = pyaudio.PyAudio()
        self.stream_in_use = False

        self.mark_frame_index = False
        self.jump_to_marked_frame_index = True
        self.marked_frame_index = 0

        if self.frames is None and os.path.exists(self.path_to_sound):
            self.frames = Audio_Utils.getFramesFromFile(self.path_to_sound)
            self.frames = Audio_Utils.getNormalizedAudioFrames(self.frames, Audio_Utils.DEFAULT_DBFS)

        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=2,
            rate=44100,
            input=True,
            frames_per_buffer=1024,
            output=True,
            output_device_index=7
        )

        self.stream2 = self.p.open(
            format=pyaudio.paInt16,
            channels=2,
            rate=44100,
            input=True,
            frames_per_buffer=1024,
            output=True,
            output_device_index=5
        )


    def playMultiThreaded(self):
        print "playing", self.path_to_sound
        if not self.is_playing: # start playing it if it not playing
            thread.start_new_thread(self.play, tuple())
        else: # stop playing it if hold_to_play is off and the key was let go
            thread.start_new_thread(self.stop, tuple())
            counter = 0
            while self.stream_in_use and counter < 1000: # wait for the self to finish outputting its current chunk to the stream if it is in the middle of doing so
                time.sleep(.001)
                counter += 1
            thread.start_new_thread(self.play, tuple())


    def play(self, reset_frame_index=True):
        self.is_playing = True
        self.continue_playing = True

        if reset_frame_index:
            frame_index = 0
        else:
            frame_index = self.marked_frame_index

        while frame_index < len(self.frames) and self.continue_playing:
            if self.mark_frame_index:
                self.marked_frame_index = frame_index
                self.mark_frame_index = False
            elif self.jump_to_marked_frame_index:
                frame_index = self.marked_frame_index
                self.jump_to_marked_frame_index = False

            self.stream_in_use = True
            current_frame = self.frames[frame_index]
            current_frame = Audio_Utils.getPitchShiftedFrame(current_frame, self.pitch_modifier)
            self.stream.write(current_frame)
            # self.stream2.write(current_frame)
            #self.stream.write(self.frames[frame_index])

            self.stream_in_use = False

            frame_index += 1

        self.is_playing = False


    def stop(self):
        self.continue_playing = False

    def moveMarkedFrameIndex(self, move_amount):
        self.marked_frame_index = max(0, self.marked_frame_index+Audio_Utils.secondsToFrames(move_amount)) # shift back in frames by .2 seconds. used max() with 0 to not get out of bounds error

    def markCurrentFrameIndex(self):
        self.mark_frame_index = True # in the loop of the self.Play() method, we check to see if this is true. if it is true, we mark the current frame index and then set this back to false

    def jumpToMarkedFrameIndex(self):
        self.jump_to_marked_frame_index = True
        if not self.is_playing:
            self.play()

    def shiftPitch(self, amount):
        self.pitch_modifier += amount


if __name__ == "__main__":
    sound = SoundEntry("x1.wav")
    sound.play()
