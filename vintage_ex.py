import sublime
import sublime_plugin

class VintageExPromptCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.window.show_input_panel("", ":", self.on_done, None, None)

    def on_done(self, text):
        try:
            if self.window.active_view():
                self.window.run_command("vintage_ex_run", {"cmd": text})
        except ValueError:
            pass


class VintageExRunCommand(sublime_plugin.WindowCommand):
    def run(self, cmd):
        {
            ":only": lambda: self.close_other_tabs(),
            ":w":    lambda: self.save(),
            ":wq":   lambda: self.save_and_close(self.window.active_view()),
            ":wqa":  lambda: self.save_and_close_all(),
            ":q":    lambda: self.close(self.window.active_view()),
            ":q!":   lambda: self.discard_changes_and_close(self.window.active_view()),
            ":qa":   lambda: self.close_all(),
            ":qa!":  lambda: self.discard_changes_and_close_all(),
            ":sp":   lambda: self.split(),
            ":vsp":  lambda: self.vertical_split(),
            ":e":    lambda: self.edit(),
        }.get(cmd,   lambda: self.invalid_command(cmd))()

    def reset_split(self):
        view = self.window.active_view()
        if view:
            # Maybe open the current file in the split tab, too...
            file_name = view.file_name()
            self.window.run_command(
                "set_layout", {
                    "cells": [[0, 0, 1, 1]],
                    "cols": [0.0, 1.0],
                    "rows": [0.0, 1.0]
                }
            )

    def vertical_split(self):
        view = self.window.active_view()
        if view:
            # Maybe open the current file in the split tab, too...
            file_name = view.file_name()
            self.window.run_command(
                "set_layout", {
                    "cells": [[0, 0, 1, 1], [1, 0, 2, 1]],
                    "cols": [0.0, 0.5, 1.0],
                    "rows": [0.0, 1.0]
                }
            )

    def split(self):
        view = self.window.active_view()
        if view:
            # Maybe open the current file in the split tab, too...
            file_name = view.file_name()
            self.window.run_command(
                "set_layout", {
                    "cells": [[0, 0, 1, 1], [0, 1, 1, 2]],
                    "cols":  [0.0, 1.0],
                    "rows": [0.0, 0.5, 1.0]
                }
            )

    def edit(self):
        self.window.run_command("prompt_open")

    def save(self):
        view = self.window.active_view()
        if view:
            view.run_command("save")
            self.switch_to_normal_mode()

    def save_and_close(self, view):
        if view:
            view.run_command("save")
            view.close()
            self.switch_to_normal_mode()

    def discard_changes_and_close_all(self):
        [self.discard_changes_and_close(v) for v in self.window.views()]

    def discard_changes_and_close(self, view):
        if view:
            view.set_scratch(True)
            view.close()

    def close_all(self):
        [self.close(v) for v in self.window.views()]

    def save_and_close_all(self):
        [self.save_and_close(v) for v in self.window.views()]

    def switch_to_normal_mode(self):
        self.window.run_command("exit_insert_mode")

    def close_other_tabs(self):
        self.reset_split()
        [self.close(v) for v in self.window.views() if v != self.window.active_view()]

    def close(self, view):
        if view:
            view.close()

    def invalid_command(self, cmd):
        sublime.status_message("ERR - UNKNOWN COMMAND - " + cmd)
