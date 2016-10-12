# parse cpp file and make a 'dom'-line tree

import sublime
import sublime_plugin
import re
from collections import deque
# function, class level scopes
# not loops

# TODO only works for built in types
type_patt = re.compile('(string|int|double|bool)') #TODO remove
var_types = r'(string|int|double|bool|void)'
variable_patt = re.compile(var_types+r'\s([\w]+)\s?\=?\s?([\w]+)?;')
function_patt = re.compile(var_types+r'\s([\w]+)\((.*)\)')
class_patt = re.compile(r'(class|struct)\s([\w]+)\s?\{')
function_end_patt = re.compile(r'\}')

class Scope():
	def __init__(self, name_in, return_type_in, parent_in=None, \
				 children_in=list(), variables_in=list(), extras_in=list()):
		self.name = name_in
		self.return_type = return_type_in
		self.parent = parent_in
		self.children = children_in
		self.variables = variables_in
		self.extras = extras_in

	def __str__(self):
		# return ' '.join([self.return_type, self.name, "variables({})".format(str(len(self.variables))), "children({})".format(str(self.children)), 'extras({})'.format(len(self.extras))])
		return ' '.join([self.return_type, self.name])

	# Returns region of child, returns None
	# if child doesn't exist yo
	#def get_child()

""" return root node to the hierarchy
 	assumes only 1 bracket per line at the moment
 	assumes you put open bracket on the same line as function declaration
 	file is list of strings of content of file """
def GetHierarchy(view, region, name, return_type=None):
	# TODO: don't pass in name or return type? :/
	scope = Scope(name_in=name, return_type_in=return_type)

	idx = region.begin()
	#while idx < view.size():
	# TODO: make work for classes, girl
	child_declaration = view.find(var_types+r'\s([\w]+)\((.*)\)', idx)
	print(child_declaration)
	idx = child_declaration.end() + 1
	print(idx)

	child_declaration = view.find(var_types+r'\s([\w]+)\((.*)\)', idx)
	print(child_declaration)
	idx = child_declaration.end() + 1
	print(idx)

	"""#count = 0
	for idx in range(0, len(content)):
		line = content[idx]
		if function_patt.match(line):
			#count += 1
			return_type = function_patt.match(line).group(1)
			name = function_patt.match(line).group(2)
			child, idx = GetFunctionDefinition(name, return_type, content[idx+1:])

			scope.children.append(child)
		elif variable_patt.match(line):
			v = Variable(getType(line), getName(line), getValue(line))
			scope.variables.append(v)
		else:
			scope.extras += line
			#print(line)


	# TODO test end line num?
	return scope, count"""

class Variable():
	def __init__(self, type_in, name_in, value_in):
		self.type = type_in
		self.name = name_in
		self.value = value_in

# returns matched type; returns none if not found
def getType(line):
	return variable_patt.match(line).group(1)

def getName(line):
	return variable_patt.match(line).group(2)

def getValue(line):
	return variable_patt.match(line).group(3)

# content is list of string, starting with first line of declaration
# returns Scope containing the content, and next_idx if function ends
def GetFunctionDefinition(name, return_type, content):

	func_scope = Scope(name_in=name, return_type_in=return_type)
"""
	#print('defining func', name)
	for idx in range(0, len(content)):
		line = content[idx]
		if function_patt.match(line):
			return_type = function_patt.match(line).group(1)
			name = function_patt.match(line).group(2)
			child, idx = GetFunctionDefinition(content[idx+1:])

			func_scope.children.append(child)
		elif variable_patt.match(line):
			v = Variable(getType(line), getName(line), getValue(line))
			func_scope.variables.append(v)
		elif function_end_patt.match(line):
			return func_scope, idx+1
		else:
			func_scope.extras += line
			#print('skipped', line)


	#print("Function never ended. Terminating.")
	exit(1)"""

"""def printHierarchy(head):
	print("Hello World")
	#q = deque()
	#q.appendleft(head)

	#i = 0
	#while i < 100:
	#	print(i)
	#	cur_node = q.pop()
		# print(str(cur_node))
	#	for child in cur_node.children:
	#		q.appendleft(child)"""

# TODO: only works for single file
class MenuOptionsCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		file_start = 0
		file_end = self.view.size()

		#src_code = self.view.split_by_newlines(sublime.Region(file_start, file_end))
		src_code = sublime.Region(file_start, file_end)
		head = GetHierarchy(view=self.view, region=src_code, name="Global")
		# head, end_idx = GetHierarchy(txt.split('\n'))
		# if end_idx != self.view.size():
		# 	print('end_idx={}, size={}'.format(end_idx, self.view.size()))
		# printHierarchy(head)
		#printHierarchy(head)
		#print ("Count: {}".format(num_scopes_found))
		#print('done')
		# return head

