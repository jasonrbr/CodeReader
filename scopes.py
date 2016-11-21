import sublime_plugin
import sublime
import re
from .config import *

# Scope types
func_scope_type = 'functions'
other_scope_type = 'other'
class_scope_type = 'classes'


# raw symbols and their translations when passing to say
# must be in decreasing order to enforce
symbol_list = {r'cout': 'see out', r'endl': 'endline',
               r'!=': ' is not equal to ', r'==': ' is equal to ',
               r'-=': ' minus equals ', r'->': ' arrow ',
               r'*=': ' times equals ', r'/=': ' divide equals ',
               r'<<': ',', r'>>': ',', r';': ',',
               r'<=': ' less than or equal to ',
               r'//': 'comment: ', r'/*': 'comment:', r'*/': 'end comment:',
               r'>=': ' greater than or equal to ',
               r'*': ' star ', r'&': ' ampersand ', r'(': ' ', r')': ' ',
               r'|': ' bar ', r'<': ' less than ', r'>': ' greater than '}

# Need to sort by descending length
symbols = sorted(symbol_list.keys(), key=len, reverse=True)


# Returns a stripped string with symbols mapped to their
# appropriate English words
def parse_symbols(input_str):
    pattern = re.compile('|'.join(re.escape(key) for key in symbols))
    parsed = pattern.sub(lambda x: symbol_list[x.group()], input_str)
    return parsed.strip()


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


class Function(Scope):
    def __init__(self, view, body, declaration):
        """
        Parameters:
            body - Region containing body/definition excluding open and
                    closing brackets
            declaration - Region containing the declaration excluding opening
                            bracket. If forward declared, this the forward
                            declared region
        """
        self._body = body
        self._declaration = declaration

        func_name = self._get_func_name(view)
        super().__init__(view,
                         func_name,
                         func_scope_type)

        self._panel_options = self._get_panel_options()

    def __eq__(self, other):
        return (self.declaration == other.declaration and
                self.params == other.params)

    @property
    def declaration(self):
        return_type = self._view.substr(self._declaration).split()[0]
        # Map to English and trim
        parsed_return_type = parse_symbols(return_type)
        return "function {} returns {}".format(self._name, parsed_return_type)

    @property
    def declaration_region(self):
        return self._declaration

    @property
    def definition_region(self):
        return self._body

    @property
    def panel_options(self):
        return self._panel_options

    @property
    def params(self):
        params = self._view.substr(
            self._declaration).split('(')[1].split(')')[0].split(',')
        params = [parse_symbols(s) for s in params]  # map to English

        # If takes no params
        if params[0] == '':
            return ''
        return " takes {}".format(', '.join(params))

    def _get_func_name(self, view):
        func_name = view.substr(self._declaration)

        # Grab word immediately after return type
        func_name = func_name.split()[1]
        # Grab word immediately before first parenthensis
        func_name = func_name.split('(')[0]
        # Grab word at end of scope operator chain
        scope_ops_arr = func_name.split('::')

        func_name = scope_ops_arr.pop().strip()

        return func_name

    def _get_panel_options(self):
        panel_options = []

        # init the config file for reading
        Config.init()
        read_line_numbers = Config.get('read_line_numbers')

        decl_str = self.declaration

        # The declaration is the first panel option
        if self.params:
            decl_str += ' and' + self.params

        if read_line_numbers:
            row, col = self._view.rowcol(self._declaration.a)
            decl_str = 'line ' + str(row + 1) + ', ' + decl_str

        panel_options.append(decl_str)

        definition = self._view.split_by_newlines(
            sublime.Region(self._body.begin(), self._body.end()))

        subscope_stack = list()

        single_line_comment = False
        multi_line_comment_found_begin = False
        multi_line_comment_found_end = False

        for line in definition:
            line_str = self._view.substr(line)
            if "}" in line_str:
                subscope_type = subscope_stack.pop()
                panel_options.append("exiting " + subscope_type)
                continue

            if "for" in line_str:
                subscope_stack.append("for loop")
            elif "while" in line_str:
                subscope_stack.append("while loop")
            elif "if" in line_str and "else" not in line_str:
                subscope_stack.append("if statement")
            elif "if" in line_str and "else" in line_str:
                subscope_stack.append("else if statement")
            elif "if" not in line_str and "else" in line_str:
                subscope_stack.append("else statement")

            if line_str and not line_str.isspace():

                # Is reading_comments off?
                if not Config.get('read_comments'):

                    # If it's a single line comment
                    if '//' in line_str:
                        single_line_comment = True
                        continue

                    # Find start of multi line comment
                    if '/*' in line_str:
                        multi_line_comment_found_begin = True
                        multi_line_comment_found_end = False
                        continue

                    # If there is more of the multi line comment to be found
                    if (multi_line_comment_found_begin and
                            not multi_line_comment_found_end):
                        continue

                    # Found the end of the multi line comment!
                    if '*/' in line_str:
                        multi_line_comment_found_end = True
                        multi_line_comment_found_begin = False
                        continue

                # Need to read comments
                else:
                    # If it's a single line comment
                    if '//' in line_str:
                        single_line_comment = True

                parsed_string = parse_symbols(line_str)

                if read_line_numbers:
                    row, col = self._view.rowcol(line.a)
                    parsed_string = 'line ' + str(row + 1) + ', ' + parsed_string

                panel_options.append(parsed_string)

                # Check for single line comment
                if single_line_comment and Config.get('read_comments'):
                    panel_options.append('end comment')
                    single_line_comment = False

        return panel_options



class Class(Scope):
    def __init__(self, view, body, declaration):
        class_name = view.substr(declaration).split()[1]
        super().__init__(view,
                         class_name,
                         class_scope_type)
        self._body = body
        self._declaration = declaration

    def __eq__(self, other):
        return self.declaration == other.declaration

    @property
    def declaration(self):
        return 'class {}'.format(self._name)

    @property
    def declaration_region(self):
        return self._declaration

    @property
    def definition_region(self):
        return self._body

    @property
    def panel_options(self):
        return self._get_panel_options()

    def _get_panel_options(self):
        panel_options = []
        panel_options.append(self.declaration)

        definition = self._view.split_by_newlines(
            sublime.Region(self._body.begin(), self._body.end()))

        # TODO: Don't read body of member function (make sub menu?)
        for line in definition:
            line_str = self._view.substr(line)

            # TODO: toggle comments on or off like for functions
            # TODO: add 'exiting scope /blah/' logic like above for functions
            # TODO: toggle line numbers being on or off like for functions

            if line_str and not line_str.isspace():
                parsed_string = parse_symbols(line_str)
                panel_options.append(parsed_string)

        return panel_options



# Test
class ScopeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        func = Function(self.view, sublime.Region(14, 67),
                        sublime.Region(1, 12))

        print(self.view.substr(func._declaration))
        print(self.view.substr(func._body))
        print(func.panel_options)
