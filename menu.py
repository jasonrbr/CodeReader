import sublime
import sublime_plugin

class MenuOptions(sublime_plugin.TextCommand):
	def display_menu(self, options):
		print(options)
		sublime.active_window().show_quick_panel(options, self.on_done)
	def on_done():
		print("done")