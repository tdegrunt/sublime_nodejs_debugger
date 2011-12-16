import sublime, sublime_plugin

class DebugTestCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        self.view.insert(edit, 0, "Hello, World!")
