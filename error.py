import sublime
from .audio import say

# error message
error_msg = 'Something went wrong! ' \
            + 'Either you have code not up to standards, ' \
            + 'or something is seriously wrong. ' \
            + 'Please check the console for more details. ' \
            + 'Click okay on this dialog box or ' \
            + 'press enter to continue.'


# pass in a MyError object and process
# it to let the user know of issues
def alert_error(error):
    say(error.msg)
    say(error_msg)
    sublime.error_message(error_msg)


class MyError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)
