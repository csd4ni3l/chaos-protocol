import arcade.color
from arcade.types import Color
from arcade.gui.widgets.buttons import UITextureButtonStyle, UIFlatButtonStyle
from arcade.gui.widgets.slider import UISliderStyle

LOGICAL_OPERATORS = ["and", "or"]
SHAPES = ["rectangle", "circle", "triangle"]
VAR_NAMES = ["a", "b", "c", "d", "e", "f", "g"]

DEFAULT_GRAVITY = 5
DEFAULT_X_VELOCITY = 0
DEFAULT_Y_VELOCITY = 0

COLORS = [key for key, value in arcade.color.__dict__.items() if isinstance(value, Color)]

VAR_DEFAULT = {
    "shape_type": SHAPES[0],
    "target_type": SHAPES[1],
    "variable": 0,
    "color": "WHITE",
    "size": 10,
}

VAR_OPTIONS = {
    "shape_type": SHAPES,
    "target_type": SHAPES,
    "variable": (0, 2500),
    "color": "WHITE",
    "size": (1, 200), 
}

IF_RULES = {
    "x_position": {
        "description": "IF X for {a} shape is {b}",
        "trigger": "every_update",
        "user_vars": ["shape_type", "variable"],
        "vars": ["shape_type", "variable", "event_shape_type", "shape_x"],
        "func": lambda *v: (v[0] == v[2]) and (v[3] == v[1])
    },
    "y_position": {
        "description": "IF Y for {a} shape is {b}",
        "trigger": "every_update",
        "user_vars": ["shape_type", "variable"],
        "vars": ["shape_type", "variable", "event_shape_type", "shape_y"],
        "func": lambda *v: (v[0] == v[2]) and (v[3] == v[1])
    },
    "color_is": {
        "description": "IF {a} shape color is {b}",
        "trigger": "every_update",
        "user_vars": ["shape_type", "color"],
        "vars": ["shape_type", "color", "event_shape_type", "shape_color"],
        "func": lambda *v: (v[0] == v[2]) and (v[3] == v[1])
    },
    "size_is": {
        "description": "IF {a} shape size is {b}",
        "trigger": "every_update",
        "user_vars": ["shape_type", "size"],
        "vars": ["shape_type", "size", "event_shape_type", "shape_size"],
        "func": lambda *v: (v[0] == v[2]) and (v[3] == v[1])
    },
    "spawns": {
        "description": "IF {a} shape spawns",
        "trigger": "spawns",
        "user_vars": ["shape_type"],
        "vars": ["shape_type", "event_shape_type"],
        "func": lambda *v: v[0] == v[1]
    },
    "destroyed": {
        "description": "IF {a} shape is destroyed",
        "trigger": "destroyed",
        "user_vars": ["shape_type"],
        "vars": ["shape_type", "event_shape_type"],
        "func": lambda *v: v[0] == v[1]
    },
    "x_velocity_changes": {
        "description": "IF {a} shape X velocity changes",
        "trigger": "x_change",
        "user_vars": ["shape_type"],
        "vars": ["shape_type", "event_shape_type"],
        "func": lambda *v: v[0] == v[1]
    },
    "y_velocity_changes": {
        "description": "IF {a} shape Y velocity changes",
        "trigger": "y_change",
        "user_vars": ["shape_type"],
        "vars": ["shape_type", "event_shape_type"],
        "func": lambda *v: v[0] == v[1]
    },
    "x_gravity_changes": {
        "description": "IF {a} shape X gravity changes",
        "trigger": "gravity_x_change",
        "user_vars": ["shape_type"],
        "vars": ["shape_type", "event_shape_type"],
        "func": lambda *v: v[0] == v[1]
    },
    "y_gravity_changes": {
        "description": "IF {a} shape Y gravity changes",
        "trigger": "gravity_y_change",
        "user_vars": ["shape_type"],
        "vars": ["shape_type", "event_shape_type"],
        "func": lambda *v: v[0] == v[1]
    },
    "gravity_changes": {
        "description": "IF gravity changes",
        "user_vars": [],
        "trigger": "gravity_change",
        "vars": [],
        "func": lambda *v: True
    },
    "color_changes": {
        "description": "IF {a} shape color changes",
        "trigger": "color_change",
        "user_vars": ["shape_type"],
        "vars": ["shape_type", "event_shape_type"],
        "func": lambda *v: v[0] == v[1]
    },
    "size_changes": {
        "description": "IF {a} shape size changes",
        "trigger": "size_change",
        "user_vars": ["shape_type"],
        "vars": ["shape_type", "event_shape_type"],
        "func": lambda *v: v[0] == v[1]
    },
    "morphs": {
        "description": "IF {a} shape morphs into {b}",
        "trigger": "morph",
        "user_vars": ["shape_type", "target_type"],
        "vars": ["shape_type", "target_type", "event_a_type", "event_b_type"],
        "func": lambda *v: (v[0] == v[2]) and (v[3] == v[1])
    },
    "collides": {
        "description": "IF {a} shape collides with {b}",
        "trigger": "collision",
        "user_vars": ["shape_type", "target_type"],
        "vars": ["shape_type", "target_type", "event_a_type", "event_b_type"],
        "func": lambda *v: (v[0] == v[2]) and (v[3] == v[1])
    },
    "launch": {
        "description": "IF game launches",
        "trigger": "game_launch",
        "user_vars": [],
        "vars": [],
        "func": lambda *v: True
    },
    "every_update": {
        "description": "Every update",
        "trigger": "every_update",
        "user_vars": [],
        "vars": [],
        "func": lambda *v: True
    }
}

