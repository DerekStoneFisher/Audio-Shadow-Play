from pydub import AudioSegment
import wave
import os
from shutil import copyfile
import datetime

import pyaudio

def writeFramesToFile(frames, filename, normalize=True):
    wf = wave.open(filename, 'wb')
    wf.setnchannels(2)
    wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
    wf.setframerate(44100)
    wf.writeframes(b''.join(frames))
    wf.close()
    if os.path.exists(filename) and "Extended_Audio" not in filename:
        copyFileToBackupFolder(filename)
    if normalize:
        normalizeAudioFile(filename)


def normalizeAudioFile(filename, target_dBFS=-10.0):
    def match_target_amplitude(sound, target_dBFS):
        change_in_dBFS = target_dBFS - sound.dBFS
        return sound.apply_gain(change_in_dBFS)

    sound = AudioSegment.from_file(filename, "wav")
    normalized_sound = match_target_amplitude(sound, target_dBFS)
    normalized_sound.export(filename, format="wav")

def copyFileToBackupFolder(filename, folder=None):
        if folder == None:
            if "manual_record" in filename:
                folder = "Manual_Records"
            else:
                folder = "Audio_Backups"
        formatted_date = str(datetime.datetime.now()).split('.')[0].replace(":", "_")
        number_of_bytes_in_one_second_of_audio = float(198656) # kind of arbitrary, I calculated it from one of my files
        seconds_in_file_formatted_nicely = str(round(os.path.getsize(filename)/number_of_bytes_in_one_second_of_audio, 1)).replace(".", ",")
        copyfile(filename, folder + "/" + filename.replace(".wav", "") + " " + seconds_in_file_formatted_nicely + " seconds - " + formatted_date + ".wav")

def swapAudioFileOutForExtendedVersion(filename, new_duration):
    extended_path = "Extended_Audio" + "/" + filename.split(".")[0] + "-"+new_duration + ".wav"
    copyfile(extended_path, filename) # replace old file with extended version
    print "COPIED " + extended_path + " TO " + filename