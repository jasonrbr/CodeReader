import sublime
import re
from .config import *
from .parse import get_sub_scopes
from .parse_symbols import parse_symbols
from .scope_reader import *
from .error import *

global_scope_name = 'global namespace'
func_scope_type = 'functions'
class_scope_type = 'classes'
library_scope_type = 'library'

scope_types = {func_scope_type, class_scope_type, library_scope_type}


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
    regex_pattern = '#include (<\w+>|\"\w+.h\")'

    def __init__(self, view, declaration_reg):
        """
        Parameters:
            name - name of the library being included
            declaration - Region containing the declaration
                          (ie., "#include <...>")
        """
        self._declaration_reg = declaration_reg
        self._name = self._get_name(self._declaration_reg, view)

        super().__init__(view,
                         self._name,
                         library_scope_type)

    # TODO: do we need to parse out '#'?
    @property
    def declaration(self):
        return "library {}".format(self._name)

    def _get_name(self, rgn, view):
        lib_pattern = self.regex_pattern
        txt = view.substr(rgn)
        m = re.match(lib_pattern, txt)
        library_name = m.group(1)
        library_name = re.sub('[\<\>\"]', '', library_name)
        return library_name


class ReadableScopes(Scope):
    def __init__(self, view, name, scope_type,
                 declaration_reg, definition_reg,
                 reading_state):
        self._declaration_reg = declaration_reg
        self._definition_reg = definition_reg
        self._reading_state = reading_state
        super().__init__(view, name, scope_type)

    def __eq__(self, other):
        return self._declaration_reg == other._declaration_reg

    @property
    def declaration_region(self):
        return self._declaration_reg

    @property
    def definition_region(self):
        return self._definition_reg

    def _get_panel_options(self):
        decl_str = self.declaration

        if self._reading_state.read_line_numbers:
            row, col = self._view.rowcol(self._declaration_reg.begin())
            decl_str = 'line ' + str(row + 1) + ', ' + decl_str

        panel_options = [decl_str]
        panel_options.extend(read_region(self._view,
                                         self._reading_state,
                                         self.definition_region))
        return panel_options


class Function(ReadableScopes):
    def __init__(self, view, declaration_reg, definition_reg):
        func_name = self._get_func_name(view, declaration_reg)
        super().__init__(view, func_name, func_scope_type,
                         declaration_reg, definition_reg,
                         FunctionReadingState())

    def __eq__(self, other):
        return super().__eq__(other) and self.params == other.params

    @property
    def panel_options(self):
        return self._get_panel_options()

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


class Class(ReadableScopes):
    def __init__(self, view, declaration_reg, definition_reg):
        class_name = view.substr(declaration_reg).split()[1]
        super().__init__(view, parse_symbols(class_name), class_scope_type,
                         declaration_reg, definition_reg,
                         self._get_reading_state(view, definition_reg))

    def __eq__(self, other):
        return super().__eq__(other)

    @property
    def panel_options(self):
        return self._get_panel_options()

    @property
    def declaration(self):
        return 'class {}'.format(self._name)

    def _get_reading_state(self, view, definition_region):
        regions_to_ignore = self._get_regions_to_ignore(view,
                                                        definition_region)
        return ClassReadingState(regions_to_ignore)

    def _get_regions_to_ignore(self, view, definition_region):
        scopes_to_ignore = get_sub_scopes(view, definition_region)
        regions_to_ignore = list()
        for scope in scopes_to_ignore:
            regions_to_ignore.append(scope.definition_region)

        return regions_to_ignore
