import os
import arcade.color, operator
from arcade.types import Color
from arcade.gui.widgets.buttons import UITextureButtonStyle, UIFlatButtonStyle
from arcade.gui.widgets.slider import UISliderStyle

# Get the directory where this module is located
_module_dir = os.path.dirname(os.path.abspath(__file__))
_assets_dir = os.path.join(os.path.dirname(_module_dir), 'assets')

SPRITES = {
            os.path.splitext(file_name)[0]: os.path.join(_assets_dir, 'graphics', 'sprites', file_name) 
            for file_name in os.listdir(os.path.join(_assets_dir, 'graphics', 'sprites'))
        }

VAR_NAMES = ["a", "b", "c", "d", "e", "f", "g"]

ALLOWED_INPUT = ["a", "b", "c", "d", "e", "q", "w", "s", "t", "space", "left", "right", "up", "down"]

TRIGGER_COLOR = (255, 204, 102)
DO_COLOR = (102, 178, 255)
IF_COLOR = (144, 238, 144)
FOR_COLOR = (255, 182, 193)

COLORS = [
    "BLACK", "WHITE", "GRAY", "DARK_GRAY", "CYAN", 
    "AMBER", "AQUA", "GREEN", "LIGHT_GREEN",
    "RED", "LIGHT_RED", "DARK_RED",
    "BLUE", "LIGHT_BLUE", "DARK_BLUE",
    "YELLOW", "LIGHT_YELLOW", "DARK_YELLOW",
    "MAGENTA", "PURPLE", "VIOLET", "INDIGO",
    "ORANGE", "BROWN",
    "GOLD", "SILVER", "BRONZE",
    "TEAL", "AZURE",
    "PINK", "HOT_PINK",
    "MINT_GREEN", "CHARTREUSE"
]

COMPARISONS = [">", ">=", "<", "<=", "==", "!="]

OPS = {
    ">": operator.gt,
    "<": operator.lt,
    ">=": operator.ge,
    "<=": operator.le,
    "==": operator.eq,
    "!=": operator.ne,
}

VAR_DEFAULT = {
    "shape_type": "rectangle",
    "target_type": "circle",
    "variable": 0,
    "color": "WHITE",
    "size": 10,
    "key_input": ALLOWED_INPUT[0],
    "comparison": COMPARISONS[0]
}

VAR_OPTIONS = {
    "shape_type": SPRITES,
    "target_type": SPRITES,
    "variable": (-700, 700),
    "color": COLORS,
    "size": (1, 200),
    "key_input": ALLOWED_INPUT,
    "comparison": COMPARISONS
}

VAR_TYPES = {
    "shape_type": "Shape Type",
    "target_type": "Target Type",
    "variable": "Variable",
    "color": "Color",
    "size": "Size",
    "key_input": "Key Input",
    "comparison": "Comparison"
}

TRIGGER_RULES = {
    "every_update": {
        "key": "every_update",
        "user_vars": [],
        "vars": [],
        "description": "Every Update",
        "func": lambda *v: True
    },
    "start": {
        "key": "start",
        "user_vars": [],
        "vars": [],
        "description": "On Game Start",
        "func": lambda *v: True
    },
    "on_input": {
        "key": "on_input",
        "user_vars": ["key_input"],
        "vars": ["key_input", "event_key"],
        "description": "IF {a} key is pressed",
        "func": lambda *v: v[0] == v[1]
    },
    "spawns": {
        "key": "spawns",
        "description": "IF {a} shape spawns",
        "user_vars": ["shape_type"],
        "vars": ["shape_type", "event_shape_type"],
        "func": lambda *v: v[0] == v[1]
    },
    "destroyed": {
        "key": "destroyed",
        "description": "IF {a} shape is destroyed",
        "user_vars": ["shape_type"],
        "vars": ["shape_type", "event_shape_type"],
        "func": lambda *v: v[0] == v[1]
    },
    "color_changes": {
        "key": "color_changes",
        "description": "IF {a} shape color changes",
        "user_vars": ["shape_type"],
        "vars": ["shape_type", "event_shape_type"],
        "func": lambda *v: v[0] == v[1]
    },
    "size_changes": {
        "key": "size_changes",
        "description": "IF {a} shape size changes",
        "user_vars": ["shape_type"],
        "vars": ["shape_type", "event_shape_type"],
        "func": lambda *v: v[0] == v[1]
    },
    "collides": {
        "key": "collides",
        "description": "IF {a} shape collides with {b}",
        "user_vars": ["shape_type", "target_type"],
        "vars": ["shape_type", "target_type", "event_a_type", "event_b_type"],
        "func": lambda *v: (v[0] == v[2]) and (v[3] == v[1])
    },
    "on_left_click": {
        "key": "on_left_click",
        "description": "IF you left click",
        "user_vars": [],
        "vars": [],
        "func": lambda *v: True
    },
    "on_right_click": {
        "key": "on_right_click",
        "description": "IF you right click",
        "user_vars": [],
        "vars": [],
        "func": lambda *v: True
    },
    "on_mouse_move": {
        "key": "on_mouse_move",
        "description": "IF mouse moves",
        "user_vars": [],
        "vars": [],
        "func": lambda *v: True
    },
}

