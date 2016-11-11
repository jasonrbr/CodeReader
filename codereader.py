import sublime
import sublime_plugin
import copy
from .menu import MenuNode
from .scopes import *
from .audio import say

# Name of global Scope
global_namespace = 'global namespace'

# Menu option Strings:
go_up = 'go up to scope, '  # Concat with scope you're currently in
read = 'read '  # Concat with scope name
global_name = 'global'


class CodeReaderCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        file_start = 0
        file_end = self.view.size()
        src_code = sublime.Region(file_start, file_end)

        # Set root to Global Namespace node
        global_scope = Scope(
            view=self.view, body=src_code, name=global_namespace)
        self._node = MenuNode(view=self.view, scope=global_scope)

        self._show_options_menu()

    # Displays a sublime panel
    #   @param: options: list of strings for selection
    #   @param: on_done: callback function
    #   @param: on_highlighted: callback function
    def _show_panel(self, options, on_done, on_highlight):
        sublime.active_window().show_quick_panel(options,
                                                 on_done,
                                                 on_highlight=on_highlight)

    # Displays a panel containing the current node's
    # children of the specified type.
    #   @param: child_type: one of func_type, class_type,
    #                       or other_type
    def _show_children_menu(self, child_type):
        self._panel_options = list()
        self._panel_options.append("Scope {}s {}".format(self._node.name,
                                                         child_type))

        children = self._node.get_children(child_type)

        # If node has no children, only display "return to options menu"
        # option. TODO: this shouldn't happen possibly assert false here
        if not children:
            self._show_panel(self._panel_options,
                             self._on_children_done,
                             self._on_highlight_done)
            return

        self._children_options = dict()

        for child in children:
            self._panel_options.append(child.name)
            self._children_options[child.name] = child

        self._panel_options.append(
            "See all children options for {}".format(self._node.name))

        self._show_panel(self._panel_options,
                         self._on_children_done,
                         self._on_highlight_done)

    # Displays a panel containing the current node's
    # available children types. Types include func_type,
    # class_type, and other_type
    def _show_options_menu(self):
        self._panel_options = list()
        self._panel_options.append("Scope {}".format(self._node.name))

        children = self._node.get_children()

        if children:
            self._panel_options += self._node.get_children()

        # Add read_scope option if the current scope is a
        # function or a class
        if (self._node.scope.type == func_type or
                self._node.scope.type == class_type):
            self._panel_options.append(read + self._node.name)

        # Add go_up hierarchy option if the current scope
        # is not the global scope
        if self._node.parent:
            self._panel_options.append(go_up + self._node.parent.name)

        self._show_panel(self._panel_options,
                         self._on_options_done, self._on_highlight_done)

    def _on_options_done(self, ind):
        # show_quick_panel() calls its callback with -1
        # if the user cancels the panel
        if(ind == -1):
            return

        # The first item in the panel is the panel title
        if(ind == 0):
            self._show_options_menu()
            return

        # if going back to the global scope
        end_ind = len(self._panel_options) - 1
        if self._node.parent and ind == end_ind:
            self._node = self._node.parent
            self._show_options_menu()
            return

        selection = self._panel_options[ind]

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

        # The first item in the panel is the panel title
        if(ind == 0):
            self._show_options_menu()

        end_ind = len(self._panel_options) - 1
        if(ind == end_ind):
            self._show_options_menu()

        selection = self._panel_options[ind]

        child = self._children_options[selection]

        self._node = MenuNode(view=self.view,
                              scope=child,
                              parent=copy.deepcopy(self._node))

        self._show_options_menu()

    def _on_highlight_done(self, ind):
        # say menu options when option is highlighted
        say(self._panel_options[ind])
