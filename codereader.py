import sublime
import sublime_plugin
import copy
from .menu import MenuNode	
from .scopes import *
from .audio import say

# Name of global Scope
global_namespace = 'global namespace'

# Menu option Strings:
exit_program = 'exit'
go_up = 'go up to scope, ' # Concat with scope you're currently in
read = 'reed ' # Concat with scope name
global_name = 'global'

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
	#	@param: on_highlighted: callback function
	def _show_panel(self, options, on_done, on_highlight):
		sublime.active_window().show_quick_panel(options, on_done, on_highlight=on_highlight)

	# Displays a panel containing the current node's
	# children of the specified type.
	#	@param: child_type: one of func_type, class_type, 
	#						or other_type
	def _show_children_menu(self, child_type):
		self._panel_options = list()
		self._panel_options.append(go_up + global_name)

		children = self._node.get_children(child_type)

		# If node has no children, only display 'go up'
		if not children:
			self._show_panel(self._panel_options, 
							 self._on_children_done, 
							 self._on_highlight_done)
			return

		self._children_options = dict()	

		for child in children:
			self._panel_options.append(child.name)
			self._children_options[child.name] = child

		self._show_panel(self._panel_options, 
						 self._on_children_done, 
						 self._on_highlight_done)

	# Displays a panel containing the current node's
	# available children types. Types include func_type,
	# class_type, and other_type
	def _show_options_menu(self):
		self._panel_options = list()

		if not self._node.parent:
			self._panel_options.append(exit_program)
		else:
			self._panel_options.append(go_up + self._node.scope.name)

		children = self._node.get_children()

		if children:
			self._panel_options += self._node.get_children()

		# Functions and Classes can be read to the user
		if self._node.scope.type == func_type or \
			self._node.scope.type == class_type:
				self._panel_options.append(read + self._node.name)

		self._show_panel(self._panel_options, self._on_options_done, self._on_highlight_done)

	def _on_options_done(self, ind):
		# show_quick_panel() calls its callback with -1
		# if the user cancels the panel
		if(ind == -1):
			return

		selection = self._panel_options[ind]

		if selection == exit_program:
			return

		# if going back to the global scope
		if selection == (go_up + global_name):
			self._node = self._node.parent
			self._show_options_menu()
			return

		# When the user reads a scope, neither the current
		# node nor the displayed menu should change
		if (read + self._node.scope.name) in selection:
			say(str(self._node.scope))
			self._show_options_menu()
		else:
			self._show_children_menu(selection)

	def _on_children_done(self, ind):
		# show_quick_panel() calls its callback with -1
		# if the user cancels the panel
		if(ind == -1):
			return

		selection = self._panel_options[ind]

		if(selection == go_up + global_name):
			self._show_options_menu()

		child = self._children_options[selection]

		self._node = MenuNode(view=self.view, 
							  scope=child, 
							  parent=copy.deepcopy(self._node))

		self._show_options_menu()

	def _on_highlight_done(self, ind):
		#say menu options when option is highlighted
		say(self._panel_options[ind])


