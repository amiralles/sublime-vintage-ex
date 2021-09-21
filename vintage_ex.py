import sublime, sublime_plugin
import os
import re
from pathlib import Path

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
        [cmd, *args] = cmd.split('/')
        {
            ":only": lambda: self.close_other_tabs(),
            ":w":    lambda: self.save(),
            ":wa":   lambda: self.save_all(),
            ":wq":   lambda: self.save_and_close(self.window.active_view()),
            ":wqa":  lambda: self.save_and_close_all(),
            ":q":    lambda: self.close(self.window.active_view()),
            ":q!":   lambda: self.discard_changes_and_close(self.window.active_view()),
            ":qa":   lambda: self.close_all(),
            ":qa!":  lambda: self.discard_changes_and_close_all(),
            ":sp":   lambda: self.split(),
            ":vsp":  lambda: self.vertical_split(),
            ":e":    lambda: self.edit(),
            ":mru":  lambda: self.mru(),
            ":clear_mru":  lambda: self.clear_mru(),
            # ":%s":   lambda: self.find_and_replace(args),
        }.get(cmd,   lambda: self.goto_line_or_invalid_command(cmd))()

    def goto_line_or_invalid_command(self, cmd):
        if cmd:
            maybe_line_number = cmd[1:]
            ok, line = self.try_parse_line_number(maybe_line_number)
            if ok:
                self.goto_line(line)
            else:
                self.invalid_command(cmd)

    def goto_line(self, line_number):
        view = self.window.active_view()
        if view:
            self.window.run_command("goto_line", {'line': line_number})

    def try_parse_line_number(self, string):
        try:
            line_number = int(string)
            return True, line_number
        except ValueError:
            return False, "Not a valid line number."

    def mru(self):
         self.window.run_command("mru")

    def clear_mru(self):
         self.window.run_command("mru_clear")

    # TODO: Find a way to set "replace_with" text.
    # def find_and_replace(self, args):
    #     # TODO: Parse and apply options.
    #     [find, replace, *opts] = args
    #     self.window.run_command(
    #         "show_panel", {
    #             "panel": "replace",
    #             "reverse": False,
    #             "regex": True,
    #             "case_sensitive": True,
    #             "whole_word": False ,
    #             "in_selection": False,
    #             "wrap": True,
    #             "highlight_matches": True
    #         }
    #     )

    #     self.window.run_command('insert', {'characters': find})

    def reset_split(self):
        view = self.window.active_view()
        if view:
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

    def save_all(self):
        self.window.run_command("save_all")

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

# This command allows us to quickly jump to the testing file
# in projects that follow Elixir's naming conventions.
# TODO: Make it so it can find the test file even when the directory structure
# doesn't match the lib/test convention.
# 1. Try with full path
# 2. Try finding the file anywhere inside the *test* dir of the
#    current project.
class JumpToExTestFileCommand(sublime_plugin.WindowCommand):
    def run(self):
        if self.can_jump_to_active_file_test():
            self.window.open_file(self.test_file_name())
        else:
            sublime.status_message("ERR - No test file :/")

    def can_jump_to_active_file_test(self):
        return self.active_file_extension() == ".ex" and \
            Path(self.test_file_name()).is_file()

    def active_file_extension(self):
        *_, ext = self.window.active_view().file_name().split(".")
        return f".{ext}"

    def test_file_name(self):
        return os.path.join(self.test_path(), self.test_name())

    def test_path(self):
        path = re.sub("/lib/", "/test/", self.window.active_view().file_name())
        return os.path.dirname(path)

    def test_name(self):
        basename = os.path.basename(self.window.active_view().file_name())
        name, _ = basename.split(".")
        return f"{name}_test.exs"

# Jumps back and forth between the previous and next cursor positions,
# similarly to vim's bultin backtick-backtick command.
class BackticksJumpCommand(sublime_plugin.WindowCommand):
    BWD=-1
    FWD=1
    next_jump_direction=BWD

    def run(self):
        if self.next_jump_direction == self.FWD:
            self.run_command_on_active_view("jump_forward")
        else:
            self.run_command_on_active_view("jump_back")
        self.toggle_next_jump_direction()

    def toggle_next_jump_direction(self):
        if self.next_jump_direction == self.FWD:
            self.next_jump_direction = self.BWD
        else:
            self.next_jump_direction = self.FWD

    def run_command_on_active_view(self, cmd):
        view = self.window.active_view()
        if view:
            view.run_command(cmd)
        else:
            print("There is no active view.")

