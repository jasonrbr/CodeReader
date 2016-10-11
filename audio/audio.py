#!/usr/bin/env python
import os
import sys

# Perform text to speech on input with the corresponding modules based on the operating system
def say(input):
	if (sys.platform == 'darwin'):
		os.system('say ' + input)
	elif(sys.platform == 'win32'):
		print('Windows!')
	elif(sys.platform == 'linux2'):
		print('Linux!')
	else:
		print('OS not supported')


say('Hello world')

function = ' foo. ';
params = ' no inputs. ';
returns = ' int. '
say ('function ' + function + params + 'returns a ' + returns)
