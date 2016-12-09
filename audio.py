#!/usr/bin/env python
import sys
import os
from .config import *

cur_path = os.path.dirname(os.path.abspath(__file__))

paths = [
    cur_path + '\\site-packages',
    cur_path + '\\site-packages\\win32',
    cur_path + '\\site-packages\\win32\\lib',
]

sys.path.extend(paths)


# Perform text to speech on input with the corresponding modules
# based on the operating system
def say(input):
    if (sys.platform == 'darwin'):
        import os
        # Get user defined speed from config file
        speed = Config.get('speed')
        os.system('say -v Ava -r ' + str(speed) + ' ' + input)

    elif (sys.platform == 'win32'):
        # Need to install pywin32 for this to work
        # Need 64 bit version of Python, and "install for all users"
        # https://sourceforge.net/projects/pywin32/files/pywin32/Build%20220/
        # E.g., pywin32-220.win-amd64-py3.4.exe if you are running python 3.4
        import win32com.client
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        speed = Config.get('speed')
        # speed is done differently in windows, so need to divide by a factor
        speaker.Rate = speed / 30
        speaker.Voice = speak.GetVoices('Name=Microsoft Mary')
        speaker.Speak(input)

    else:
        print('OS not supported')