# This setting affects the number of entries we *show* on the quick panel. It
# has no effect on the number of entries we store.
MRU_MAX_ENTRIES = 30
MRU_MAX_FILE_NAME_WIDTH = 45
MRU_MAX_PATH_DISPLAY_LEN = 120
MRU_FILE_NAME = ".sublime-mru"
MRU_NO_FILES_MSG = "There are no recently used files."

class Mru():
    def describe_current_project_mru_files(self):
        return [d for d in self.describe_mru_files() if self.is_current_project_file(d["full_path"])]

    def is_current_project_file(self, file_path):
        return self.current_project_path() in file_path

    def current_project_path(self):
        folders = self.window.folders()
        return folders[0] if len(folders) > 0 else ""

    def largest_file_name_in_current_project(self):
        largest_file_name = ""
        for file_path in self.mru_files_in_current_project():
            file_name = os.path.basename(file_path)
            if len(file_name) > len(largest_file_name):
                largest_file_name = file_name
        return largest_file_name

    def mru_files_in_current_project(self):
        with open(self.mru_file_fullpath(), "r") as file:
            files = []
            for index, line in enumerate(file, start=1):
                if index > MRU_MAX_ENTRIES:
                    return files

                file_path = line.strip()
                if self.is_current_project_file(file_path):
                    files.insert(len(files) - 1, file_path)
            return files

    # Returns a list of key value pairs for each entry in the MRU file
    # where the *key* is the caption we use for the quick_panel and *value*
    # is the absolute file path that allows us to open the selected item.
    def describe_mru_files(self):
        files_descriptions = []
        if self.mru_file_exists():
            with open(self.mru_file_fullpath(), "r") as f:
                for line in f:
                    file_path = line.strip()
                    if file_path:
                        files_descriptions.append({
                            "file_description": self.describe_file(file_path),
                            "full_path": file_path
                        }
                    )
        return files_descriptions

    # Returns a list of MRU files paths.
    def read_mru_file(self):
        mru_files_paths = []
        if self.mru_file_exists():
            with open(self.mru_file_fullpath(), "r") as f:
                for line in f:
                    file_path = line.strip()
                    if file_path:
                        mru_files_paths.append(file_path)

        return mru_files_paths

    def update_mru_file(self, file_path):
        mru_files_paths = self.read_mru_file()

        if file_path in mru_files_paths:
            mru_files_paths.remove(file_path)

        mru_files_paths.insert(0, file_path)
        with open(self.mru_file_fullpath(), "w") as f:
            for file_path in mru_files_paths:
                if file_path:
                    f.write(file_path + os.linesep)

    # Returns a string in the form of:
    # foo.txt  | /Users/jane/tmp/
    # bar.txt  | /Users/jane/tmp/
    def describe_file(self, file_path):
        relevant_dir_names = self.project_relative_path(file_path).split("/")[:3]
        relevant_dirs_path = "/".join(relevant_dir_names)

        pad_size = len(self.largest_file_name_in_current_project())
        if (pad_size > MRU_MAX_FILE_NAME_WIDTH):
            pad_size = MRU_MAX_ENTRIES

        formatted_file_name = os.path.basename(file_path).ljust(pad_size, " ")
        return f"{formatted_file_name} | {relevant_dirs_path}"

    def mru_file_exists(self):
        full_path = self.mru_file_fullpath()
        if Path(full_path).is_file():
            return True

    def project_relative_path(self, file_path):
        return file_path.replace(self.current_project_path() + "/", "")[:MRU_MAX_PATH_DISPLAY_LEN]

    def mru_file_fullpath(self):
        home = os.path.expanduser("~")
        return os.path.join(home, MRU_FILE_NAME)


class MruOnSave(sublime_plugin.EventListener, Mru):
    def on_activated_async(self, view):
        self.update_mru_file(view.file_name())


class MruClearCommand(sublime_plugin.WindowCommand, Mru):
    def run(self):
        os.remove(self.mru_file_fullpath())

# Shows most recently used files in the current project.
class MruCommand(sublime_plugin.WindowCommand, Mru):
    def run(self):
        files_descriptions = self.describe_current_project_mru_files()
        if len(files_descriptions) > 0:
            items = [x["file_description"] for x in files_descriptions]
            self.window.show_quick_panel(
                items=items[:MRU_MAX_ENTRIES],
                on_select=lambda idx: self.open_file(files_descriptions, idx))
        else:
            print(MRU_NO_FILES_MSG)

    def open_file(self, mru_files, idx):
        if idx >= 0:
            self.window.open_file(mru_files[idx]['full_path'])
