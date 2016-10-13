import sublime_plugin, sublime

# TODO: assumes each line contains a single ';'
# TODO: arguments
class Function():
	# Assumes function_region stores a valid function 
 	# 	declaration/definition.
	# params:
	#	function_region_: region that stores a valid function
	#		declaration/definition
	#
	#	view_: sublime view that contains the function region 
	def __init__(self, view_, function_region_):
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
		return declaration.split()[0]

	# returns string containing this Function's name
	def _get_name(self, declaration):
		name = declaration.split()[1]
		return name.split('(')[0]
	
	# TODO: make property
	def get_declaration(self):
		declaration = self._get_literal_declaration()
		return "function {} returns {}".format(
			self._get_name(declaration),
			self._get_return_type(declaration))

	@property
	def name(self):
		return self._get_name(self._get_literal_declaration())
	

	@property
	def region(self):
		return self.function_region

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
		func = Function(self.view, sublime.Region(42, 95))
		func_str = func.get_declaration()
		func.output()