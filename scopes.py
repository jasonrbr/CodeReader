import sublime
import re
from .config import *
from .parse_symbols import parse_symbols
from .scope_reader import Reader

global_scope_name = 'global namespace'
func_scope_type = 'functions'
class_scope_type = 'classes'
library_scope_type = 'library'

scope_types = {func_scope_type, class_scope_type, library_scope_type}

# Used to grab a scope's panel options
scope_reader = Reader()


def is_valid_type(scope_type):
    return scope_type in scope_types


class Scope():
    def __init__(self, view, name, scope_type=None):
        self._view = view
        self._scope_type = scope_type
        self._name = name

    @property
    def type(self):
        return self._scope_type

    @property
    def name(self):
        return self._name

    @property
    def can_have_subscopes(self):
        return self._scope_type == class_scope_type


# TODO: make this derive from ScopesWithDefinitions, and have its
# declaration match its definition???
class GlobalScope(Scope):
    def __init__(self, view):
        super().__init__(view, global_scope_name)
        self._body_reg = sublime.Region(0, self._view.size())

    # Called "definition region" for sorta-polymorphism
    @property
    def definition_region(self):
        return self._body_reg

    @property
    def can_have_subscopes(self):
        return True


# TODO: do we even need this?
class Library(Scope):
    def __init__(self, view, declaration_reg):
        """
        Parameters:
            name - name of the library being included
            declaration - Region containing the declaration
                          (ie., "#include <...>")
        """
        self._declaration_reg = declaration_reg

        super().__init__(view,
                         self._name,
                         library_scope_type)

    # TODO: do we need to parse out '#'?
    @property
    def declaration(self):
        return self._view.substr(self._declaration_reg)

    # TODO: make work for project libs (e.g. #include "lib.h")
    @property
    def regex_pattern():
        return '\#include \<(\w+)\>'

    def _get_name(self):
        lib_pattern = self.regex_pattern
        txt = self.view.substr(self._declaration_reg)
        m = re.match(lib_pattern, txt)
        return m.group(1)


class ScopesWithDefinitions(Scope):
    def __init__(self, view, name, scope_type,
                 declaration_reg, definition_reg):
        self._declaration_reg = declaration_reg
        self._definition_reg = definition_reg

        super().__init__(view, name, scope_type)

    def __eq__(self, other):
        return self._declaration_reg == other._declaration_reg

    @property
    def declaration_region(self):
        return self._declaration_reg

    @property
    def definition_region(self):
        return self._definition_reg


class Function(ScopesWithDefinitions):
    def __init__(self, view, declaration_reg, definition_reg):
        func_name = self._get_func_name(view, declaration_reg)
        super().__init__(view, func_name, func_scope_type,
                         declaration_reg, definition_reg)

    def __eq__(self, other):
        return super().__eq__(other) and self.params == other.params

    @property
    def declaration(self):
        return_type = self._view.substr(self._declaration_reg).split()[0]
        # Map to English and trim
        parsed_return_type = parse_symbols(return_type)

        decl_str = "function {} returns {}".format(self._name,
                                                   parsed_return_type)

        params = self.params

        if not params:
            return decl_str

        return decl_str + " and takes {}".format(params)

    @property
    def panel_options(self):
        return self._get_panel_options()

    @property
    def params(self):
        params = self._view.substr(
            self._declaration_reg).split('(')[1].split(')')[0].split(',')
        params = [parse_symbols(s) for s in params]  # map to English

        # If takes no params
        if params[0] == '':
            return None
        return "{}".format(', '.join(params))

    def _get_func_name(self, view, declaration_reg):
        func_name = view.substr(declaration_reg)

        # Grab word immediately after return type
        func_name = func_name.split()[1]
        # Grab word immediately before first parenthensis
        func_name = func_name.split('(')[0]
        # Grab word at end of scope operator chain
        scope_ops_arr = func_name.split('::')

        func_name = scope_ops_arr.pop().strip()

        return func_name

    def _get_panel_options(self):
        Config.init()
        read_line_numbers = Config.get('read_line_numbers')

        decl_str = self.declaration

        if read_line_numbers:
            row, col = self._view.rowcol(self._declaration_reg.begin())
            decl_str = 'line ' + str(row + 1) + ', ' + decl_str

        panel_options = [decl_str]
        panel_options.extend(scope_reader.read(self._view,
                                               self._definition_reg))
        return panel_options


class Class(ScopesWithDefinitions):
    def __init__(self, view, declaration_reg, definition_reg):
        class_name = view.substr(declaration_reg).split()[1]
        super().__init__(view, parse_symbols(class_name), class_scope_type,
                         declaration_reg, definition_reg)

    def __eq__(self, other):
        return super().__eq__(other)

    @property
    def declaration(self):
        return 'class {}'.format(self._name)

    @property
    def panel_options(self):
        return self._get_panel_options()

    def _get_panel_options(self):
        panel_options = []

        decl_str = self.declaration
        # init the config file for reading
        Config.init()
        read_line_numbers = Config.get('read_line_numbers')

        if read_line_numbers:
            row, col = self._view.rowcol(self._declaration_reg.a)
            decl_str = 'line ' + str(row + 1) + ', ' + decl_str

        panel_options.append(decl_str)

        definition = self._view.split_by_newlines(
            sublime.Region(self._definition_reg.begin(),
                           self._definition_reg.end()))

        # TODO: Don't read body of member function (make sub menu?)
        returned_panel_options = read_definition(self, definition=definition,
                                                 panel_options=panel_options,
                                                 read_line_numbers=read_line_numbers)

        return returned_panel_options
