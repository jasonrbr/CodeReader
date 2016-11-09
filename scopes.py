import sublime_plugin
import sublime

# Scope types
func_scope_type = 'functions'
class_scope_type = 'classes'
other_scope_type = 'other'


class Scope():
    def __init__(self, view, body, name, scope_type=None):
        self._view = view
        self._scope_type = scope_type
        self._body = body
        self._name = name

    @property
    def type(self):
        return self._scope_type

    @property
    def body(self):
        return self._body

    @property
    def name(self):
        return self._name


class Function(Scope):
    def __init__(self, view, body, declaration):
        super().__init__(view, body,
                         declaration.split()[1].split('(')[0],
                         func_scope_type)

        self._returns = declaration.split()[0]
        self._params = declaration.split('(')[1].split(')')[0].split(',')
        self._params = [s.strip() for s in self._params]  # trim whitespace

    @property
    def declaration(self):
        return "function {} returns {}".format(self._name, self._returns)

    @property
    def params(self):
        return "takes {}".format(', '.join(self._params))

    def __str__(self):
        func_str = self.declaration + '\n'

        definition = self._view.split_by_newlines(
            sublime.Region(self._body.begin(), self._body.end()))

        # Iterate all lines of code in the function
        for line in definition:
            line_str = self._view.substr(line)

            if line_str.isspace() or not line_str:
                func_str += 'empty line\n'
            else:
                func_str += line_str.lstrip() + '\n'

        return func_str

    def __eq__(self, other):
        return (self.declaration == other.declaration and
                self._params == other._params)


class Class(Scope):
    def __init__(self, view, body, declaration):
        super().__init__(view, body,
                         declaration.split()[1], class_scope_type)

    @property
    def declaration(self):
        return 'class {}'.format(self._name)

    def __str__(self):
        class_str = self.declaration + '\n'

        definition = self._view.split_by_newlines(
            sublime.Region(self._body.begin(), self._body.end()))

        # Iterate all lines of code in the function
        for line in definition:
            line_str = self._view.substr(line)

            if line_str.isspace() or not line_str:
                class_str += 'empty line\n'
            else:
                class_str += line_str.lstrip() + '\n'

        return class_str

    def __eq__(self, other):
        return self.declaration == other.declaration


# Test
class ScopeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        func = Function(self.view, sublime.Region(31, 54),
                        "int foo(int x, int y, int z) {")
        func2 = Function(self.view, sublime.Region(31, 54),
                         "int foo(int x, int y, int z) {")
        func3 = Function(self.view, sublime.Region(80, 95),
                         "int foo(int x, int y) {")
        print(str(func3))
        print(func3.params)
        if func == func2:
            print('equal')
        if func != func3:
            print('yay')
        if func != func2:
            print('boo')
        if func == func3:
            print('boo you whore')
