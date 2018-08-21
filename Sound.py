import Audio_Utils
import pyaudio
import json
from Audio_Proj_Const import KEY_ID_TO_NAME_MAP
import random


class SoundCollection:
    def __init__(self, key_bind_map=None):
        self.key_bind_map = key_bind_map
        if self.key_bind_map is None:
            self.key_bind_map = dict()
            self.key_bind_map[tuple(["o"])] = SoundEntry("x1.wav")
            self.key_bind_map[tuple(["p"])] = SoundEntry("x2.wav")
            self.key_bind_map[tuple(["oem_4"])] = SoundEntry("x3.wav")

    def ingestSoundboardJsonConfigFile(self, config_file_path):
        with open(config_file_path) as config_file:
            config_object = json.load(config_file)
            soundboard_entries = config_object["soundboardEntries"]
            for soundboard_entry in soundboard_entries:
                path_to_sound = soundboard_entry["file"]
                activation_key_codes = soundboard_entry["activationKeysNumbers"]
                activation_key_names = [KEY_ID_TO_NAME_MAP[key_code].lower() for key_code in activation_key_codes]
                soundEntry_to_add = SoundEntry(path_to_sound, activation_keys=activation_key_names)
                self.key_bind_map[tuple(activation_key_names)] = soundEntry_to_add


    def addSoundEntry(self, soundEntry):
        copy = tuple(soundEntry.activation_keys)
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

        if self.frames is None:
            self.frames = Audio_Utils.getFramesFromFile(self.path_to_sound)
            self.frames = Audio_Utils.getNormalizedAudioFrames(self.frames, Audio_Utils.DEFAULT_DBFS)

        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=2,
            rate=44100,
            input=True,
            frames_per_buffer=1024,
            output=True,
            output_device_index=2
        )

    def play(self):
        self.is_playing = True
        self.continue_playing = True

        frame_index = 0
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
