import Audio_Utils
import pyaudio
import time


class SoundCollection:
    def __init__(self, key_bind_map=None):
        self.key_bind_map = key_bind_map

        if self.key_bind_map is None:
            self.key_bind_map = dict()
            self.key_bind_map[tuple("o")] = SoundEntry("x1.wav")
            self.key_bind_map[tuple("p")] = SoundEntry("x2.wav")

class SoundEntry:
    def __init__(self, path_to_sound, frames=None, modifier_keys=[], activation_key="", is_playing=False, continue_playing=True, pitch_modifier=1.0):
        self.path_to_sound = path_to_sound
        self.modifier_keys = modifier_keys,
        self.activation_key = activation_key,
        self.frames = frames
        self.is_playing = is_playing
        self.continue_playing = continue_playing
        self.pitch_modifier = pitch_modifier
        self.p = pyaudio.PyAudio()

        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=2,
            rate=44100,
            input=True,
            frames_per_buffer=1024,
            output=True
        )

        if self.frames is None:
            self.frames = Audio_Utils.getFramesFromFile(self.path_to_sound)

    def play(self):
        self.is_playing = True
        self.continue_playing = True



        for frame in self.frames:
            if self.continue_playing:
                self.stream.write(frame)

        self.is_playing = False

    def stop(self):
        self.continue_playing = False


if __name__ == "__main__":
    sound = SoundEntry("x1.wav")
    sound.play()
