import sublime, sublime_plugin


class DebugSetBreakpointCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        #self.view.insert(edit, 0, "Hello, World!")
        mark = [s for s in self.view.sel()]
        #all_breakpoints.append(mark)
        self.view.add_regions("debugger-breakpoint", mark, "mark", "bookmark", sublime.DRAW_EMPTY_AS_OVERWRITE | sublime.PERSISTENT)
