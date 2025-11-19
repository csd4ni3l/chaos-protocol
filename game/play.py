import arcade, arcade.gui

from utils.constants import menu_background_color, button_style
from utils.preload import button_texture, button_hovered_texture

class Game(arcade.gui.UIView):
    def __init__(self, pypresence_client):
        super().__init__()

    def on_show_view(self):
        super().on_show_view()
