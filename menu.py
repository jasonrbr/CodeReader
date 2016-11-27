import sublime
import sublime_plugin
from collections import deque
from .scopes import *
from .parse import *

global_namespace = 'global namespace'


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
        self._children = {
            class_scope_type: list(),
            func_scope_type: list()}

    def add_child(self, node):
        """
        Appends node to the children list corresponding to
        the node's type.

        Parameters:
            node - MenuNode whose scope region is within the region
                   of this menu node's scope region
        """
        assert (node._scope.type == func_scope_type or
                node._scope.type == class_scope_type)
        self._children[node._scope.type].append(node)

    def get_children(self, child_type=None):
        """
        Returns list of children nodes of the specified scope type.
        If scope type not given, returns list of available scope types;
        these are the children scope types that map to a non-empty list

        Parameters:
            child_type - indicates which node list to return.
                         If None, returns available scope types.
        """
        if (child_type and child_type in self._children and
                len(self._children[child_type])):
            return self._children[child_type]

        if not child_type:
            children = list()
            for key, value in self._children.items():
                if len(value):
                    children.append(key)
            if len(children):
                return children

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


def generate_global_node(view):
    global_scope = Scope(view=view,
                         name=global_namespace)
    global_node = MenuNode(view=view,
                           scope=global_scope)
    return global_node


class MenuTree():
    def __init__(self, view):
        self._view = view
        self._root = generate_global_node(self._view)

    def push(self, new_scope):
        stack = list()
        queue = deque()

        queue.append(self._root)

        while queue:
            node = queue.popleft()

            # Functions can't have children
            if node._scope.type == func_scope_type:
                continue

            stack.append(node)

            class_children = node.get_children(class_scope_type)

            if not class_children:
                continue

            for node in class_children:
                queue.append(node)

        insert_node = None
        while stack:
            node = stack.pop()

            if node is self._root:
                insert_node = node
                break

            assert node.scope.type == class_scope_type

            node_reg = node.scope.definition_region
            new_scope_reg = new_scope.declaration_region

            if (new_scope_reg.begin() >= node_reg.begin() and
                    node_reg.end() >= new_scope_reg.end()):

                insert_node = node
                break

        assert insert_node

        child_node = MenuNode(view=self._view,
                              scope=new_scope,
                              parent=insert_node)

        insert_node.add_child(child_node)

    def _make_string(self, prefix, node):
        str_ = "{}{}\n".format(prefix, node.scope.name)

        children = list()

        funcs = node.get_children(func_scope_type)
        if funcs:
            children.extend(funcs)
        classes = node.get_children(class_scope_type)
        if classes:
            children.extend(classes)

        if children:
            prefix += '\t'
            for node in children:
                str_ += self._make_string(prefix, node)

        return str_

    def __str__(self):
        prefix = ""
        return self._make_string(prefix, self._root)

    @property
    def root(self):
        return self._root


# Test
class MenuCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        scopes = list()
        # Convert all symbols in the view to
        # scopes
        for pair in self.view.symbols():
            scope = get_scope(self.view, pair[0])
            # TODO: handle fwd declarations
            if scope:
                scopes.append(scope)

        tree = MenuTree(self.view)
        for scope in scopes:
            tree.push(scope)

        print(str(tree))
