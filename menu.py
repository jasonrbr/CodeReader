import sublime
import sublime_plugin
from .function import Function

# TODO: use pypeg
class MenuNode():
	def _get_child(self, start_region):
		# Get declaration
		declaration = self._view.line(start_region)

		regions = \
			self._view.split_by_newlines(
				sublime.Region(declaration.begin(), 
							   self._region.end()))

		open_count = 0
		closed_count = 0

		end_point = None
		for region in regions:
			line = self._view.substr(region)

			if '{' in line:
				open_count += line.count('{')
			if '}' in line:
				closed_count += line.count('}')

			end_point = region.end()
				
			if open_count == closed_count:
				break

		# Missing closing bracket
		if open_count != closed_count:
			return None, None

		child_region = sublime.Region(declaration.begin(), end_point)
		declaration_str = self._view.substr(declaration)

		# TODO: other
		# Seprate classes and structs?
		if "class" in declaration_str or "struct" in declaration_str:
			# TODO: class object
			return None, 'classes'
		else:
			func = Function(self._view, 
							child_region,
							declaration_str)

			return func, 'functions'

	# TODO: use pypeg
	# TODO: only works when '{' on same line
	def _generate_children(self):
		# TODO: rename 'others'
		self._children = {
			'others' : list(),
			'classes' : list(),
			'functions' : list()}	

		# TODO: prevent class/struct from selecting self
		idx = self.region.begin()
		while True:
			# TODO: use pypeg
			start_region = \
				self._view.find('{', idx)

			# All children have been found
			if not start_region:
				return

			child, child_type = self._get_child(start_region)	

			if not child:
				return

			self._children[child_type].append({child.name : child})	

			idx = child.region.end() + 1

	def __init__(self, view, name, region, parent=None):
		self._view = view
		self._name = name
		self._region = region

		self._parent = parent
		self._generate_children()	

	@property
	def name(self):
		return self._name

	@property
	def region(self):
		return self._region

	@property
	def parent(self):
		return self._parent

	def get_children(self, key=None):
		if key and key in self._children:
			return self._children[key]

		if not key:
			keys = list()
			for key, value in self._children.items():
				if len(value):
					keys.append(key)
			return keys
		
		return None

class MenuCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		file_start = 0
		file_end = self.view.size()

		menu = MenuNode(self.view, name="Global",
			region=sublime.Region(file_start, file_end))

		print(menu.get_children())
		print(menu.get_children('functions'))
	
	