FOR_RULES = {
    "every_shape": {
        "key": "every_shape",
        "user_vars": [],
        "vars": [],
        "description": "For every shape",
    }
}

IF_RULES = {
    "x_position_compare": {
        "key": "x_position_compare",
        "description": "IF X is {a} {b}",
        "user_vars": ["comparison", "variable"],
        "vars": ["comparison", "variable", "shape_x"],
        "func": lambda *v: OPS[v[0]](v[2], v[1])
    },
    "y_position_compare": {
        "key": "y_position_compare",
        "description": "IF Y is {a} {b}",
        "user_vars": ["comparison", "variable"],
        "vars": ["comparison", "variable", "shape_y"],
        "func": lambda *v: OPS[v[0]](v[2], v[1])
    },
    "size_compare": {
        "key": "size_compare",
        "description": "IF size is {a} {b}",
        "user_vars": ["comparison", "variable"],
        "vars": ["comparison", "variable", "shape_size"],
        "func": lambda *v: OPS[v[0]](v[2], v[1])
    },
    "x_velocity_compare": {
        "key": "x_velocity_compare",
        "description": "IF X velocity is {a} {b}",
        "user_vars": ["comparison", "variable"],
        "vars": ["comparison", "variable", "shape_x_velocity"],
        "func": lambda *v: OPS[v[0]](v[2], v[1])
    },
    "y_velocity_compare": {
        "key": "y_velocity_compare",
        "description": "IF Y velocity is {a} {b}",
        "user_vars": ["comparison", "variable"],
        "vars": ["comparison", "variable", "shape_y_velocity"],
        "func": lambda *v: OPS[v[0]](v[2], v[1])
    },
    "color_is": {
        "key": "color_is",
        "description": "IF color is {a}",
        "user_vars": ["color"],
        "vars": ["color", "shape_color"],
        "func": lambda *v: v[0] == v[1]
    },
    "shape_type_is": {
        "key": "shape_type_is",
        "description": "IF shape type is {a}",
        "user_vars": ["shape_type"],
        "vars": ["shape_type", "event_shape_type"],
        "func": lambda *v: v[0] == v[1]
    },
}

DO_RULES = {
    "change_x": {
        "key": "change_x",
        "description": "Change this shape's X to {a}",
        "action": {"type": "shape_action", "name": "change_x"},
        "user_vars": ["variable"],
        "vars": ["shape", "variable"]
    },

    "change_y": {
        "key": "change_y",
        "description": "Change this shape's Y to {a}",
        "action": {"type": "shape_action", "name": "change_y"},
        "user_vars": ["variable"],
        "vars": ["shape", "variable"]
    },

    "move_x": {
        "key": "move_x",
        "description": "Move this shape's X by {a}",
        "action": {"type": "shape_action", "name": "move_x"},
        "user_vars": ["variable"],
        "vars": ["shape", "variable"]
    },

    "move_y": {
        "key": "move_y",
        "description": "Move this shape's Y by {a}",
        "action": {"type": "shape_action", "name": "move_y"},
        "user_vars": ["variable"],
        "vars": ["shape", "variable"]
    },

    "change_x_velocity": {
        "key": "change_x_velocity",
        "description": "Change X velocity of this to {a}",
        "action": {"type": "shape_action", "name": "change_x_velocity"},
        "user_vars": ["variable"],
        "vars": ["shape", "variable"]
    },

    "change_y_velocity": {
        "key": "change_y_velocity",
        "description": "Change Y velocity of this to {a}",
        "action": {"type": "shape_action", "name": "change_y_velocity"},
        "user_vars": ["variable"],
        "vars": ["shape", "variable"]
    },

    "change_color": {
        "key": "change_color",
        "description": "Change this shape's color to {a}",
        "action": {"type": "shape_action", "name": "change_color"},
        "user_vars": ["color"],
        "vars": ["shape", "color"]
    },

    "change_size": {
        "key": "change_size",
        "description": "Change this shape's size to {a}",
        "action": {"type": "shape_action", "name": "change_size"},
        "user_vars": ["size"],
        "vars": ["shape", "size"]
    },

    "destroy": {
        "key": "destroy",
        "description": "Destroy this",
        "action": {"type": "shape_action", "name": "destroy"},
        "user_vars": [],
        "vars": ["shape"]
    },

    "change_x_gravity": {
        "key": "change_x_gravity",
        "description": "Change X gravity to {a}",
        "action": {"type": "global_action", "name": "change_x_gravity"},
        "user_vars": ["variable"],
        "vars": ["variable"]
    },

    "change_y_gravity": {
        "key": "change_y_gravity",
        "description": "Change Y gravity to {a}",
        "action": {"type": "global_action", "name": "change_y_gravity"},
        "user_vars": ["variable"],
        "vars": ["variable"]
    },

    "spawn": {
        "key": "spawn",
        "description": "Spawn {a}",
        "action": {"type": "global_action", "name": "spawn"},
        "user_vars": ["shape_type"],
        "vars": ["shape_type"]
    }
}

