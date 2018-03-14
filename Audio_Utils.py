from pydub import AudioSegment
import wave
import os
import shutil
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
        copyfileToBackupFolder(filename)
    if normalize:
        normalizeAudioFile(filename)


def normalizeAudioFile(filename, target_dBFS=-20.0):
    def match_target_amplitude(sound, target_dBFS):
        change_in_dBFS = target_dBFS - sound.dBFS
        return sound.apply_gain(change_in_dBFS)

    sound = AudioSegment.from_file(filename, "wav")
    normalized_sound = match_target_amplitude(sound, target_dBFS)
    normalized_sound.export(filename, format="wav")

def copyfileToBackupFolder(filename, folder=None):
        if folder == None:
            if "manual_record" in filename:
                folder = "Manual_Records"
            else:
                folder = "Audio_Backups"
        formatted_date = str(datetime.datetime.now()).split('.')[0].replace(":", "_")
        number_of_bytes_in_one_second_of_audio = float(198656) # kind of arbitrary, I calculated it from one of my files
        seconds_in_file_formatted_nicely = str(round(os.path.getsize(filename)/number_of_bytes_in_one_second_of_audio, 1)).replace(".", ",")
        shutil.copyfile(filename, folder + "/" + filename.replace(".wav", "") + " " + seconds_in_file_formatted_nicely + " seconds - " + formatted_date + ".wav")

def swapAudioFileOutForExtendedVersion(filename, new_duration):
    extended_path = "Extended_Audio" + "/" + filename.split(".")[0] + "-"+new_duration + ".wav"
    shutil.copyfile(extended_path, filename) # replace old file with extended version
    print "COPIED " + extended_path + " TO " + filename

def trimEnd(infile, outfilename, trim_ms):
    infile = wave.open(infile, "r")
    width = infile.getsampwidth()
    rate = infile.getframerate()
    frameCount = infile.getnframes()
    fpms = rate / 1000 # frames per ms
    length = frameCount - (trim_ms*fpms)

    out = wave.open("_"+outfilename, "w")
    out.setparams((infile.getnchannels(), width, rate, length, infile.getcomptype(), infile.getcompname()))

    out.writeframes(infile.readframes(length))
    out.close()
    infile.close()

    shutil.move("_"+outfilename, outfilename)


def trimStart(infile, outfilename, trim_ms):
    infile = wave.open(infile, "r")
    width = infile.getsampwidth()
    rate = infile.getframerate()
    frameCount = infile.getnframes()
    fpms = rate / 1000 # frames per ms
    length = frameCount - (trim_ms*fpms)
    start_index = trim_ms * fpms

    infile.rewind()
    anchor = infile.tell()
    infile.setpos(anchor + start_index)


    out = wave.open("_"+outfilename, "w")
    out.setparams((infile.getnchannels(), width, rate, length, infile.getcomptype(), infile.getcompname()))

    out.writeframes(infile.readframes(length))
    out.close()
    infile.close()

    shutil.move("_"+outfilename, outfilename)