NON_COMPATIBLE_WHEN = [
    ("spawns", "destroyed"),
    ("spawns", "morphs"),
    ("spawns", "collides"),
    ("spawns", "x_velocity_changes"),
    ("spawns", "y_velocity_changes"),
    ("spawns", "x_gravity_changes"),
    ("spawns", "y_gravity_changes"),
    ("spawns", "gravity_changes"),
    ("spawns", "color_changes"),
    ("spawns", "size_changes"),

    ("destroyed", "morphs"),
    ("destroyed", "collides"),
    ("destroyed", "x_velocity_changes"),
    ("destroyed", "y_velocity_changes"),
    ("destroyed", "x_gravity_changes"),
    ("destroyed", "y_gravity_changes"),
    ("destroyed", "gravity_changes"),
    ("destroyed", "color_changes"),
    ("destroyed", "size_changes"),

    ("morphs", "collides"),
    ("morphs", "x_velocity_changes"),
    ("morphs", "y_velocity_changes"),
    ("morphs", "x_gravity_changes"),
    ("morphs", "y_gravity_changes"),
    ("morphs", "gravity_changes"),
    ("morphs", "color_changes"),
    ("morphs", "size_changes"),

    ("collides", "destroyed"),
    ("collides", "morphs"),
    ("collides", "gravity_changes"),

    ("x_gravity_changes", "gravity_changes"),
    ("y_gravity_changes", "gravity_changes"),

    ("color_changes", "gravity_changes"),
    ("size_changes", "gravity_changes"),

    ("every_update", "spawns"),
    ("every_update", "destroyed"),
    ("every_update", "morphs"),
    ("every_update", "collides"),
    ("every_update", "x_velocity_changes"),
    ("every_update", "y_velocity_changes"),
    ("every_update", "x_gravity_changes"),
    ("every_update", "y_gravity_changes"),
    ("every_update", "gravity_changes"),
    ("every_update", "color_changes"),
    ("every_update", "size_changes"),
    ("every_update", "launch"),

    ("launch", "spawns"),
    ("launch", "destroyed"),
    ("launch", "morphs"),
    ("launch", "collides"),
    ("launch", "x_velocity_changes"),
    ("launch", "y_velocity_changes"),
    ("launch", "x_gravity_changes"),
    ("launch", "y_gravity_changes"),
    ("launch", "gravity_changes"),
    ("launch", "color_changes"),
    ("launch", "size_changes"),
]

NON_COMPATIBLE_DO_WHEN = [
    ("destroyed", "change_x"),
    ("destroyed", "change_y"),
    ("destroyed", "move_x"),
    ("destroyed", "move_y"),
    ("destroyed", "change_x_velocity"),
    ("destroyed", "change_y_velocity"),
    ("destroyed", "change_gravity"),
    ("destroyed", "change_color"),
    ("destroyed", "change_size"),
    ("destroyed", "morph_into"),
    ("destroyed", "destroy"),

    ("morphs", "morph_into"),

    ("gravity_changes", "change_x"),
    ("gravity_changes", "change_y"),
    ("gravity_changes", "move_x"),
    ("gravity_changes", "move_y"),
    ("gravity_changes", "change_x_velocity"),
    ("gravity_changes", "change_y_velocity"),
    ("gravity_changes", "change_gravity"),
    ("gravity_changes", "change_color"),
    ("gravity_changes", "change_size"),
    ("gravity_changes", "morph_into"),
    ("gravity_changes", "destroy"),

    ("x_velocity_changes", "change_x_velocity"),
    ("y_velocity_changes", "change_y_velocity"),
    
    ("color_changes", "change_color"),
    ("size_changes", "change_size"),

    ("launch", "change_x"),
    ("launch", "change_y"),
    ("launch", "move_x"),
    ("launch", "move_y"),
    ("launch", "change_x_velocity"),
    ("launch", "change_y_velocity"),
    ("launch", "change_gravity"),
    ("launch", "change_color"),
    ("launch", "change_size"),
    ("launch", "destroy"),
    ("launch", "morph_into")
]

