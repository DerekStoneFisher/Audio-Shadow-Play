from pydub import AudioSegment
import pydub.playback
import wave
import os
import shutil
import datetime
import struct
import pyaudio
import numpy as np
import io


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


def getFramesFromFile(filename, normalize=False):
    try:
        if os.path.exists(filename):
            wf = wave.open(filename, 'rb')
            frames = []
            frame = wf.readframes(1024)
            while frame != '':
                frames.append(frame)
                frame = wf.readframes(1024)
            return frames
        else:
            print "error: cannot write file to frames because file does not exist\tfilename=" + str(filename)
    except:
        print "failed to get frames from file", filename



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

def getIndexOfSpeakers():
    p = pyaudio.PyAudio()
    return p.get_default_output_device_info()

def getPitchShiftedFrame(frame, octaves):
    sample_width = pyaudio.PyAudio().get_sample_size(pyaudio.paInt16)
    sound = AudioSegment(frame, sample_width=sample_width, frame_rate=44100, channels=2)

    new_sample_rate = int(sound.frame_rate * (2.0 ** octaves))
    lowpitch_sound = sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate})
    lowpitch_sound = lowpitch_sound.set_frame_rate(44100)

    return lowpitch_sound.raw_data



    #Play pitch changed sound
    #play(lowpitch_sound)

    # frame_copy = frame
    # sampleWidth = pyaudio.PyAudio().get_sample_size(pyaudio.paInt16)
    # frame_copy = np.array(wave.struct.unpack("%dh" % (len(frame_copy) / sampleWidth), frame_copy)) * 2
    #
    # frame_copy = np.fft.rfft(frame_copy, 1)
    # #MANipulation
    # frame_copy = np.fft.irfft(frame_copy, 1)
    # frame_out = np.array(frame_copy * 0.5, dtype='int16') #undo the *2 that was done at reading
    # chunk_out = struct.pack("%dh"%(len(frame_out)), *list(frame_out)) #convert back to 16-bit data
    # return chunk_out



def secondsToFrames(seconds):
    return int(seconds*43)

def framesToSeconds(frames):
    return '%.2f' % (float(frames)/43)
