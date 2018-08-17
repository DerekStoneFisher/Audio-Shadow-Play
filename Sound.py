import Audio_Utils
import pyaudio



class SoundCollection:
    def __init__(self, key_bind_map=None):
        self.key_bind_map = key_bind_map
        if self.key_bind_map is None:
            self.key_bind_map = dict()
            self.key_bind_map[tuple(["o"])] = SoundEntry("x1.wav")
            self.key_bind_map[tuple(["p"])] = SoundEntry("x2.wav")
            self.key_bind_map[tuple(["oem_4"])] = SoundEntry("x3.wav")

    # def addSoundEntry(self, soundEntry):
    #     soundEntry.

    def addSoundEntryies(self, soundEntries):
        for soundEntry in soundEntries:
            self.addSoundEntry(soundEntry)


class SoundEntry:
    def __init__(self, path_to_sound, frames=None, modifier_keys=[], activation_key="", is_playing=False, continue_playing=True, pitch_modifier=0):
        self.path_to_sound = path_to_sound
        self.modifier_keys = modifier_keys,
        self.activation_key = activation_key,
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

    def updateFromState(self, state):
        if state.mark_frame_index_of_last_sound:
            print "mark_frame_index pt2"
            self.mark_frame_index = True
            state.mark_frame_index_of_last_sound = False
        if state.jump_to_frame_index_of_last_sound:
            print "jump_to_marked_frame_index pt2"
            self.jump_to_marked_frame_index = True
            state.jump_to_frame_index_of_last_sound = False
        if state.move_marked_frame_forward: # if down pressed, move marked frame back by .1 sec
            print "marked_frame_index pt2"
            self.marked_frame_index = max(0, self.marked_frame_index-Audio_Utils.secondsToFrames(.2)) # shift back in frames by .2 seconds. used max() with 0 to not get out of bounds error
            state.move_marked_frame_forward = False
        if state.move_marked_frame_backward:
            print "marked_frame_index pt2"
            self.marked_frame_index = max(0, self.marked_frame_index+Audio_Utils.secondsToFrames(.2))
            state.move_marked_frame_backward = False
        if state.pitch_shift_up:
            print "pitch_shift_up pt2"
            self.pitch_modifier += .1
            state.pitch_shift_up = False
        if state.pitch_shift_down:
            print "pitch_shift_down pt2"
            self.pitch_modifier -= .1
            state.pitch_shift_down = False



if __name__ == "__main__":
    sound = SoundEntry("x1.wav")
    sound.play()