DO_RULES = {
    "change_x": {
        "description": "Change this shape's X to {a}",
        "action": {"type": "shape_action", "name": "change_x"},
        "user_vars": ["variable"]
    },

    "change_y": {
        "description": "Change this shape's Y to {a}",
        "action": {"type": "shape_action", "name": "change_y"},
        "user_vars": ["variable"]
    },

    "move_x": {
        "description": "Move this shape's X by {a}",
        "action": {"type": "shape_action", "name": "move_x"},
        "user_vars": ["variable"]
    },

    "move_y": {
        "description": "Move this shape's Y by {a}",
        "action": {"type": "shape_action", "name": "move_y"},
        "user_vars": ["variable"]
    },

    "change_x_velocity": {
        "description": "Change X velocity of this to {a}",
        "action": {"type": "shape_action", "name": "change_x_vel"},
        "user_vars": ["variable"]
    },

    "change_y_velocity": {
        "description": "Change Y velocity of this to {a}",
        "action": {"type": "shape_action", "name": "change_y_vel"},
        "user_vars": ["variable"]
    },

    "change_color": {
        "description": "Change this shape's color to {a}",
        "action": {"type": "shape_action", "name": "change_color"},
        "user_vars": ["color"]
    },

    "change_size": {
        "description": "Change this shape's size to {a}",
        "action": {"type": "shape_action", "name": "change_size"},
        "user_vars": ["size"]
    },

    "destroy": {
        "description": "Destroy this",
        "action": {"type": "shape_action", "name": "destroy"},
        "user_vars": []
    },

    "morph_into": {
        "description": "Morph this into {a}",
        "action": {"type": "shape_action", "name": "morph"},
        "user_vars": ["shape_type"]
    },

    "change_gravity": {
        "description": "Change this shape's gravity to {a}",
        "action": {"type": "shape_action", "name": "change_gravity"},
        "user_vars": ["variable"]
    },

    "spawn": {
        "description": "Spawn {a}",
        "action": {"type": "global_action", "name": "spawn"},
        "user_vars": ["shape_type"]
    }
}

menu_background_color = (30, 30, 47)
log_dir = 'logs'
discord_presence_id = 1440807203094138940

button_style = {'normal': UITextureButtonStyle(font_name="Roboto", font_color=arcade.color.BLACK), 'hover': UITextureButtonStyle(font_name="Roboto", font_color=arcade.color.BLACK),
                'press': UITextureButtonStyle(font_name="Roboto", font_color=arcade.color.BLACK), 'disabled': UITextureButtonStyle(font_name="Roboto", font_color=arcade.color.BLACK)}
big_button_style = {'normal': UITextureButtonStyle(font_name="Roboto", font_color=arcade.color.BLACK, font_size=26), 'hover': UITextureButtonStyle(font_name="Roboto", font_color=arcade.color.BLACK, font_size=26),
                'press': UITextureButtonStyle(font_name="Roboto", font_color=arcade.color.BLACK, font_size=26), 'disabled': UITextureButtonStyle(font_name="Roboto", font_color=arcade.color.BLACK, font_size=26)}

dropdown_style = {'normal': UIFlatButtonStyle(font_name="Roboto", font_color=arcade.color.BLACK, bg=Color(128, 128, 128)), 'hover': UIFlatButtonStyle(font_name="Roboto", font_color=arcade.color.BLACK, bg=Color(49, 154, 54)),
                  'press': UIFlatButtonStyle(font_name="Roboto", font_color=arcade.color.BLACK, bg=Color(128, 128, 128)), 'disabled': UIFlatButtonStyle(font_name="Roboto", font_color=arcade.color.BLACK, bg=Color(128, 128, 128))}

slider_default_style = UISliderStyle(bg=Color(128, 128, 128), unfilled_track=Color(128, 128, 128), filled_track=Color(49, 154, 54))
slider_hover_style = UISliderStyle(bg=Color(49, 154, 54), unfilled_track=Color(128, 128, 128), filled_track=Color(49, 154, 54))

slider_style = {'normal': slider_default_style, 'hover': slider_hover_style, 'press': slider_hover_style, 'disabled': slider_default_style}

settings = {
    "Graphics": {
        "Window Mode": {"type": "option", "options": ["Windowed", "Fullscreen", "Borderless"], "config_key": "window_mode", "default": "Windowed"},
        "Resolution": {"type": "option", "options": ["1366x768", "1440x900", "1600x900", "1920x1080", "2560x1440", "3840x2160"], "config_key": "resolution"},
        "Anti-Aliasing": {"type": "option", "options": ["None", "2x MSAA", "4x MSAA", "8x MSAA", "16x MSAA"], "config_key": "anti_aliasing", "default": "4x MSAA"},
        "VSync": {"type": "bool", "config_key": "vsync", "default": True},
        "FPS Limit": {"type": "slider", "min": 0, "max": 480, "config_key": "fps_limit", "default": 60},
    },
    "Sound": {
        "Music": {"type": "bool", "config_key": "music", "default": True},
        "SFX": {"type": "bool", "config_key": "sfx", "default": True},
        "Music Volume": {"type": "slider", "min": 0, "max": 100, "config_key": "music_volume", "default": 50},
        "SFX Volume": {"type": "slider", "min": 0, "max": 100, "config_key": "sfx_volume", "default": 50},
    },
    "Miscellaneous": {
        "Discord RPC": {"type": "bool", "config_key": "discord_rpc", "default": True},
    },
    "Credits": {}
}
settings_start_category = "Graphics"
