import sublime
import sublime_plugin
from .audio import say

help_text = '''This is the help text. Use the arrow keys to cycle through the available functions or classes. Press enter to make a selection. Command: _____ Toggle line numbers on or off. Use the arrow keys to read through a function. End of the help document.'''

class HelpMeCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		say(help_text)