import sublime
import sublime_plugin
from collections import deque
from .scopes import *
from .parse import get_sub_scopes


class MenuNode():
    """
    Attributes:
        view - sublime view into text buffer
        scope - scope object associated with this node
        parent - the parent of this node in the hierarchy tree.
                 this node is root if parent is None
        children - dictionary of scope type strings to a
                   list of menu nodes. These nodes are the
                   children of this node in the hierarchy tree
    """

    def __init__(self, view, scope, parent=None):
        self._view = view
        self._scope = scope

        self._parent = parent
        # Dictonary of scope types to a list of nodes of that type
        self._children = {scope_type: list() for scope_type in scope_types}

        # TODO: do something with the _children.library_scope_type

    def add_child(self, node):
        """
        Appends node to the children list corresponding to
        the node's type.

        Parameters:
            node - MenuNode whose scope region is within the region
                   of this menu node's scope region
        """
        assert is_valid_type(node.scope.type)
        self._children[node.scope.type].append(node)

    def get_children(self, child_type=None):
        """
        Returns list of children nodes of the specified scope type.
        If scope type not given, returns list of available scope types;
        these are the children scope types that map to a non-empty list

        Parameters:
            child_type - indicates which node list to return.
                         If None, returns available scope types.
        """

        # Checks whether the child_type is valid and if any children
        # of this type exists
        if (child_type and (child_type in self._children) and
                len(self._children[child_type])):
            return self._children[child_type]

        # Returns a list of all available children types.
        # Does nothing if scope contains no children types.
        if not child_type:
            children_types = list()
            for key, value in self._children.items():
                if len(value):
                    children_types.append(key)
            if len(children_types):
                return children_types

        return None

    @property
    def name(self):
        return self._scope._name

    @property
    def parent(self):
        return self._parent

    @property
    def scope(self):
        return self._scope

    @property
    def is_global_node(self):
        return self._parent is None


def get_libraries(view, parent):
# TODO ignore #include's that are under subscopes
# Look for libraries in view to make into scopes
    result = []

    lib_rgns = view.find_all(Library.regex_pattern)
    for rgn in lib_rgns:
        result.append(Library(view, rgn))
    return result


def get_hierarchy_tree(view, node=None):
    if not node:
        node = MenuNode(view=view,
                        scope=GlobalScope(view))

    # Base case: node is of scope type that cannot
    # have children
    if not node.scope.can_have_subscopes:
        return node

    subscopes = get_sub_scopes(view, node.scope.definition_region)

    # Base case: node has no children
    if not subscopes:
        return node

    # Add children nodes
    for subscope in subscopes:
        child_node = get_hierarchy_tree(view, MenuNode(view,
                                                       subscope,
                                                       parent=node))
        node.add_child(child_node)

    # get libraries
    # if global scope:
    if not node.parent:
        libs = get_libraries(view, node)
        for lib in libs:
            node.add_child(MenuNode(view, lib, node))

    return node


# Test
class MenuCommand(sublime_plugin.TextCommand):
    # Preorder traversal
    def print_hierarchy(self, node, prefix=""):
        print(prefix + node.name)

        # Base case: node is of scope type that cannot
        # have children
        if not node.scope.can_have_subscopes:
            return

        # Base case: node has no children
        available_scope_types = node.get_children()
        if not available_scope_types:
            return

        for scope_type in available_scope_types:
            children = node.get_children(scope_type)
            for child_node in children:
                self.print_hierarchy(node=child_node, prefix=(prefix + "\t"))

    def run(self, edit):
        root = get_hierarchy_tree(self.view)
        self.print_hierarchy(node=root)
        # print(root.scope.definition_region)
        # print(root.scope.name)

        # print(root.get_children())
