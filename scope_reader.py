from .config import *
from .parse_symbols import parse_symbols


class ReadingState():
    def __init__(self):
        # Config States
        Config.init()
        self.read_comments = Config.get('read_comments')
        self.read_line_numbers = Config.get('read_line_numbers')
        # Comment State
        self.in_comment = False
        # Available subscopes (functions)
        self.subscope_strings = None
        # Regions to ignore (classes)
        self.subregions_to_ignore = None


class FunctionReadingState(ReadingState):
    def __init__(self):
        super().__init__()
        self.subscope_strings = {
            "}": "exiting {}",
            "for": "for loop",
            "while": "while loop",
            "if": "if statement",
            "else if": "else if statement",
            "else": "else statement"
        }
        # Tracks entering and exiting subscopes
        self.subscope_stack = list()


class ClassReadingState(ReadingState):
    def __init__(self, regions_to_ignore):
        super().__init__()
        self.subregions_to_ignore = regions_to_ignore


def _handle_comment(view, reading_state, line_str):
    # Entering a comment
    if "/*" in line_str:
        reading_state.in_comment = True

    # If inside of a comment, only return the translated string if
    # read comments has been toggled on
    if "//" in line_str or reading_state.in_comment:
        # Exiting a comment
        if "*/" in line_str:
            reading_state.in_comment = False

        # Decide whether to read the comment
        if reading_state.read_comments:
            return "Comment: {}".format(line_str)
        else:
            return None

    # No need to translate
    return line_str


def _handle_subscopes(reading_state, line_str):
    # Exiting subscope
    if '}' in line_str:
        subscope_name = reading_state.subscope_stack.pop()
        subscope_str = reading_state.subscope_strings[subscope_name]
        return True, reading_state.subscope_strings['}'].format(subscope_str)

    # Entering subscope:
    for key, val in reading_state.subscope_strings.items():
        if key in line_str:
            reading_state.subscope_stack.append(key)
            return True, val

    # Not a subscope
    return False, line_str


def _translate_line_region(view, reading_state, line_region):
    line_str = view.substr(line_region)

    # Case: empty line or line of whitespace
    if line_str.isspace():
        return None

    # Case: the scope being read can have subscopes
    # such as loops, if statements, etc
    if reading_state.subscope_strings:
        did_modify, line_str = _handle_subscopes(reading_state, line_str)
        # The line either represents entering or exiting
        # a subscope
        if did_modify:
            return line_str

    # Returns unmodified line if it's not a comment
    return _handle_comment(view, reading_state, line_str)


def _is_reg1_end_in_reg2(reg1, reg2):
    return (reg1.end() >= reg2.begin() and
            reg1.end() <= reg2.end())


def _is_reg1_begin_in_reg2(reg1, reg2):
    return (reg1.begin() >= reg2.begin() and
            reg1.begin() <= reg2.end())


def _ignore_region(reading_state, region):
    assert reading_state.subregions_to_ignore

    # 'Subregions to ignore' is a list sorted in ascending region
    # order. Remove subregions from the front of the list until
    # a subregion that contains region is found.
    while region.begin() > reading_state.subregions_to_ignore[0].end():
        del reading_state.subregions_to_ignore[0]

    # If no subregions were found, no more regions need to be ignored
    if not reading_state.subregions_to_ignore:
        return False, region

    is_subreg_begin_in_reg = \
        _is_reg1_begin_in_reg2(reading_state.subregions_to_ignore[0], region)

    is_subreg_end_in_reg = \
        _is_reg1_end_in_reg2(reading_state.subregions_to_ignore[0], region)

    # If the beginning and end of the subregion is inside the region,
    # the entire region must be ignored.
    if is_subreg_begin_in_reg and is_subreg_end_in_reg:
        return True, None

    # If the subregion is in the second part of the region, modify
    # the region to only contain its first part
    if is_subreg_begin_in_reg:
        return False, sublime.Region(
            region.begin(), reading_state.subregions_to_ignore[0].begin())

    # If the subregion is in the first part of the region, modify
    # the region to only contain its second part
    if is_subreg_end_in_reg:
        return False, sublime.Region(
            reading_state.subregions_to_ignore[0].end() + 1, region.end())

    # Nothing needs to be ignored
    return False, region


def read_region(view, reading_state, region):
    subregions = view.split_by_newlines(region)

    parsed_lines = list()

    for subregion in subregions:
        # Case: scope being read has subregions
        # that need to be ignored
        if reading_state.subregions_to_ignore:
            ignore, subregion = _ignore_region(reading_state, subregion)
            # Goto next subregion if this subregion must
            # be ignored
            if ignore:
                continue

        line_str =\
            _translate_line_region(view, reading_state, subregion)

        # Goto next subregion if the line was translated
        # to the empty string
        if not line_str:
            continue

        # Parse symbols out of line
        # TODO: do I have to do this?
        line_str = parse_symbols(line_str)

        # Concat line numbers if necessary
        if reading_state.read_line_numbers:
            row, _ = view.rowcol(subregion.begin())
            line_str = ('line ' + str(row + 1) +
                        ', ' + line_str)

        parsed_lines.append(line_str)

    return parsed_lines
