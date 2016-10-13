import sublime_plugin, sublime

# TODO: assumes each line contains a single ';'
# TODO: arguments
class Function():
	def __init__(self, view, region, declaration):
		self._view = view
		self._region = region
		self._returns = declaration.split()[0]
		self._name = declaration.split()[1].split('(')[0]

	@property
	def region(self):
		return self._region

	@property
	def name(self):
		return self._name

	@property
	def declaration(self):
		return "function {} returns {}".format(self._name, self._returns)

	def __str__(self):
		func_str = self.declaration + '\n'

		# Get region immediately after declaration
		row = self._view.rowcol(self._region.begin())[0] + 1
		definition_start = self._view.text_point(row, 0)

		# TODO: split by ';'
		definition = self._view.split_by_newlines(
			sublime.Region(definition_start, self._region.end()))

		# Iterate all lines of code in the function
		for line in definition:
			line_str = self._view.substr(line)

			# TODO: just skip?
			if line_str.isspace() or not line_str:
				func_str += 'empty line\n'
			else:
				func_str += line_str.lstrip() + '\n'

		return func_str

# Testing
class ScopeCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		func = Function(self.view, sublime.Region(42, 95), "int main() {")
		print(str(func))