PROVIDES_SHAPE = [
    # Trigger
    "spawns",
    "color_changes",
    "size_changes",
    "collides",

    # IFs, technically, these need and provide a shape to the next rule
    "x_position_compare",
    "y_position_compare",
    "size_compare",
    "x_velocity_compare",
    "y_velocity_compare",
    "color_is",
    "shape_type_is",

    # FOR
    "every_shape"
]

NEEDS_SHAPE = [
    # IF
    "x_position_compare",
    "y_position_compare",
    "size_compare",
    "x_velocity_compare",
    "y_velocity_compare",
    "color_is",
    "shape_type_is",

    # DO
    "change_x",
    "change_y",
    "move_x",
    "move_y",
    "change_x_velocity",
    "change_y_velocity",
    "change_size",
    "destroy",
]

RULE_DEFAULTS = {
    rule_type: {
        rule_key: (
            rule_dict["description"].format_map(
                {
                    VAR_NAMES[n]: VAR_NAMES[n]
                    for n, variable in enumerate(rule_dict["user_vars"])
                }
            ),
            [
                VAR_DEFAULT[variable]
                for variable in rule_dict["user_vars"]
            ],
        )
        for rule_key, rule_dict in rule_var.items()
    }

    for rule_type, rule_var in [("if", IF_RULES), ("do", DO_RULES), ("trigger", TRIGGER_RULES), ("for", FOR_RULES)]
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
        "Resolution": {"type": "option", "options": ["1440x900", "1600x900", "1920x1080", "2560x1440", "3840x2160"], "config_key": "resolution"},
        "Anti-Aliasing": {"type": "option", "options": ["None", "2x MSAA", "4x MSAA", "8x MSAA", "16x MSAA"], "config_key": "anti_aliasing", "default": "4x MSAA"},
        "VSync": {"type": "bool", "config_key": "vsync", "default": True},
        "FPS Limit": {"type": "slider", "min": 0, "max": 480, "config_key": "fps_limit", "default": 60},
    },
    "Sound": {
        "Music": {"type": "bool", "config_key": "music", "default": True},
        "Music Volume": {"type": "slider", "min": 0, "max": 100, "config_key": "music_volume", "default": 50},
    },
    "Game": {
        "Default X velocity": {"type": "slider", "min": -999, "max": 999, "config_key": "default_x_velocity", "default": 0},
        "Default Y velocity": {"type": "slider", "min": -999, "max": 999, "config_key": "default_y_velocity", "default": 0},
        "Default X gravity": {"type": "slider", "min": -999, "max": 999, "config_key": "default_x_gravity", "default": 0},
        "Default Y gravity": {"type": "slider", "min": -999, "max": 999, "config_key": "default_y_gravity", "default": 5},
        "Max Shapes": {"type": "slider", "min": 0, "max": 999, "config_key": "max_shapes", "default": 120},
    },
    "Miscellaneous": {
        "Discord RPC": {"type": "bool", "config_key": "discord_rpc", "default": True},
    },
    "Credits": {}
}
settings_start_category = "Graphics"
