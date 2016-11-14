import sublime_plugin
import os
from .audio import say


# A key binding will activate this function to read aloud the help menu
# located in help.txt
class OpenHelpCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        fn = os.path.join(os.path.dirname(__file__), 'help.txt')
        with open(fn, 'r') as myfile:
            data = myfile.read().replace('\n', '')
            say(data)
