import sublime
import sublime_plugin
from .error import *
from .audio import say
from .menu import get_hierarchy_tree
from .parse import *
from .scopes import *

# Menu option menu strings:
go_up_prfx = 'go up to scope, '
read_prfx = 'read '  # Note: reed not read for proper pronunciation
scope_prfx = 'you are in scope '

# Child option menu strings:
title_str = 'scope {}s {}'
return_to_options_prfx = 'go back to options for '

# Read option menu strings:
quit_str = 'quit reading'

# Option menu Indices
title_ind = 0
read_ind = 1


def show_panel(options, on_done, on_hilight=None):
    """
    Displays a sublime panel.

    Parameters:
        options - list of strings to be displayed in the panel
        on_done - callback function called when user selects a
                    panel option
        on_hilight - callback function called when user changes
                    which panel option the cursor is hilighting
    """
    sublime.active_window().show_quick_panel(options,
                                             on_done,
                                             on_highlight=on_hilight)


class CodeReaderCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        try:
            # initialize configuration before the rest of run
            Config.init()
            self._curr_node = get_hierarchy_tree(self.view)
            self._show_options_menu()
        except MyError as e:
            alert_error(e)
            assert False

    def _show_children_menu(self, child_type):
        """
        Displays a panel containing the current node's
        children of the specified child_type
        """
        self._panel_options = list()
        self._panel_options.append(title_str.format(self._curr_node.name,
                                                    child_type))

        children_nodes = self._curr_node.get_children(child_type)
        assert children_nodes

        self._children_node_options = dict()

        # Make menu show scope's name and params
        for node in children_nodes:
            self._panel_options.append(node.scope.declaration)
            self._children_node_options[node.scope.declaration] = node

        self._panel_options.append(return_to_options_prfx +
                                   self._curr_node.scope.name)

        show_panel(self._panel_options,
                   self._on_children_done,
                   self._on_highlight_done)

    def _show_options_menu(self):
        """
        Displays options menu containing the current node's
        available child types
        """
        self._panel_options = list()
        self._panel_options.append(scope_prfx +
                                   self._curr_node.scope.name)

        # If current node is not the global namespace, append
        # read scope option
        if self._curr_node.parent:
            self._panel_options.append(read_prfx +
                                       self._curr_node.scope.name)

        scope_type_options = self._curr_node.get_children()

        if scope_type_options:
            self._panel_options.extend(scope_type_options)

        # Add go up hierarchy option if the current node is
        # not the global namespace
        if self._curr_node.parent:
            self._panel_options.append(go_up_prfx +
                                       self._curr_node.parent.scope.name)

        show_panel(self._panel_options,
                   self._on_options_done,
                   self._on_highlight_done)

    def _show_read_menu(self):
        self._panel_options = self._curr_node.scope.panel_options
        self._panel_options.append(quit_str)

        show_panel(self._panel_options,
                   self._on_read_done,
                   self._on_highlight_done)

    def _on_children_done(self, ind):
        """
        Callback function for children menu. Updates the current node
        to the selected child, or displays the options menu again.

        Parameters:
            ind - the panel index that the user selected
        """

        # Panel passes -1 in callback if user exits
        # out of the panel
        if(ind == -1):
            return

        # Display the current node's options menu
        if ind == self._get_go_up_ind():
            self._show_options_menu()
            return

        # Do not change panel state if user selects
        # the title
        if(ind == title_ind):
            self._show_children_menu(self._selected_child_type)
            return

        # The current node becomes the selected child node
        # (go one level down the tree)
        child_name = self._panel_options[ind]
        self._curr_node = self._children_node_options[child_name]
        self._show_options_menu()

    def _on_options_done(self, ind):
        """
        Callback function for options menu. Displays the children menu
        for the selected child type, or goes one level up the tree.

        Parameters:
            ind - the panel index that the user selected
        """

        # Panel passes -1 in callback if user exits
        # out of the panel
        if(ind == -1):
            return

        # Do not change panel state if user selects
        # the title
        if(ind == title_ind):
            self._show_options_menu()
            return

        # When the current node is not the global namespace node, then
        # selecting the read index opens the read scope panel
        if(ind == read_ind) and self._curr_node.parent:
            self._show_read_menu()
            return

        # When the current node is not the global namespace node, then
        # selecting go_up index changes the current node to its parent
        # (go up one level in the tree)
        if (ind == self._get_go_up_ind()) and self._curr_node.parent:
            self._curr_node = self._curr_node.parent
            self._show_options_menu()
            return

        self._selected_child_type = self._panel_options[ind]
        self._show_children_menu(self._selected_child_type)

    def _on_read_done(self, ind):
        # Panel passes -1 in callback if user exits
        # out of the panel
        if(ind == -1):
            return

        # Display the current node's options menu
        if ind == self._get_go_up_ind():
            self._show_options_menu()
            return

        show_panel(self._panel_options,
                   self._on_read_done,
                   self._on_highlight_done)

    """
    Utility Member Functions:
    """

    def _on_highlight_done(self, ind):
        """
        Say menu options when option is highlighted
        """
        say(self._panel_options[ind])

    def _get_go_up_ind(self):
        return len(self._panel_options) - 1
