import sublime
import sublime_plugin
from .menu import MenuNode	

# TODO: only works for single file
class CodeReaderCommand(sublime_plugin.TextCommand):
	def run(self, edit):		
		file_start = 0
		file_end = self.view.size()
		src_code = sublime.Region(file_start, file_end)

		root = MenuNode(view=self.view, name="Global", region=src_code)
		print("parent: {}".format(root.parent))
		print("children:")

		options = root.get_children()
		for option in options:
			print('    {}'.format(option))
			children = root.get_children(option)
			for child in children:
				for key in child:
					print('           {}'.format(key))
