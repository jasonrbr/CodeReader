import sublime
import sublime_plugin
import re
from collections import deque
from .scope import Function
from .menu import MenuOptions

# TODO only works for built in types
type_patt = re.compile('(string|int|double|bool)') #TODO remove
var_types = r'(string|int|double|bool|void)'
# TODO how to include open bracket?
variable_patt = re.compile(var_types+r'\s([\w]+)\s?\=?\s?([\w]+)?;')
function_patt = re.compile(var_types+r'\s([\w]+)\((.*)\)')
class_patt = re.compile(r'(class|struct)\s([\w]+)\s?\{')
function_end_patt = re.compile(r'\}')

class Hierarchy:
	def _get_child_region(self, child_start_point, end_search_point):
		regions = self._view.split_by_newlines(
			sublime.Region(child_start_point, end_search_point))

		open_bracket_count = 0
		close_bracket_count = 0

		end_point = child_start_point
		for region in regions:
			region_str = self._view.substr(region)

			if '{' in region_str:
				open_bracket_count += region_str.count('{')
			if '}' in region_str:
				close_bracket_count += region_str.count('}')
			
			end_point = region.end();

			if open_bracket_count == close_bracket_count:
				break

		region = sublime.Region(child_start_point, end_point)

		if open_bracket_count == close_bracket_count:
			return sublime.Region(child_start_point, end_point)
		# Scope never ends
		else:
			return None

	def __init__(self, view, name, region, parent=None):
		self._view = view
		self._name = name
		self._parent = parent
		# TODO: list of regions or Scope objects?
		# TODO: rename 'others'
		self._children = {
			'others' : list(),
			'classes' : list(),
			'functions' : list()}

		idx = 0
		while True:
			child_declaration = view.find(
				var_types+r'\s([\w]+)\((.*)\)', idx)

			if not child_declaration:
				return

			child_region = self._get_child_region(
				child_declaration.end() + 1, region.end())

			if not child_region:
				# TODO: needs more descriptive error message
				print("No end bracket found")
				return None

			func = Function(self._view, child_region)
			func_dict = {func.name : func.region}
			#print(func_dict)
			#TODO check if function?

			self._children['functions'].append(func_dict)

			idx = func.region.end() + 1

	def output(self):
		print('Scope: {}'.format(self._name))
		
		for key, val in self._children.items():
			print("    {}:".format(key))
			for region in val:
				func = Function(self._view, region)
				print("        {}".format(func.get_name()))

	@property
	def functions(self):
		return self._children['functions']

	@property
	def classes(self):
		return self._children['classes']

	# Todo: rename
	@property
	def others(self):
		return self._children['others']
	

# TODO: only works for single file
class MenuOptionsCommand(sublime_plugin.TextCommand, sublime_plugin.WindowCommand):
	def run(self, edit):
		file_start = 0
		file_end = self.view.size()

		menu = MenuOptions(sublime.active_window())

		#src_code = self.view.split_by_newlines(sublime.Region(file_start, file_end))
		src_code = sublime.Region(file_start, file_end)
		head = Hierarchy(view=self.view, name='Global', region=src_code)

		keys = list()
		for idx in range(0, len(head.functions)):
			for key in head.functions[idx]:
				keys.append(key)

		menu.display_menu(keys)

		"""while True:
			cmd = self.window.show_input_panel("Selection:", "", self.on_done, None, None)
			if not cmd:
				return
			# handle non-functions
			if cmd is 'function':
				print(head.functions)
			else:
				print('{} inputted'.format(cmd))"""