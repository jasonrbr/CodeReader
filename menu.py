import sublime
import sublime_plugin
from .scopes import *

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

	# @param: child_type: when child_type == None, returns a list
	#					  of available child_types. If the node doesn't
	#					  have a certain child_type, it's not included
	#					  in the list. Child types include func_type
	#					  class_type, and other_type
	#
	#					  when child_type != None, returns a list of
	#					  all children with that available type. If none
	#					  exist, returns None
	def get_children(self, child_type=None):
		if child_type and child_type in self._children and len(self._children[child_type]):
			return self._children[child_type]

		if not child_type:
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
	
	# Stores all children found within the body of this
	# MenuNode's scope
	def _generate_children(self):
		idx = self._scope.body.begin()
		while True:
			start_region = \
				self._view.find('{', idx)

			# All available children have been found
			if not start_region:
				return

			# All children in scope have been found
			if start_region.end() > self._scope.body.end():
				return

			child = self._get_child(start_region)	

			# A child is missing a closing bracket
			if not child:
				return

			self._children[child.type].append(child)	

			idx = child.body.end() + 1

	# Find and returns a child of this MenuNode's scope
	#	@param: start_region: region containing the declaration of
	#			the child
	def _get_child(self, start_region):
		# Get child's declaration
		declaration = self._view.substr(self._view.line(start_region))

		# Get child's definition (body)
		body_start_row = self._view.rowcol(start_region.begin())[0] + 1
		body_start_point = self._view.text_point(body_start_row, 0)
		body = self._get_child_body(body_start_point, self._scope._body.end())

		# Child has no closing bracket
		if not body:
			return None

		if 'class' in declaration or 'struct' in declaration:
			return Class(self._view, body, declaration)
		else:
			return Function(self._view, body, declaration)

	# NOTE: Assumes all lines contain and end with a single ';'
	#
	# Finds and returns the Region containing the child's definition (body)
	# 	@param: start_point: point located in the first line of the child body
	#	@param: end_point: point at end of the MenuNode's scope. If final '}' is
	#			not found once this point is reached, the child has no closing
	# 			bracket (compile error) and 'None' is returned
	def _get_child_body(self, start_point, end_point):	
		body_regions = \
			self._view.split_by_newlines(
				sublime.Region(start_point, end_point))

		# Tracks the number of open/closed brackets
		# respectively
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
		
		# Child has no closing bracket
		if open_count != closed_count:
			return None

		return sublime.Region(start_point, end_point)

# Test
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
