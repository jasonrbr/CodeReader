#!/usr/bin/env python
import sys
import os

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
        # Rate of speech is 250 words per minute
        # TODO: make this number customizable?
        os.system('say -r 260 ' + input)

    elif (sys.platform == 'win32'):
        # Need to install pywin32 for this to work
        # Need 64 bit version of Python, and "install for all users"
        # https://sourceforge.net/projects/pywin32/files/pywin32/Build%20220/
        # E.g., pywin32-220.win-amd64-py3.4.exe if you are running python 3.4
        import win32com.client
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        speaker.Rate = 5 # edit for rate of speech
        speaker.Speak(input)

    else:
        print('OS not supported')
