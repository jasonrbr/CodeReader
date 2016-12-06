import sublime
import sublime_plugin
from .scopes import Function, Class
from .audio import say


def get_decl_start(view, symbol_start):
    """
    Returns the start point of the symbol's declaration
    in the view.

    Parameters:
        view - sublime view
        symbol_start - the start point of the symbol
                       within the view
    """
    is_whitespace = True

    while True:
        symbol_start -= 1

        # If the start of the file has been reached and the last
        # character viewed wasn't whitespace, the declaration has
        # been found. Otherwise, there is no valid declaration.
        if symbol_start < 0:
            if not is_whitespace:
                symbol_start += 1
                break
            else:
                say("Error: missing declaration")
                assert False

        # Triggered when first whitespace character is found
        if is_whitespace and not view.substr(symbol_start).isspace():
            is_whitespace = False

        # Triggered when start of declaration has been found
        elif not is_whitespace and view.substr(symbol_start).isspace():
            symbol_start += 1
            break

    return symbol_start


def get_decl_end(view, symbol_end):
    """
    Returns the end point of the symbol's declaration
    in the view. A declaration ends at the first ';' or
    '{' after the symbol's end

    Parameters:
        view - sublime view
        symbol_end - the end point of the symbol
                     within the view
    """
    while True:
        if symbol_end == view.size() - 1:
            say("Error: missing open bracket or semicolon")
            assert False

        symbol_end += 1

        # If a semicolon is found before an open bracket,
        # this symbol is associated with a forward
        # declaration.
        if view.substr(symbol_end) == ';':
            return True, symbol_end - 1

        if view.substr(symbol_end) == '{':
            return False, symbol_end - 1


def get_declaration(view, symbol_reg):
    """
    Returns declaration associated with the symbol and
    whether it is a forward declaration.

    Parameters:
        view - sublime view
        symbol_reg - the symbol's region
    """
    decl_start = get_decl_start(view, symbol_reg.begin())

    is_fwd_decl, decl_end = get_decl_end(view, symbol_reg.end())

    return is_fwd_decl, sublime.Region(decl_start, decl_end)


def get_def_start(view, decl_end):
    """
    Returns the start of the definition associated with the
    declaration.

    Parameters:
        view - sublime view
        decl_end - the end region of the declaration
    """
    def_start = decl_end

    # Find point immediately after '{'
    while True:
        if def_start == view.size() - 1:
            say("Error: missing definition")
            assert False

        def_start += 1

        if view.substr(def_start) == '{':
            return def_start + 1


def get_def_end(view, def_start):
    """
    Returns the end of the definition.

    Parameters:
        view - sublime view
        def_start - the start of the definition
    """

    def_end = def_start

    open_bracket_count = 1
    closed_bracket_count = 0

    # Search for the closing bracket associated with the
    # first open bracket
    while open_bracket_count != closed_bracket_count:
        if def_end == view.size() - 1:
            say("Error: missing closing bracket")
            assert False

        def_end += 1

        if view.substr(def_end) == '{':
            open_bracket_count += 1
        elif view.substr(def_end) == '}':
            closed_bracket_count += 1

    return def_end


def get_definition(view, declaration_reg):
    """
    Returns the definition associated with the
    declaration.

    Parameters:
        view - sublime view
        declaration_reg - the declaration region
    """
    def_start = get_def_start(view, declaration_reg.end())

    def_end = get_def_end(view, def_start)

    return sublime.Region(def_start, def_end)


def get_scope(view, symbol_reg):
    """
    Returns the scope associated with the
    symbol.

    Parameters:
        view - sublime view
        symbol_reg - the symbol region
    """
    is_fwd_decl, declaration_reg = get_declaration(view, symbol_reg)

    # todo get this to recognize libraries as a scope(?)
    if is_fwd_decl:
        return None

    definition_reg = get_definition(view, declaration_reg)

    if view.substr(declaration_reg).split()[0] == 'class':
        scope = Class(view, definition_reg, declaration_reg)
    else:
        scope = Function(view, definition_reg, declaration_reg)

    return scope


def get_sub_scopes(view, region):
    """
    Returns the region associated with the
    symbol without converting it to a scope

    Parameters:
        view - sublime view
        symbol_reg - the symbol region
    """
    subscopes = list()

    for pair in view.symbols():
        symbol_reg = pair[0]

        # Do nothing if the symbol is not within the region
        if(symbol_reg.end() < region.begin() or
                symbol_reg.begin() > region.end()):
            continue

        # Do nothing if the symbol is within a subscope (nested)
        if(subscopes and
                (symbol_reg.begin() >
                    subscopes[-1].definition_region.begin() and
                    symbol_reg.end() < subscopes[-1].definition_region.end())):
            continue

        subscopes.append(get_scope(view, symbol_reg))

    return subscopes


class ParseCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        classAreg = sublime.Region(9, 88)
        subscopes = get_sub_scopes(self.view, classAreg)
        for scope in subscopes:
            print(scope.declaration)
