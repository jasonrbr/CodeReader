import sublime
import sublime_plugin
from .scopes import *
from .parse import *

class MenuNode():
    def __init__(self, view, scope, parent=None):
        self._view = view
        self._scope = scope

        self._parent = parent
        self._children = {
            other_type: list(),
            class_type: list(),
            func_type: list()}

        if self._scope.type != func_type:
            self._generate_children()

    # @param: child_type: when child_type == None, returns a list
    #                     of available child_types. If the node doesn't
    #                     have a certain child_type, it's not included
    #                     in the list. Child types include func_type
    #                     class_type, and other_type
    #
    #                     when child_type != None, returns a list of
    #                     all children with that available type. If none
    #                     exist, returns None
    def get_children(self, child_type=None):
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

def generate_menu(view):
    scopes = list()
    for pair in view.symbols():
        scope = get_scope(view, pair[0])
        if scope:
            scopes.append(get_scope(view, pair[0]))
    for scope in scopes:
        print(scope.declaration)  

# Test
class MenuCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        generate_menu(self.view)
