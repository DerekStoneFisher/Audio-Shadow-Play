from pydub import AudioSegment
import wave
import os
import shutil
import datetime

import pyaudio

def writeFramesToFile(frames, filename, normalize=True):
    if os.path.exists(filename) and "Extended_Audio" not in filename:
        copyfileToBackupFolder(filename)
        os.remove(filename)
    wf = wave.open(filename, 'wb')
    wf.setnchannels(2)
    wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
    wf.setframerate(44100)
    wf.writeframes(b''.join(frames))
    wf.close()
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


def getIndexOfStereoMix():
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    index_of_stereo_mix = None
    for i in range(0, numdevices):
            if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                device_name = p.get_device_info_by_host_api_device_index(0, i).get('name')
                print "Input Device id ", i, " - ", device_name
                if "Stereo Mix" in device_name:
                    index_of_stereo_mix = i
                    print "set index of input device (stereo mix) to " + str(i)
    if index_of_stereo_mix is None:
        raise ValueError("ERROR: COULD NOT FIND STEREO MIX - MAKE SURE IT IS ENABLED")
    return index_of_stereo_mix