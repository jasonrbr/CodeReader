import sublime_plugin
import sublime

# Scope types
func_scope_type = 'functions'
class_scope_type = 'classes'
other_scope_type = 'other'


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

        # Convert region to string
        # Split on whitespace to get after return type
        # Then go up to opening parenthesis to get function name
        func_name = view.substr(declaration).split()[1].split('(')[0]
        super().__init__(view,
                         func_name,
                         func_scope_type)
        self._body = body
        self._declaration = declaration

    def get_panel_options(self):
        panel_options = []
        panel_options.append(self.declaration + ' and ' + self.params)

        definition = self._view.split_by_newlines(
            sublime.Region(self._body.begin(), self._body.end()))

        for line in definition:
            line_str = self._view.substr(line)

            if line_str and not line_str.isspace():
                panel_options.append(line_str.strip())

        return panel_options

    def __eq__(self, other):
        return (self.declaration == other.declaration and
                self.params == other.params)

    @property
    def declaration(self):
        return_type = self._view.substr(self._declaration).split()[0]
        return "function {} returns {}".format(self._name, return_type)

    @property
    def declaration_region(self):
        return self._declaration

    @property
    def definition_region(self):
        return self._body

    @property
    def params(self):
        params = self._view.substr(
            self._declaration).split('(')[1].split(')')[0].split(',')
        params = [s.strip() for s in params]  # trim whitespace

        # If takes no params
        if params[0] == '':
            return ''
        return " takes {}".format(', '.join(params))


class Class(Scope):
    def __init__(self, view, body, declaration):
        class_name = view.substr(declaration).split()[1]
        super().__init__(view,
                         class_name,
                         class_scope_type)
        self._body = body
        self._declaration = declaration

    @property
    def declaration(self):
        return 'class {}'.format(self._name)

    def get_panel_options(self):
        panel_options = []
        panel_options.append(self.declaration)

        definition = self._view.split_by_newlines(
            sublime.Region(self._body.begin(), self._body.end()))

        # TODO: Don't read body of member function (make sub menu?)
        for line in definition:
            line_str = self._view.substr(line)

            if line_str and not line_str.isspace():
                panel_options.append(line_str.strip())

        return panel_options

    def __eq__(self, other):
        return self.declaration == other.declaration

    @property
    def declaration_region(self):
        return self._declaration

    @property
    def definition_region(self):
        return self._body


# Test
class ScopeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        func = Function(self.view, sublime.Region(31, 53),
                        sublime.Region(0, 28))
        classA = Class(self.view, sublime.Region(71, 105),
                       sublime.Region(56, 68))

        print(func.get_panel_options())
        print(classA.get_panel_options())
