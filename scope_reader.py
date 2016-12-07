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
            # Do nothing if subregion should be ignored
            if self._ignore_region(subregion):
                continue

            line_str = view.substr(subregion)
            translated_line = self._translate_line(line_str)

            if not translated_line:
                continue

            # Parse symbols out of line
            # TODO: just have say do this?
            parsed_line = parse_symbols(translated_line)

            # Concat line numbers
            if self._read_line_numbers:
                row, _ = view.rowcol(subregion.begin())
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
            subscope_name = self._subscope_stack.pop()
            subscope_str = self._subscope_strings[subscope_name]
            return self._subscope_strings['}'].format(subscope_str)

        # Entering subscope:
        for subscope_name, subscope_string in self._subscope_strings.items():
            print(subscope_name)
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

    def _ignore_region(self, region):
        # No regions should be ignored
        if not self._subregions_to_ignore:
            return False

        # 'Subregions to ignore' is a list sorted in ascending region
        # order. Remove subregions from the front of the list until
        # a subregion that contains region is found. If none can be
        # found, no other regions must be ignored.
        while region.begin() > self._subregions_to_ignore[0].end():
            del self._subregions_to_ignore[0]

        # Returns False if the previous loop emptied all subregions
        # in 'subregions to ignore'. Checks whether region is contained
        # within the first subregion in 'subregions to ignore'
        return (self._subregions_to_ignore and
                region.begin() >= self._subregions_to_ignore[0].begin() and
                region.end() <= self._subregions_to_ignore.end())