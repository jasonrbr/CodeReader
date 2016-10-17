import sublime
import sublime_plugin
import os

help_text = '''This is the help menu. If on Windows, use the key binding "Control w" to close. If on Mac, key binding "Command w" to close.
Use the arrow keys to cycle through the available functions or classes.
Press enter to make a selection.
Command: _____ Toggle line numbers on slash off.
Use the arrow keys to read through a function
End of the help document.
If on Windows, use the key binding "Control w" to close. If on Mac, key binding "Command w" to close.'''

class HelpCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		say(help_text)