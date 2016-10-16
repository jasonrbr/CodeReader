import sublime
import sublime_plugin
import copy
from .menu import MenuNode	
from .scopes import *

global_namespace = 'global namespace'
# TODO: do we even need an exit item?
exit_program = 'exit'
# Rename (goes up one level in the tree)
go_up = 'go up'

# TODO: only works for single file
# TODO: permanently store global scope?
class CodeReaderCommand(sublime_plugin.TextCommand):
	def run(self, edit):		
		file_start = 0
		file_end = self.view.size()
		src_code = sublime.Region(file_start, file_end)
			
		global_scope = Scope(view=self.view, body=src_code, name=global_namespace)
		self._node = MenuNode(view=self.view, scope=global_scope)

		self._show_options_menu()

	# TODO: Prob should refactor this X(
	def _show_children_menu(self, child):
		self._options = tuple()
		self._options += (go_up,)

		panel_options = list()
		panel_options.append(go_up)

		children = self._node.get_children(child)

		# TODO: add read option if class or func
		if not children:
			# TODO: perhaps print on hilight
			sublime.active_window().show_quick_panel(
				self._options, self._on_children_done)
			return

		panel_options = list()
		panel_options.append(go_up)

		for child in children:
			panel_options.append(child.name)
			self._options += (child,)

		assert(len(panel_options) == len(self._options))

		# TODO: perhaps print on hilight
		sublime.active_window().show_quick_panel(
			panel_options, self._on_children_done)

	def _show_options_menu(self):
		self._options = list()

		if not self._node.parent:
			self._options.append(exit_program)
		else:
			self._options.append(go_up)

		children = self._node.get_children()
		# TODO: what if function or P.O.D class
		if children:
			self._options += self._node.get_children()

		# TODO: perhaps print on hilight
		sublime.active_window().show_quick_panel(
			self._options, self._on_options_done)

	def _on_options_done(self, ind):
		if(ind == -1):
			return

		selection = self._options[ind]

		if selection == exit_program:
			return

		if selection == go_up:
			self._node = self._node.parent
			self._show_options_menu()
			return
		
		self._show_children_menu(selection)

	def _on_children_done(self, ind):
		if(ind == -1):
			return

		selection = self._options[ind]

		if(selection == go_up):
			self._show_options_menu()

		# Set current node to the selected child
		self._node = MenuNode(view=self.view, 
							  scope=selection, 
							  parent=copy.deepcopy(self._node))

		self._show_options_menu()
