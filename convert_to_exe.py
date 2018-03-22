import py2exe
from distutils.core import setup

if __name__ == "__main__":
    setup(windows=['Audio_Shadow_Play.py'])


    # , options={
    #     'py2exe':{
    #         'packages':['pyaudio']
    #     }
    # }