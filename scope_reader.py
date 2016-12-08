from .config import *
from .parse_symbols import parse_symbols


class Reader():
    def __init__(self):
        Config.init()
        self._read_line_numbers = Config.get('read_line_numbers')
        self._read_comments = Config.get('read_comments')
        self._subscope_strings = {
            "}": "exiting {}",
            "for": "foor loop",
            "while": "while loop",
            "if": "if statement",
            "else if": "else if statement",
            "else": "else statement"
        }

    def read(self, view, region, subregions_to_ignore=None):
        self._subscope_stack = list()
        self._subregions_to_ignore = subregions_to_ignore
        # Tracks whether or not the reader is currently in
        # a comment
        self._in_comment = False

        subregions = view.split_by_newlines(region)
        parsed_lines = list()

        for subregion in subregions:
            ignore, modified_subregion = self._ignore_region(subregion)

            # Do nothing if subregion should be ignored
            if ignore:
                continue

            line_str = view.substr(modified_subregion)
            translated_line = self._translate_line(line_str)

            if not translated_line:
                continue

            # Parse symbols out of line
            # TODO: just have say do this?
            parsed_line = parse_symbols(translated_line)

            # Concat line numbers
            if self._read_line_numbers:
                row, _ = view.rowcol(modified_subregion.begin())
                parsed_line = ('line ' + str(row + 1) +
                               ', ' + parsed_line)

            parsed_lines.append(parsed_line)

        return parsed_lines

    def _translate_line(self, line_str):
        # Case: empty line or line of whitespace
        if line_str.isspace():
            return None

        # Exiting subscope
        if '}' in line_str:
            print("line: " + line_str)
            subscope_name = self._subscope_stack.pop()
            subscope_str = self._subscope_strings[subscope_name]
            return self._subscope_strings['}'].format(subscope_str)

        # Entering subscope:
        for subscope_name, subscope_string in self._subscope_strings.items():
            if subscope_name in line_str:
                self._subscope_stack.append(subscope_name)
                return subscope_string

        # Entering a comment
        if "/*" in line_str:
            self._in_comment = True

        # If inside of a comment, only return the translated string if
        # read comments has been toggled on
        if "//" in line_str or self._in_comment:
            # Exiting a comment
            if "*/" in line_str:
                self._in_comment = False

            # Decide whether to read the comment
            if self._read_comments:
                return "Comment: {}".format(line_str)
            else:
                return None

        # No need to translate
        return line_str

    def _ignore_region(self, subregion):
        # No regions should be ignored
        if not self._subregions_to_ignore:
            return False, subregion

        # 'Subregions to ignore' is a list sorted in ascending region
        # order. Remove subregions from the front of the list until
        # a subregion that contains region is found. If none can be
        # found, no other regions must be ignored.
        while subregion.begin() > self._subregions_to_ignore[0].end():
            del self._subregions_to_ignore[0]

        # Check if any subregions to ignore remain
        if not self._subregions_to_ignore:
            return False, subregion

        is_begin_of_subregion_inside_region = \
            self._is_begin_of_subregion_inside_region(
                subregion, self._subregions_to_ignore[0])

        is_end_of_subregion_inside_region = \
            self._is_end_of_subregion_inside_region(
                subregion, self._subregions_to_ignore[0])

        # Ignore the entire subregion if its begin and end point lies
        # within the superregion (inclusive)
        if (is_begin_of_subregion_inside_region and
                is_end_of_subregion_inside_region):
            return True, subregion
        # Modify the subregion if its first section lies within
        # the subregion
        elif is_begin_of_subregion_inside_region:
            return False, sublime.Region(
                self._subregions_to_ignore[0].end() + 1, subregion.end())
        # Modify the subregion if its last section lies within
        # the subregion
        elif is_end_of_subregion_inside_region:
            return False, sublime.Region(subregion.begin(),
                                         self._subregions_to_ignore[0].begin())
        # Don't modify the subregion
        else:
            return False, subregion

    def _is_begin_of_subregion_inside_region(self, subregion, region):
        """
        Returns true if subregion.begin() lies inbetween the subregion.begin()
        and subregion.end() inclusive.
        e.g. returns true if subregion = (5, 15) and region = (0, 10)
        """
        return (subregion.begin() >= region.begin() and
                subregion.begin() <= region.end())

    def _is_end_of_subregion_inside_region(self, subregion, region):
        """
        Returns true if subregion.end() lies inbetween the subregion.begin()
        and subregion.end() inclusive.
        e.g. returns true if subregion = (0, 10) and region = (5, 15)
        """
        return (subregion.end() >= region.begin() and
                subregion.end() <= region.end())
