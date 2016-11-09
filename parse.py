import sublime
import sublime_plugin

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

def get_scope_end(view, symbol_end):
    """
    Returns the end point of the symbol's definition
    in the view.

    Parameters:
        view - sublime view
        symbol_end - the end point of the symbol
                     withing the view
    """
    end_point = symbol_end

    # Find first open bracket or ';'
    while True:
        if end_point == view.size() - 1:
            print("Error: missing open bracket or semicolon")
            assert False

        end_point += 1

        # If a semicolon is found before an open bracket,
        # this symbol is associated with a forward
        # declaration.
        if view.substr(end_point) == ';':
            return True, end_point

        if view.substr(end_point) == '{':
            break

    open_bracket_count = 1
    closed_bracket_count = 0

    # Search for the closing bracket associated with the
    # first open bracket
    while open_bracket_count != closed_bracket_count:
        if end_point == view.size() - 1:
            print("Error: missing closing bracket")
            assert False

        end_point += 1

        if view.substr(end_point) == '{':
            open_bracket_count += 1
        elif view.substr(end_point) == '}':
            closed_bracket_count += 1

    return False, end_point

def get_scope_region(view, symbol_reg):
    """
    Returns the region of the scope associated 
    with the symbol
    
    Parameters:
        view - sublime view
        symbol_reg - sublime.Region of a symbol in view
    """
    symbol_start = symbol_reg.begin()
    declaration_start = get_decl_start(view, symbol_start)

    symbol_end = symbol_reg.end() - 1
    is_fwd_decl, end_point = get_scope_end(view, symbol_end)

    return sublime.Region(declaration_start, end_point + 1)

# For testing
class TestCommand(sublime_plugin.TextCommand):
    def run(self, edit):   
        for pair in self.view.symbols():
            declaration_region = pair[0]
            scope_region = get_scope_region(self.view, 
                                            declaration_region)
            print(self.view.substr(scope_region))