import sublime_plugin, sublime

class Scope():
	def __init__(self, name_in, return_type_in, parent_in=None, \
				 children_in=list(), variables_in=list(), extras_in=list()):
		#self.name = name_in
		self.return_type = return_type_in
		#self.parent = parent_in
		self.children = children_in
		self.variables = variables_in
		self.extras = extras_in

	#def __str__(self):
		# return ' '.join([self.return_type, self.name, "variables({})".format(str(len(self.variables))), "children({})".format(str(self.children)), 'extras({})'.format(len(self.extras))])
	#	return ' '.join([self.return_type, self.name])

# TODO: assumes each line contains a single ';'
# TODO: arguments
# TODO: get rid of hierarchy? :/
class Function(Scope):
	# Assumes function_region stores a valid function 
 	# 	declaration/definition.
	# params:
	#	function_region_: region that stores a valid function
	#		declaration/definition
	#
	#	view_: sublime view that contains the function region 
	def __init__(self, function_region_, view_):
		self.function_region=function_region_
		self.view=view_

	# returns string containing this Function's declaration 
	# (includes '{')
	def _get_literal_declaration(self):
		declaration = self.view.line(
			self.view.find('{', self.function_region.begin()))
		return self.view.substr(declaration).split('{')[0] + '{'

	# returns string containing this Function's return type
	def _get_return_type(self,declaration):
		return self._get_literal_declaration().split()[0]

	# returns string containing this Function's name
	def _get_name(self, declaration):
		name = self._get_literal_declaration().split()[1]
		return name.split('(')[0]

	# returns string describing this Function's declaration
	# in layman's terms
	def get_declaration(self):
		declaration = self._get_literal_declaration()
		return "function {} returns {}".format(
			self._get_name(declaration),
			self._get_return_type(declaration))

	# output the declaration and each line in the function
	#	without leading whitespace
	# TODO: incorporate keyboard navigation
	# TODO: ignore whitespace lines?
	# TODO: don't print final bracket! 
	#			print "function end on line {}" instead
	# TODO: split region by ';' rather than newlines....
	# TODO: possibly store body in initialization
	def output(self):
		print(self.get_declaration())

		# Get point after declaration
		row = self.view.rowcol(self.function_region.a)[0] + 1
		start_point = self.view.text_point(row, 0)

		function_body_lines = self.view.split_by_newlines(
			sublime.Region(start_point, self.function_region.b))

		for region in function_body_lines:
			region_str = self.view.substr(region)
			
			if region_str.isspace() or not region_str:
				print("empty line")
			else:
				print(region_str.lstrip())

# Testing
class ScopeCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		func = Function(sublime.Region(42, 95), self.view)
		func_str = func.get_declaration()
		func.output()