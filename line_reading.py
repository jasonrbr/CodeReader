import sublime
import sublime_plugin

with_line = False

class GetUserInputCommand(sublime_plugin.WindowCommand):
  def run(self):
    self.window.show_input_panel("Give me a command:", "", self.on_done, None, None)

  def on_done(self, text):
    print(text)
    if (text == 'quit'):
      return
    if self.window.active_view():
      self.window.run_command("get_user_input")

# class KeyBindingListener(sublime_plugin.EventListener):
#   def on_window_command(self, window, name, args):
#     print('The window command name is: ' + name)
#     print('The args are: ' + str(args))

#   def on_text_command(self, window, name, args):
#     print('The text command name is: ' + name)
#     print('The args are: ' + str(args))

#https://www.sublimetext.com/docs/3/api_reference.html#sublime_plugin.EventListener

class ToggleLineNumberCommand(sublime_plugin.WindowCommand):
  def run(self):
    global with_line
    with_line = not with_line

class ExampleCommand(sublime_plugin.TextCommand):

  def get_row(self):
    '''
    Returns line number in 1-based indexing of where the cursor is
    '''
    print(self.view.sel()[0])
    (row,col) = self.view.rowcol(self.view.sel()[0].begin())
    return row + 1

  def run(self, edit):
    global with_line
    line = "Hello World!\n"
    if (with_line):
      line = str(self.get_row()) + " " + line
    #self.view.insert(edit, 0, line)
    print(line)

