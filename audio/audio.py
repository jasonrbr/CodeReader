#!/usr/bin/env python
import sys

# Perform text to speech on input with the corresponding modules based on the operating system
def say(input):
	if (sys.platform == 'darwin'):
		import os
		os.system('say ' + input)

	elif (sys.platform == 'win32'):
		# Need to install pywin32 for this to work
		# https://sourceforge.net/projects/pywin32/files/pywin32/Build%20220/
		# E.g., pywin32-220.win-amd64-py3.4.exe if you are running python 3.4
		import win32com.client
		speaker = win32com.client.Dispatch("SAPI.SpVoice")
		speaker.Speak(input)

	else:
		print('OS not supported')
