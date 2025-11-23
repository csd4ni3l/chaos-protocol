import arcade, arcade.gui, pyglet, random

from utils.constants import slider_style, dropdown_style, VAR_NAMES, VAR_DEFAULT, DEFAULT_GRAVITY, VAR_OPTIONS, DO_RULES, IF_RULES

from arcade.gui.experimental.scroll_area import UIScrollArea, UIScrollBar

from game.rules import generate_rule
from game.sprites import *

class Game(arcade.gui.UIView):
    def __init__(self, pypresence_client):
        super().__init__()

        self.pypresence_client = pypresence_client
        self.pypresence_client.update(state="Causing Chaos")

        self.anchor = self.add_widget(arcade.gui.UIAnchorLayout(size_hint=(1, 1)))

        self.scroll_area = UIScrollArea(size_hint=(0.25, 1)) # center on screen
        self.scroll_area.scroll_speed = -75
        self.anchor.add(self.scroll_area, anchor_x="right", anchor_y="center", align_x=-self.window.width * 0.02)

        self.scrollbar = UIScrollBar(self.scroll_area)
        self.scrollbar.size_hint = (0.02, 1)
        self.anchor.add(self.scrollbar, anchor_x="right", anchor_y="center")

        self.rules_box = arcade.gui.UIBoxLayout(align="left", size_hint=(0.25, 1)).with_background(color=arcade.color.DARK_GRAY)
        self.scroll_area.add(self.rules_box)

        self.gravity = DEFAULT_GRAVITY

        self.current_ruleset_num = 0
        self.rulesets = {}
        self.rule_values = {}
        self.triggered_events = []

        self.rule_labels = {}
        self.rule_var_changers = {}

        self.shapes = []
        self.shape_batch = pyglet.graphics.Batch()

    def move_x(self, shape, a):
        shape.x += a

    def move_y(self, shape, a):
        shape.y += a

    def change_x(self, shape, a):
        shape.x = a

    def change_y(self, shape, a):
        shape.y = a

    def change_x_velocity(self, shape, a):
        shape.x_velocity = a

    def change_y_velocity(self, shape, a):
        shape.y_velocity = a

    def change_gravity(self, a):
        self.gravity = a

    def spawn(self, shape):
        x, y = random.randint(100, self.window.width - 100), random.randint(100, self.window.height - 100)

        if shape == "circle":
            self.shapes.append(Circle(x, y, 10, color=arcade.color.WHITE, batch=self.shape_batch))

        elif shape == "rectangle":
            self.shapes.append(Rectangle(x, y, width=10, height=10, color=arcade.color.WHITE, batch=self.shape_batch))
            
        elif shape == "triangle":
            self.shapes.append(Triangle(x, y, x + 10, y, x + 5, y + 10, color=arcade.color.WHITE, batch=self.shape_batch))

    def create_rule_ui(self, rule_box: arcade.gui.UIBoxLayout, rule, rule_type, rule_num=1):
        rule_dict = IF_RULES[rule] if rule_type == "if" else DO_RULES[rule]

        ruleset_num = self.current_ruleset_num

        default_values = {VAR_NAMES[n]: VAR_DEFAULT[variable] for n, variable in enumerate(rule_dict["user_vars"])}
        description = rule_dict["description"].format_map(default_values)
        
        desc_label = rule_box.add(arcade.gui.UILabel(description if rule_type == "if" else f"THEN {description}", font_size=13, width=self.window.width * 0.25))
        self.rule_labels[f"{self.current_ruleset_num}_{rule_num}_desc"] = desc_label

        for n, variable_type in enumerate(rule_dict["user_vars"]):
            key = f"{self.current_ruleset_num}_{rule_num}_{variable_type}_{n}"

            self.rule_values[key] = default_values[VAR_NAMES[n]]

            label = rule_box.add(arcade.gui.UILabel(f'{VAR_NAMES[n]}: {default_values[VAR_NAMES[n]]}', font_size=11, width=self.window.width * 0.25, height=self.window.height / 25))
            self.rule_labels[key] = label

            if variable_type in ["variable", "size"]: 
                slider = rule_box.add(arcade.gui.UISlider(value=default_values[VAR_NAMES[n]], min_value=VAR_OPTIONS[variable_type][0], max_value=VAR_OPTIONS[variable_type][1], step=1, style=slider_style, width=self.window.width * 0.25, height=self.window.height / 25))
                slider._render_steps = lambda surface: None  
                slider.on_change = lambda event, variable_type=variable_type, rule=rule, rule_type=rule_type, ruleset_num=ruleset_num, rule_num=rule_num, n=n: self.change_rule_value(ruleset_num, rule_num, rule, rule_type, variable_type, n, event.new_value)
                self.rule_var_changers[key] = slider
            elif variable_type in ["shape_type", "target_type", "color"]:
                dropdown = rule_box.add(arcade.gui.UIDropdown(default=default_values[VAR_NAMES[n]], options=VAR_OPTIONS[variable_type], active_style=dropdown_style, primary_style=dropdown_style, dropdown_style=dropdown_style, width=self.window.width * 0.25, height=self.window.height / 25))
                dropdown.on_change = lambda event, variable_type=variable_type, rule=rule, rule_type=rule_type, ruleset_num=ruleset_num, rule_num=rule_num, n=n: self.change_rule_value(ruleset_num, rule_num, rule, rule_type, variable_type, n, event.new_value)
                self.rule_var_changers[key] = dropdown

    def add_ruleset(self, ruleset):
        rule_box = self.rules_box.add(arcade.gui.UIBoxLayout(space_between=5, align="left").with_background(color=arcade.color.DARK_SLATE_GRAY))

        if len(ruleset) == 2:
            self.rulesets[self.current_ruleset_num] = ruleset
            
            self.create_rule_ui(rule_box, ruleset[0], "if")
            self.create_rule_ui(rule_box, ruleset[1], "do")                
        
        else:
            self.rulesets[self.current_ruleset_num] = ruleset

            self.create_rule_ui(rule_box, ruleset[0], "if")
            rule_box.add(arcade.gui.UILabel(ruleset[1].upper(), font_size=14, width=self.window.width * 0.25))
            self.create_rule_ui(rule_box, ruleset[2], "if", 2)
            self.create_rule_ui(rule_box, ruleset[3], "do", 3)                

        self.rules_box.add(arcade.gui.UISpace(height=self.window.height / 50))
        
    def on_show_view(self):
        super().on_show_view()

        add_rule_button = self.rules_box.add(arcade.gui.UIFlatButton(text="Add rule", width=self.window.width * 0.25, height=self.window.height / 15, style=dropdown_style))
        add_rule_button.on_click = lambda event: self.add_rule()

        self.rules_box.add(arcade.gui.UISpace(height=self.window.height / 50))

        for _ in range(8):
            self.add_rule()

        self.triggered_events.append(["game_launch", {}])

    def add_rule(self):
        self.rulesets[self.current_ruleset_num] = generate_rule()
        self.add_ruleset(self.rulesets[self.current_ruleset_num])
        self.current_ruleset_num += 1

    def get_rule_values(self, ruleset_num, rule_num, rule_dict, event_args):
        args = [self.rule_values[f"{ruleset_num}_{rule_num}_{user_var}_{n}"] for n, user_var in enumerate(rule_dict["user_vars"])]

        return args + [event_args[var] for var in rule_dict.get("vars", []) if var in rule_dict["user_vars"]]

    def check_rule(self, ruleset_num, rule_num, rule_dict, event_args):
        return rule_dict["func"](*self.get_rule_values(ruleset_num, rule_num, rule_dict, event_args))
    
    def get_action_function(self, action_dict):
        ACTION_FUNCTION_DICT = {
            "global_action": {
                "spawn": self.spawn,
                "change_gravity": self.change_gravity
            },
            "shape_action": {
                "move_x": self.move_x,
                "move_y": self.move_y,
                "change_x": self.change_x,
                "change_y": self.change_y,
                "change_x_velocity": self.change_x_velocity,
                "change_y_velocity": self.change_y_velocity
            }
        }

        return ACTION_FUNCTION_DICT[action_dict["type"]][action_dict["name"]]

    def run_do_rule(self, ruleset_num, rule_num, rule_dict, event_args):
        self.get_action_function(rule_dict["action"])(*self.get_rule_values(ruleset_num, rule_num, rule_dict, event_args))

    def on_update(self, delta_time):
        self.triggered_events.append(["every_update", {}])

        while len(self.triggered_events) > 0:
            trigger, trigger_args = self.triggered_events.pop(0)

            for key, ruleset in self.rulesets.items():
                if len(ruleset) == 2:
                    if_rule_dict = IF_RULES[ruleset[0]]
                    do_rule_dict = DO_RULES[ruleset[1]]

                    if not if_rule_dict["trigger"] == trigger:
                        continue
                    
                    if if_rule_dict["trigger"] in ["every_update"]:
                        for shape in self.shapes:
                            event_args = trigger_args
                            
                            if not "event_shape_type" in trigger_args:
                                event_args.update({"event_shape_type": shape.shape_type, "shape_size": shape.size})

                            if self.check_rule(key, 0, if_rule_dict, event_args):
                                self.run_do_rule(key, 1, do_rule_dict, event_args)
                    else:
                        event_args = trigger_args
                        if self.check_rule(key, 0, if_rule_dict, event_args):
                            self.run_do_rule(key, 1, do_rule_dict, event_args)

                else:
                    if_rule_dicts = IF_RULES[ruleset[0]], IF_RULES[ruleset[2]]
                    do_rule_dict = DO_RULES[ruleset[3]]

                    if not (if_rule_dicts[0]["trigger"] == trigger and if_rule_dicts[0]["trigger"] == trigger):
                        continue

                    for shape in self.shapes if not "event_shape_type" in trigger_args else [shape]:
                        event_args = trigger_args
                        if not "event_shape_type" in trigger_args:
                            event_args.update({"event_shape_type": shape.shape_type, "shape_size": shape.size})

                        if ruleset[1] == "and":
                            if self.check_rule(key, 0, if_rule_dicts[0], event_args) and self.check_rule(key, 2, if_rule_dicts[1], event_args):
                                self.run_do_rule(key, 3, do_rule_dict, event_args)

                        elif ruleset[1] == "or":
                            if self.check_rule(key, 0, if_rule_dicts[0], event_args) or self.check_rule(key, 2, if_rule_dicts[1], event_args):
                                self.run_do_rule(key, 3, do_rule_dict, event_args)

        for shape in self.shapes:
            shape.update(self.gravity)

    def change_rule_value(self, ruleset_num, rule_num, rule, rule_type, variable_type, n, value):
        rule_dict = IF_RULES[rule] if rule_type == "if" else DO_RULES[rule]
        key = f"{ruleset_num}_{rule_num}_{variable_type}_{n}"
        
        self.rule_values[key] = value
        
        values = {}
        for i, variable in enumerate(rule_dict["user_vars"]):
            lookup_key = f"{ruleset_num}_{rule_num}_{variable}_{i}"
            values[VAR_NAMES[i]] = self.rule_values.get(lookup_key, VAR_DEFAULT[variable])
        
        description = rule_dict["description"].format_map(values)
        
        self.rule_labels[f"{ruleset_num}_{rule_num}_desc"].text = description if rule_type == "if" else f"THEN {description}"
        self.rule_labels[key].text = f'{VAR_NAMES[n]}: {value}'

    def on_draw(self):
        super().on_draw()

        self.shape_batch.draw()