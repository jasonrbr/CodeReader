import sublime
import sublime_plugin
from .scopes import *
# TODO: use pypeg

class MenuNode():
	def __init__(self, view, scope, parent=None):
		self._view = view
		self._scope = scope

		self._parent = parent
		self._children = {
			other_type : list(),
			class_type : list(),
			func_type : list()}	

		if self._scope.type != func_type:
			self._generate_children()	

	def get_children(self, key=None):
		if key and key in self._children and len(self._children[key]):
			return self._children[key]

		if not key:
			children = list()
			for key, value in self._children.items():
				if len(value):
					children.append(key)
			if len(children):
				return children
		
		return None

	@property
	def name(self):
		return self._scope._name

	@property
	def parent(self):
		return self._parent

	@property
	def scope(self):
		return self._scope
	
	# TODO: use pypeg
	# TODO: only works when '{' on same line
	# TODO: list of pairs instead of list of dicts
	# TODO: stop at end of region
	def _generate_children(self):
		idx = self._scope.body.begin()
		while True:
			start_region = \
				self._view.find('{', idx)

			# All children have been found
			if not start_region:
				return

			# All children in scope have been found
			if start_region.end() > self._scope.body.end():
				return

			child = self._get_child(start_region)	

			# End bracket not found
			if not child:
				return

			self._children[child.type].append(child)	

			idx = child.body.end() + 1

	# Assumes all lines contain and end with a single ';'
	def _get_child_body(self, start_point, end_point):	
		body_regions = \
			self._view.split_by_newlines(
				sublime.Region(start_point, end_point))

		open_count = 1
		closed_count = 0
		end_point = None

		for region in body_regions:
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
			return None

		return sublime.Region(start_point, end_point)

	def _get_child(self, start_region):
		# Get declaration
		declaration = self._view.substr(self._view.line(start_region))

		# Get body
		body_start_row = self._view.rowcol(start_region.begin())[0] + 1
		body_start_point = self._view.text_point(body_start_row, 0)
		body = self._get_child_body(body_start_point, self._scope._body.end())

		# body not found
		if not body:
			return None

		# TODO: other
		if 'class' in declaration or 'struct' in declaration:
			return Class(self._view, body, declaration)
		else:
			return Function(self._view, body, declaration)

class MenuCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		file_start = 0
		file_end = self.view.size()

		scope = Scope(view=self.view, 
					  body=sublime.Region(file_start, file_end),
					  name="Global")

		menu = MenuNode(self.view, scope=scope)

		print("{}: ".format(menu.name))
		print(menu.get_children())
		print(menu.get_children(class_type))
		print(menu.get_children(func_type))

		children = menu.get_children(class_type)

		classA_menu = MenuNode(self.view, scope=children[0])
		classB_menu = MenuNode(self.view, scope=children[1])
		classC_menu = MenuNode(self.view, scope=children[2])

		assert(classA_menu.get_children() == None)
		assert(classA_menu.get_children(class_type) == None)
		assert(classA_menu.get_children(func_type) == None)
		assert(classA_menu.get_children(other_type) == None)
		print("{}: None".format(classA_menu.name))

		assert(classB_menu.get_children() == None)
		assert(classB_menu.get_children(class_type) == None)
		assert(classB_menu.get_children(func_type) == None)
		assert(classB_menu.get_children(other_type) == None)
		print("{}: None".format(classB_menu.name))

		print("{}: ".format(classC_menu.name))
		print(classC_menu.get_children())
		print(classC_menu.get_children(func_type))
		
		assert(classC_menu.get_children(class_type) == None)
		assert(classC_menu.get_children(other_type) == None)
