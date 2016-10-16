import sublime
import sublime_plugin
import copy
from .menu import MenuNode	
from .scopes import *

# Name of global Scope
global_namespace = 'global namespace'

# Menu option Strings:
exit_program = 'exit' # TODO: get rid of exit?
go_up = 'go up'
read = 'read ' # Concat with scope name

# TODO: only works for single file
# TODO: permanently store global scope?
# TODO: output on hilight for panels?
# TODO: give panel a title
class CodeReaderCommand(sublime_plugin.TextCommand):
	def run(self, edit):		
		file_start = 0
		file_end = self.view.size()
		src_code = sublime.Region(file_start, file_end)
			
		# Set root to Global Namespace node
		global_scope = Scope(view=self.view, body=src_code, name=global_namespace)
		self._node = MenuNode(view=self.view, scope=global_scope)

		self._show_options_menu()

	# Displays a sublime panel
	#	@param: options: list of strings for selection
	#	@param: on_done: callback function
	def _show_panel(self, options, on_done):
		sublime.active_window().show_quick_panel(options, on_done)

	# Displays a panel containing the current node's
	# children of the specified type.
	#	@param: child_type: one of func_type, class_type, 
	#						or other_type
	def _show_children_menu(self, child_type):
		# Options is a tuple because it must store a string
		# and Scope() objects
		self._options = tuple()
		self._options += (go_up,) # TODO: perhaps store parent?

		children = self._node.get_children(child_type)

		if not children:
			self._show_panel(self._options, self._on_children_done)
			return

		panel_options = list()
		panel_options.append(go_up)

		for child in children:
			panel_options.append(child.name)
			self._options += (child,)

		assert(len(panel_options) == len(self._options))

		self._show_panel(panel_options, self._on_children_done)

	# Displays a panel containing the current node's
	# available children types. Types include func_type,
	# class_type, and other_type
	def _show_options_menu(self):
		self._options = list()

		if not self._node.parent:
			self._options.append(exit_program)
		else:
			self._options.append(go_up)

		children = self._node.get_children()

		if children:
			self._options += self._node.get_children()

		# Functions and Classes can be read to the user
		if self._node.scope.type == func_type or \
			self._node.scope.type == class_type:
				self._options.append(read + self._node.name)

		self._show_panel(self._options, self._on_options_done)

	def _on_options_done(self, ind):
		# show_quick_panel() calls its callback with -1
		# if the user cancels the panel
		if(ind == -1):
			return

		selection = self._options[ind]

		if selection == exit_program:
			return

		if selection == go_up:
			self._node = self._node.parent
			self._show_options_menu()
			return

		# When the user reads a scope, neither the current
		# node nor the displayed menu should change
		if (read + self._node.scope.name) in selection:
			print(self._node.scope)
			self._show_options_menu()
		else:
			self._show_children_menu(selection)

	def _on_children_done(self, ind):
		# show_quick_panel() calls its callback with -1
		# if the user cancels the panel
		if(ind == -1):
			return

		selection = self._options[ind]

		if(selection == go_up):
			self._show_options_menu()

		self._node = MenuNode(view=self.view, 
							  scope=selection, 
							  parent=copy.deepcopy(self._node))

		self._show_options_menu()