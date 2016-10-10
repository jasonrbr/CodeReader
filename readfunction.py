import sublime, sublime_plugin

class ReadFunctionCommand(sublime_plugin.TextCommand):
	# TODO: should this find and return the function ending?
	#		more efficient, but bad design
	# NOTE: prints region line by line (instead of printing whole region)
	#		to make it easier to incorporate key bindings :)
	def print_func(self, func_region):
		curr_region = self.view.line(func_region.a)
		curr_row, _ = self.view.rowcol(curr_region.a)
		end_row, _ = self.view.rowcol(func_region.b)

		# Output each line in the function
		# NOTE: emulates do-while loop
		while True:
			print(self.view.substr(curr_region))
			curr_row += 1
			if curr_row > end_row:
				break
			next_row_starting = \
				self.view.text_point(curr_row, 0)
			curr_region = self.view.line(next_row_starting)

	# TODO: make ignore for loops !!
	# TODO: also return function end? Probs inefficent
	#	start: point to start looking for the function
	def find_func(self, start):
		# TODO: what if { is on different line than function name? Use a region...
		func_start_region = self.view.line(self.view.find("{", start))
		if not func_start_region:
			return None

		func_end_region = self.view.find("}", func_start_region.a)
		if not func_end_region:
			# TODO: Include function name :p
			raise RuntimeError("No end bracket found")

		return sublime.Region(func_start_region.a, func_end_region.b)

	def run(self, edit):
		file_start = 0
		try:
			func_region = self.find_func(file_start)
			if func_region:
				self.print_func(func_region)
			else:
				print("No function found")
		except RuntimeError as e:
			print(str(e))
