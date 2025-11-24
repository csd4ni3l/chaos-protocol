import arcade.color
from arcade.types import Color
from arcade.gui.widgets.buttons import UITextureButtonStyle, UIFlatButtonStyle
from arcade.gui.widgets.slider import UISliderStyle

LOGICAL_OPERATORS = ["and", "or"]
SHAPES = ["rectangle", "circle", "triangle"]
VAR_NAMES = ["a", "b", "c", "d", "e", "f", "g"]

ALLOWED_INPUT = ["a", "b", "c", "d", "e", "q", "w", "s", "t"]

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

VAR_DEFAULT = {
    "shape_type": SHAPES[0],
    "target_type": SHAPES[1],
    "variable": 0,
    "color": "WHITE",
    "size": 10,
    "key_input": ALLOWED_INPUT[0],
    "comparison": COMPARISONS[0]
}

VAR_OPTIONS = {
    "shape_type": SHAPES,
    "target_type": SHAPES,
    "variable": (-700, 700),
    "color": COLORS,
    "size": (1, 200),
    "key_input": ALLOWED_INPUT,
    "comparison": COMPARISONS
}

IF_RULES = {
    "x_position_compare": {
        "key": "x_position_compare",
        "description": "IF X for {a} shape is {b} {c}",
        "trigger": "every_update",
        "user_vars": ["shape_type", "comparison", "variable"],
        "vars": ["shape_type", "comparison", "variable", "event_shape_type", "shape_x"],
        "func": lambda *v: (v[0] == v[3]) and eval(f"{v[4]} {v[1]} {v[2]}")
    },
    
    "y_position_compare": {
        "key": "y_position_compare",
        "description": "IF Y for {a} shape is {b} {c}",
        "trigger": "every_update",
        "user_vars": ["shape_type", "comparison", "variable"],
        "vars": ["shape_type", "comparison", "variable", "event_shape_type", "shape_y"],
        "func": lambda *v: (v[0] == v[3]) and eval(f"{v[4]} {v[1]} {v[2]}")
    },
    
    "size_compare": {
        "key": "size_compare",
        "description": "IF {a} shape size is {b} {c}",
        "trigger": "every_update",
        "user_vars": ["shape_type", "comparison", "variable"],
        "vars": ["shape_type", "comparison", "variable", "event_shape_type", "shape_size"],
        "func": lambda *v: (v[0] == v[3]) and eval(f"{v[4]} {v[1]} {v[2]}")
    },
    
    "spawns": {
        "key": "spawns",
        "description": "IF {a} shape spawns",
        "trigger": "spawn",
        "user_vars": ["shape_type"],
        "vars": ["shape_type", "event_shape_type"],
        "func": lambda *v: v[0] == v[1]
    },
    "destroyed": {
        "key": "destroyed",
        "description": "IF {a} shape is destroyed",
        "trigger": "destroyed",
        "user_vars": ["shape_type"],
        "vars": ["shape_type", "event_shape_type"],
        "func": lambda *v: v[0] == v[1]
    },
    "x_velocity_changes": {
        "key": "x_velocity_changes",
        "description": "IF {a} shape X velocity changes",
        "trigger": "x_velocity_change",
        "user_vars": ["shape_type"],
        "vars": ["shape_type", "event_shape_type"],
        "func": lambda *v: v[0] == v[1]
    },
    "y_velocity_changes": {
        "key": "y_velocity_changes",
        "description": "IF {a} shape Y velocity changes",
        "trigger": "y_velocity_change",
        "user_vars": ["shape_type"],
        "vars": ["shape_type", "event_shape_type"],
        "func": lambda *v: v[0] == v[1]
    },
    "color_changes": {
        "key": "color_changes",
        "description": "IF {a} shape color changes",
        "trigger": "color_change",
        "user_vars": ["shape_type"],
        "vars": ["shape_type", "event_shape_type"],
        "func": lambda *v: v[0] == v[1]
    },
    "size_changes": {
        "key": "size_changes",
        "description": "IF {a} shape size changes",
        "trigger": "size_change",
        "user_vars": ["shape_type"],
        "vars": ["shape_type", "event_shape_type"],
        "func": lambda *v: v[0] == v[1]
    },
    "morphs": {
        "key": "morphs",
        "description": "IF {a} shape morphs into {b}",
        "trigger": "morph",
        "user_vars": ["shape_type", "target_type"],
        "vars": ["shape_type", "target_type", "event_a_type", "event_b_type"],
        "func": lambda *v: (v[0] == v[2]) and (v[3] == v[1])
    },
    "collides": {
        "key": "collides",
        "description": "IF {a} shape collides with {b}",
        "trigger": "collision",
        "user_vars": ["shape_type", "target_type"],
        "vars": ["shape_type", "target_type", "event_a_type", "event_b_type"],
        "func": lambda *v: (v[0] == v[2]) and (v[3] == v[1])
    },
    "on_left_click": {
        "key": "on_left_click",
        "description": "IF you left click",
        "trigger": "on_left_click",
        "user_vars": [],
        "vars": [],
        "func": lambda *v: True
    },
    "on_right_click": {
        "key": "on_right_click",
        "description": "IF you right click",
        "trigger": "on_right_click",
        "user_vars": [],
        "vars": [],
        "func": lambda *v: True
    },
    "on_mouse_move": {
        "key": "on_mouse_move",
        "description": "IF mouse moves",
        "trigger": "on_mouse_move",
        "user_vars": [],
        "vars": [],
        "func": lambda *v: True
    },
    "on_input": {
        "key": "on_input",
        "description": "IF {a} key is pressed",
        "trigger": "on_input",
        "user_vars": ["key_input"],
        "vars": ["key_input", "event_key"],
        "func": lambda *v: v[0] == v[1]
    },    
    "game_launch": {
        "key": "game_launch",
        "description": "IF game launches",
        "trigger": "game_launch",
        "user_vars": [],
        "vars": [],
        "func": lambda *v: True
    },
    "every_update": {
        "key": "every_update",
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
    ("spawns", "color_changes"),
    ("spawns", "size_changes"),
    
    ("destroyed", "morphs"),
    ("destroyed", "collides"),
    ("destroyed", "x_velocity_changes"),
    ("destroyed", "y_velocity_changes"),
    ("destroyed", "x_gravity_changes"),
    ("destroyed", "y_gravity_changes"),
    ("destroyed", "color_changes"),
    ("destroyed", "size_changes"),
    
    ("morphs", "collides"),
    ("morphs", "x_velocity_changes"),
    ("morphs", "y_velocity_changes"),
    ("morphs", "x_gravity_changes"),
    ("morphs", "y_gravity_changes"),
    ("morphs", "color_changes"),
    ("morphs", "size_changes"),
    
    ("collides", "destroyed"),
    ("collides", "morphs"),
    
    ("every_update", "spawns"),
    ("every_update", "destroyed"),
    ("every_update", "morphs"),
    ("every_update", "collides"),
    ("every_update", "x_velocity_changes"),
    ("every_update", "y_velocity_changes"),
    ("every_update", "x_gravity_changes"),
    ("every_update", "y_gravity_changes"),
    ("every_update", "color_changes"),
    ("every_update", "size_changes"),
    ("every_update", "game_launch"),
    
    ("game_launch", "spawns"),
    ("game_launch", "destroyed"),
    ("game_launch", "morphs"),
    ("game_launch", "collides"),
    ("game_launch", "x_velocity_changes"),
    ("game_launch", "y_velocity_changes"),
    ("game_launch", "x_gravity_changes"),
    ("game_launch", "y_gravity_changes"),
    ("game_launch", "color_changes"),
    ("game_launch", "size_changes"),
]

NON_COMPATIBLE_DO_WHEN = [
    ("destroyed", "change_x"),
    ("destroyed", "change_y"),
    ("destroyed", "move_x"),
    ("destroyed", "move_y"),
    ("destroyed", "change_x_velocity"),
    ("destroyed", "change_y_velocity"),
    ("destroyed", "change_x_gravity"),
    ("destroyed", "change_y_gravity"),
    ("destroyed", "change_color"),
    ("destroyed", "change_size"),
    ("destroyed", "morph_into"),
    ("destroyed", "destroy"),
    
    ("morphs", "morph_into"),
    
    ("x_velocity_changes", "change_x_velocity"),
    ("y_velocity_changes", "change_y_velocity"),
    
    ("color_changes", "change_color"),
    
    ("size_changes", "change_size"),
    
    ("every_update", "change_x"),
    ("every_update", "change_y"),
    ("every_update", "move_x"),
    ("every_update", "move_y"),
    ("every_update", "change_x_velocity"),
    ("every_update", "change_y_velocity"),
    ("every_update", "change_color"),
    ("every_update", "change_size"),
    ("every_update", "destroy"),
    ("every_update", "morph_into"),
    
    ("game_launch", "change_x"),
    ("game_launch", "change_y"),
    ("game_launch", "move_x"),
    ("game_launch", "move_y"),
    ("game_launch", "change_x_velocity"),
    ("game_launch", "change_y_velocity"),
    ("game_launch", "change_x_gravity"),
    ("game_launch", "change_y_gravity"),
    ("game_launch", "change_color"),
    ("game_launch", "change_size"),
    ("game_launch", "destroy"),
    ("game_launch", "morph_into")
]

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

    "morph_into": {
        "key": "morph_into",
        "description": "Morph this into {a}",
        "action": {"type": "shape_action", "name": "morph"},
        "user_vars": ["shape_type"],
        "vars": ["shape", "shape_type"]
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
