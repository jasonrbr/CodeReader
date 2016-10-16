import sublime_plugin, sublime

# Scope types
func_type = 'function'
class_type = 'class'
other_type = 'other'

class Scope():
	def __init__(self, view, body, name, s_type=None):
		self._view = view
		self._type = s_type
		self._body = body
		self._name = name
	
	@property
	def type(self):
		return self._type
	
	@property
	def body(self):
		return self._body

	@property
	def name(self):
		return self._name

# TODO: assumes each line contains a single ';'
# TODO: store arguments
class Function(Scope):
	def __init__(self, view, body, declaration):
		super().__init__(view, body,
			  declaration.split()[1].split('(')[0],
			  func_type)

		self._returns = declaration.split()[0]

	@property
	def declaration(self):
		return "function {} returns {}".format(self._name, self._returns)

	def __str__(self):
		func_str = self.declaration + '\n'

		# TODO: split by ';'
		definition = self._view.split_by_newlines(
			sublime.Region(self._body.begin(), self._body.end()))

		# Iterate all lines of code in the function
		for line in definition:
			line_str = self._view.substr(line)

			# TODO: just skip?
			if line_str.isspace() or not line_str:
				func_str += 'empty line\n'
			else:
				func_str += line_str.lstrip() + '\n'

		return func_str

# TODO: assumes each line contains a single ';'
class Class(Scope):
	def __init__(self, view, body, declaration):
		super().__init__(view, body, 
			declaration.split()[1], class_type)

	@property
	def declaration(self):
		return 'class {}'.format(self._name)

	# TODO: make funcs print pretty
	def __str__(self):
		class_str = self.declaration + '\n'

		# TODO: split by ';'
		definition = self._view.split_by_newlines(
			sublime.Region(self._body.begin(), self._body.end()))

		# Iterate all lines of code in the function
		for line in definition:
			line_str = self._view.substr(line)

			# TODO: just skip?
			if line_str.isspace() or not line_str:
				class_str += 'empty line\n'
			else:
				class_str += line_str.lstrip() + '\n'

		return class_str

# Test
class ScopeCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		func = Function(self.view, sublime.Region(82, 122), "int main() {")
		print(str(func))