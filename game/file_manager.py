import arcade, arcade.gui, os, time

from utils.constants import button_style
from utils.preload import button_texture, button_hovered_texture

from arcade.gui.experimental.scroll_area import UIScrollArea, UIScrollBar

class FileManager(arcade.gui.UIAnchorLayout):
    def __init__(self, width, allowed_extensions):
        super().__init__(size_hint=(0.95, 0.875), vertical=False)

        self.filemanager_width = width

        self.current_directory = os.path.expanduser("~")
        self.allowed_extensions = allowed_extensions
        self.file_buttons = []
        self.submitted_content = ""
        self.mode = None

        self.content_cache = {}
        self.pre_cache_contents()

        self.current_directory_label = self.add(arcade.gui.UILabel(text=self.current_directory, font_name="Roboto", font_size=22), anchor_x="center", anchor_y="top", align_y=-10)

        self.scroll_area = UIScrollArea(size_hint=(0.665, 0.7)) # center on screen
        self.scroll_area.scroll_speed = -50
        self.add(self.scroll_area, anchor_x="center", anchor_y="center", align_y=self.filemanager_width * 0.025)

        self.scrollbar = UIScrollBar(self.scroll_area)
        self.scrollbar.size_hint = (0.02, 1)
        self.add(self.scrollbar, anchor_x="right", anchor_y="bottom")

        self.files_box = arcade.gui.UIBoxLayout(space_between=5)
        self.scroll_area.add(self.files_box)

        self.bottom_box = self.add(arcade.gui.UIBoxLayout(space_between=5), anchor_x="center", anchor_y="bottom", align_y=5)

        self.filename_label = self.bottom_box.add(arcade.gui.UILabel(text="Filename:", font_name="Roboto", font_size=17))
        self.filename_input = self.bottom_box.add(arcade.gui.UIInputText(width=self.filemanager_width * 0.35, height=self.filemanager_width * 0.02).with_border(color=arcade.color.WHITE))
        
        self.submit_button = self.bottom_box.add(arcade.gui.UITextureButton(texture=button_texture, texture_hovered=button_hovered_texture, text="Submit", style=button_style, width=self.filemanager_width * 0.5, height=self.filemanager_width * 0.025))
        self.submit_button.on_click = lambda event: self.submit(self.current_directory)

        self.submit_button.visible = False
        self.filename_label.visible = False
        self.filename_input.visible = False

        self.show_directory()

    def change_mode(self, mode):
        self.mode = mode
        self.filename_input.visible = self.mode == "export"
        self.filename_label.visible = self.mode == "export"
        self.submit_button.visible = self.mode == "export"

    def submit(self, content):
        self.submitted_content = content if self.mode == "import" else f"{content}/{self.filename_input.text}"

        self.disable()

    def get_content(self, directory):
        if not directory in self.content_cache or time.perf_counter() - self.content_cache[directory][-1] >= 30:
            try:
                entries = os.listdir(directory)
            except PermissionError:
                return None

            filtered = [
                entry for entry in entries
                if (os.path.isdir(os.path.join(directory, entry)) and not "." in entry) or
                os.path.splitext(entry)[1].lower() in self.allowed_extensions
            ]

            sorted_entries = sorted(
                filtered,
                key=lambda x: (0 if os.path.isdir(os.path.join(directory, x)) else 1, x.lower())
            )

            self.content_cache[directory] = sorted_entries
            self.content_cache[directory].append(time.perf_counter())

        return self.content_cache[directory][:-1]

    def pre_cache_contents(self):
        for directory in self.walk_limited_depth(self.current_directory):
            self.get_content(directory)

    def walk_limited_depth(self, start_dir, max_depth=2):
        start_dir = os.path.abspath(start_dir)

        def _walk(current_dir, current_depth):
            if current_depth > max_depth:
                return

            yield current_dir
            try:
                with os.scandir(current_dir) as it:
                    for entry in it:
                        if entry.is_dir(follow_symlinks=False):
                            yield from _walk(entry.path, current_depth + 1)
            except PermissionError:
                pass  # skip directories you can't access

        return _walk(start_dir, 0)

    def show_directory(self):
        self.files_box.clear()
        self.file_buttons.clear()

        self.current_directory_label.text = self.current_directory

        self.file_buttons.append(self.files_box.add(arcade.gui.UITextureButton(texture=button_texture, texture_hovered=button_hovered_texture, text="Go up", style=button_style, width=self.filemanager_width / 1.5)))
        self.file_buttons[-1].on_click = lambda event, directory=self.current_directory: self.change_directory(os.path.dirname(directory))

        for file in self.get_content(self.current_directory):
            self.file_buttons.append(self.files_box.add(arcade.gui.UITextureButton(texture=button_texture, texture_hovered=button_hovered_texture, text=file, style=button_style, width=self.filemanager_width / 1.5)))
            if os.path.isdir(f"{self.current_directory}/{file}"):
                self.file_buttons[-1].on_click = lambda event, directory=f"{self.current_directory}/{file}": self.change_directory(directory)
            else:
                self.file_buttons[-1].on_click = lambda event, file=f"{self.current_directory}/{file}": self.submit(file)

    def disable(self):
        self.parent.parent.disable() # The FileManager UIManager. self.parent is the FileManager UIAnchorLayout

    def change_directory(self, directory):
        if directory.startswith("//"): # Fix / paths
            directory = directory[1:]

        self.current_directory = directory

        self.show_directory()