import sublime
import sublime_plugin
from .scopes import Function, Class


def get_decl_start(view, symbol_start):
    """
    Returns the start point of the symbol's declaration
    in the view.

    Parameters:
        view - sublime view
        symbol_start - the start point of the symbol
                       within the view
    """
    start_decl = symbol_start

    is_whitespace = True
    while True:
        if start_decl == 0:
            print("Error: missing declaration")
            assert False

        start_decl -= 1

        if is_whitespace and not view.substr(start_decl).isspace():
            is_whitespace = False

        if not is_whitespace and view.substr(start_decl).isspace():
            start_decl += 1
            break

    return start_decl


def get_decl_end(view, symbol_end):
    end_decl = symbol_end

    # Find first open bracket or ';'
    while True:
        if end_decl == view.size() - 1:
            print("Error: missing open bracket or semicolon")
            assert False

        end_decl += 1

        # If a semicolon is found before an open bracket,
        # this symbol is associated with a forward
        # declaration.
        if view.substr(end_decl) == ';':
            return True, end_decl - 1

        if view.substr(end_decl) == '{':
            return False, end_decl - 1


def get_declaration(view, symbol_reg):
    decl_start = get_decl_start(view, symbol_reg.begin())

    is_fwd_decl, decl_end = get_decl_end(view, symbol_reg.end())

    return is_fwd_decl, sublime.Region(decl_start, decl_end)


def get_def_start(view, decl_end):
    def_start = decl_end

    while True:
        if def_start == view.size() - 1:
            print("Error: missing definition")
            assert False

        def_start += 1

        if view.substr(def_start) == '{':
            return def_start + 1


def get_def_end(view, def_start):
    def_end = def_start

    open_bracket_count = 1
    closed_bracket_count = 0

    # Search for the closing bracket associated with the
    # first open bracket
    while open_bracket_count != closed_bracket_count:
        if def_end == view.size() - 1:
            print("Error: missing closing bracket")
            assert False

        def_end += 1

        if view.substr(def_end) == '{':
            open_bracket_count += 1
        elif view.substr(def_end) == '}':
            closed_bracket_count += 1

    return def_end


def get_definition(view, declaration_reg):
    def_start = get_def_start(view, declaration_reg.end())

    def_end = get_def_end(view, def_start)

    return sublime.Region(def_start, def_end)


def get_scope(view, symbol_reg):
    is_fwd_decl, declaration_reg = get_declaration(view, symbol_reg)

    if is_fwd_decl:
        return None

    definition_reg = get_definition(view, declaration_reg)

    if view.substr(declaration_reg).split()[0] == 'class':
        scope = Class(view, definition_reg, declaration_reg)
    else:
        scope = Function(view, definition_reg, declaration_reg)

    return scope


# For testing
class TestCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for pair in self.view.symbols():
            scope = get_scope(self.view, pair[0])
            if scope:
                print(scope.declaration)
                print(scope.get_panel_options())