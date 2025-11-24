import arcade, arcade.gui, pyglet, random, json

from utils.preload import SPRITE_TEXTURES
from utils.constants import slider_style, dropdown_style, VAR_NAMES, VAR_DEFAULT, VAR_OPTIONS, DO_RULES, IF_RULES, SHAPES, ALLOWED_INPUT

from game.rules import generate_ruleset
from game.sprites import BaseShape, Rectangle, Circle, Triangle

class Game(arcade.gui.UIView):
    def __init__(self, pypresence_client):
        super().__init__()

        self.pypresence_client = pypresence_client
        self.pypresence_client.update(state="Causing Chaos")

        with open("settings.json", "r") as file:
            self.settings = json.load(file)

        self.anchor = self.add_widget(arcade.gui.UIAnchorLayout(size_hint=(1, 1)))

        self.rules_box = arcade.gui.UIBoxLayout(align="center", size_hint=(0.25, 0.95)).with_background(color=arcade.color.DARK_GRAY)
        self.anchor.add(self.rules_box, anchor_x="right", anchor_y="center", align_x=-self.window.height * 0.025)

        self.sprites_box = self.anchor.add(arcade.gui.UIBoxLayout(size_hint=(0.15, 0.95), align="center", space_between=10).with_background(color=arcade.color.DARK_GRAY), anchor_x="left", anchor_y="center", align_x=self.window.height * 0.025)

        self.x_gravity = self.settings.get("default_x_gravity", 0)
        self.y_gravity = self.settings.get("default_y_gravity", 5)

        self.current_ruleset_num = 0
        self.current_ruleset_page = 0
        self.rulesets_per_page = 3
        self.rulesets = {}
        self.rule_values = {}
        self.triggered_events = []

        self.rule_labels = {}
        self.rule_var_changers = {}
        self.rule_boxes = {}

        self.shapes = []
        self.shape_batch = pyglet.graphics.Batch()

        self.rules_content_box = None
        self.nav_buttons_box = None


    def move_x(self, a, shape):
        if isinstance(shape, Triangle):
            shape.x += a
            shape.x2 += a
            shape.x3 += a
        else:
            shape.x += a

    def move_y(self, a, shape):
        if isinstance(shape, Triangle):
            shape.y += a
            shape.y2 += a
            shape.y3 += a
        else:
            shape.y += a

    def change_x(self, a, shape):
        if isinstance(shape, Triangle):
            offset_x2 = shape.x2 - shape.x
            offset_x3 = shape.x3 - shape.x
            
            shape.x = a
            shape.x2 = a + offset_x2
            shape.x3 = a + offset_x3
        else:
            shape.x = a
    
    def change_y(self, a, shape):
        if isinstance(shape, Triangle):
            offset_y2 = shape.y2 - shape.y
            offset_y3 = shape.y3 - shape.y
            
            shape.y = a
            shape.y2 = a + offset_y2
            shape.y3 = a + offset_y3
        else:
            shape.y = a

    def change_x_velocity(self, a, shape):
        shape.x_velocity = a
        self.triggered_events.append(["x_velocity_change", {"event_shape_type": shape.shape_type, "shape_size": shape.shape_size, "shape_x": shape.x, "shape_y": shape.y, "shape": shape, "shape_color": shape.shape_color}])

    def change_y_velocity(self, a, shape):
        shape.y_velocity = a
        self.triggered_events.append(["y_velocity_change", {"event_shape_type": shape.shape_type, "shape_size": shape.shape_size, "shape_x": shape.x, "shape_y": shape.y, "shape": shape, "shape_color": shape.shape_color}])

    def change_x_gravity(self, a):
        self.x_gravity = a
        self.triggered_events.append(["x_gravity_change", {}])

    def change_y_gravity(self, a):
        self.y_gravity = a
        self.triggered_events.append(["y_gravity_change", {}])

    def change_color(self, a, shape):
        shape.shape_color = getattr(arcade.color, a)
        self.triggered_events.append(["color_change", {"event_shape_type": shape.shape_type, "shape_size": shape.shape_size, "shape_x": shape.x, "shape_y": shape.y, "shape": shape, "shape_color": shape.shape_color}])

    def destroy(self, shape: BaseShape):
        self.triggered_events.append(["destroyed", {"event_shape_type": shape.shape_type}])
        if shape in self.shapes:
            self.shapes.remove(shape)
            shape.delete()

    def change_size(self, a, shape):
        if isinstance(shape, Circle):
            shape.radius = a
        elif isinstance(shape, Rectangle):
            shape.width = a
            shape.height = a
        elif isinstance(shape, Triangle):
            size = a - shape.shape_size

            shape.x += size
            shape.y += size
            
            shape.x2 += size
            shape.y2 += size

            shape.x3 += size
            shape.y3 += size

        self.triggered_events.append(["size_change", {"event_shape_type": shape.shape_type, "shape_size": shape.shape_size, "shape_x": shape.x, "shape_y": shape.y, "shape": shape, "shape_color": shape.shape_color}])

    def spawn(self, shape_type):
        x, y = random.randint(int(self.window.width * 0.15) + 50, int(self.window.width * 0.75) - 50), random.randint(100, self.window.height - 100)

        if shape_type == "circle":
            self.shapes.append(Circle(x, y, 10, color=arcade.color.WHITE, batch=self.shape_batch))

        elif shape_type == "rectangle":
            self.shapes.append(Rectangle(x, y, width=10, height=10, color=arcade.color.WHITE, batch=self.shape_batch))
            
        elif shape_type == "triangle":
            self.shapes.append(Triangle(x, y, x + 10, y, x + 5, y + 10, color=arcade.color.WHITE, batch=self.shape_batch))

        shape = self.shapes[-1]

        self.triggered_events.append(["spawn", {"event_shape_type": shape.shape_type, "shape_size": shape.shape_size, "shape_x": shape.x, "shape_y": shape.y, "shape": shape, "shape_color": shape.shape_color}])

    def morph(self, a, shape):
        old_shape_x, old_shape_y, old_shape_size, old_shape_color = shape.x, shape.y, shape.shape_size, shape.shape_color
        self.destroy(shape)

        if a == "circle":
            self.shapes.append(Circle(old_shape_x, old_shape_y, old_shape_size, color=getattr(arcade.color, old_shape_color), batch=self.shape_batch))

        elif a == "rectangle":
            self.shapes.append(Rectangle(old_shape_x, old_shape_y, width=old_shape_size, height=old_shape_size, color=getattr(arcade.color, old_shape_color), batch=self.shape_batch))
            
        elif a == "triangle":
            self.shapes.append(Triangle(old_shape_x, old_shape_y, old_shape_x + old_shape_size, old_shape_y, old_shape_x + int(old_shape_size / 2), old_shape_y + old_shape_size, color=getattr(arcade.color, old_shape_color), batch=self.shape_batch))

    def get_rule_defaults(self, rule_type):
        if rule_type == "if":
            return {
                    rule_key: (
                        rule_dict["description"].format_map({VAR_NAMES[n]: VAR_NAMES[n] for n, variable in enumerate(rule_dict["user_vars"])}), 
                        {VAR_NAMES[n]: VAR_DEFAULT[variable] for n, variable in enumerate(rule_dict["user_vars"])}
                    ) 
                    for rule_key, rule_dict in IF_RULES.items()
            }
        elif rule_type == "do":
            return {
                    rule_key: (
                        rule_dict["description"].format_map({VAR_NAMES[n]: VAR_NAMES[n] for n, variable in enumerate(rule_dict["user_vars"])}), 
                        {VAR_NAMES[n]: VAR_DEFAULT[variable] for n, variable in enumerate(rule_dict["user_vars"])}
                    ) 
                    for rule_key, rule_dict in DO_RULES.items()
            }
    def create_rule_ui(self, rule_box: arcade.gui.UIBoxLayout, rule, rule_type, rule_num=1):
        defaults = self.get_rule_defaults(rule_type)
        rule_dict = IF_RULES[rule] if rule_type == "if" else DO_RULES[rule]
        ruleset_num = self.current_ruleset_num
        default_values = defaults[rule][1]

        dropdown_options = [desc for desc, _ in defaults.values()]
        desc_label = rule_box.add(arcade.gui.UIDropdown(default=defaults[rule][0], options=dropdown_options, font_size=13, width=self.window.width * 0.225, active_style=dropdown_style, primary_style=dropdown_style, dropdown_style=dropdown_style))
        desc_label.on_change = lambda event, rule_type=rule_type, ruleset_num=ruleset_num, rule_num=rule_num: self.change_rule_type(ruleset_num, rule_num, rule_type, event.new_value)
        self.rule_labels[f"{self.current_ruleset_num}_{rule_num}_desc"] = desc_label

        for n, variable_type in enumerate(rule_dict["user_vars"]):
            key = f"{self.current_ruleset_num}_{rule_num}_{variable_type}_{n}"

            self.rule_values[key] = default_values[VAR_NAMES[n]]

            label = rule_box.add(arcade.gui.UILabel(f'{VAR_NAMES[n]}: {default_values[VAR_NAMES[n]]}', font_size=11, width=self.window.width * 0.225, height=self.window.height / 30))
            self.rule_labels[key] = label

            if variable_type in ["variable", "size"]: 
                slider = rule_box.add(arcade.gui.UISlider(value=default_values[VAR_NAMES[n]], min_value=VAR_OPTIONS[variable_type][0], max_value=VAR_OPTIONS[variable_type][1], step=1, style=slider_style, width=self.window.width * 0.225, height=self.window.height / 30))
                slider._render_steps = lambda surface: None  
                slider.on_change = lambda event, variable_type=variable_type, rule=rule, rule_type=rule_type, ruleset_num=ruleset_num, rule_num=rule_num, n=n: self.change_rule_value(ruleset_num, rule_num, rule, rule_type, variable_type, n, event.new_value)
                self.rule_var_changers[key] = slider

            else:
                dropdown = rule_box.add(arcade.gui.UIDropdown(default=default_values[VAR_NAMES[n]], options=VAR_OPTIONS[variable_type], active_style=dropdown_style, primary_style=dropdown_style, dropdown_style=dropdown_style, width=self.window.width * 0.225, height=self.window.height / 30))
                dropdown.on_change = lambda event, variable_type=variable_type, rule=rule, rule_type=rule_type, ruleset_num=ruleset_num, rule_num=rule_num, n=n: self.change_rule_value(ruleset_num, rule_num, rule, rule_type, variable_type, n, event.new_value)
                self.rule_var_changers[key] = dropdown

    def change_rule_type(self, ruleset_num, rule_num, rule_type, new_rule_text):
        defaults = self.get_rule_defaults(rule_type)
        new_rule_name = next(key for key, default_list in defaults.items() if default_list[0] == new_rule_text)
        
        ruleset = self.rulesets[ruleset_num]
        
        if len(ruleset) == 2:
            if rule_type == "if":
                ruleset[0] = new_rule_name
            else:
                ruleset[1] = new_rule_name
        else:
            if rule_type == "if":
                if rule_num == 1:
                    ruleset[0] = new_rule_name
                else:
                    ruleset[2] = new_rule_name
            else:
                ruleset[3] = new_rule_name

        self.rebuild_ruleset_ui(ruleset_num)

    def rebuild_ruleset_ui(self, ruleset_num):
        rule_box = self.rule_boxes[ruleset_num]
        
        keys_to_remove = [k for k in self.rule_labels.keys() if k.startswith(f"{ruleset_num}_")]
        for key in keys_to_remove:
            del self.rule_labels[key]
        
        keys_to_remove = [k for k in self.rule_var_changers.keys() if k.startswith(f"{ruleset_num}_")]
        for key in keys_to_remove:
            del self.rule_var_changers[key]
        
        keys_to_remove = [k for k in self.rule_values.keys() if k.startswith(f"{ruleset_num}_")]
        for key in keys_to_remove:
            del self.rule_values[key]
        
        rule_box.clear()
        
        ruleset = self.rulesets[ruleset_num]
        old_ruleset_num = self.current_ruleset_num
        self.current_ruleset_num = ruleset_num
        
        if len(ruleset) == 2:
            self.create_rule_ui(rule_box, ruleset[0], "if")
            self.create_rule_ui(rule_box, ruleset[1], "do", 2)
        else:
            self.create_rule_ui(rule_box, ruleset[0], "if")
            rule_box.add(arcade.gui.UILabel(ruleset[1].upper(), font_size=14, width=self.window.width * 0.25))
            self.create_rule_ui(rule_box, ruleset[2], "if", 2)
            self.create_rule_ui(rule_box, ruleset[3], "do", 3)
        
        self.current_ruleset_num = old_ruleset_num

    def add_ruleset(self, ruleset):
        rule_box = arcade.gui.UIBoxLayout(space_between=5, align="left").with_background(color=arcade.color.DARK_SLATE_GRAY)
        self.rule_boxes[self.current_ruleset_num] = rule_box

        if len(ruleset) == 2:
            self.rulesets[self.current_ruleset_num] = ruleset
            
            self.create_rule_ui(rule_box, ruleset[0], "if")
            self.create_rule_ui(rule_box, ruleset[1], "do", 2)                
        
        else:
            self.rulesets[self.current_ruleset_num] = ruleset

            self.create_rule_ui(rule_box, ruleset[0], "if")
            rule_box.add(arcade.gui.UILabel(ruleset[1].upper(), font_size=14, width=self.window.width * 0.25))
            self.create_rule_ui(rule_box, ruleset[2], "if", 2)
            self.create_rule_ui(rule_box, ruleset[3], "do", 3)

    def refresh_rules_display(self):
        self.rules_content_box.clear()

        sorted_keys = sorted(self.rule_boxes.keys())
        start_idx = self.current_ruleset_page * self.rulesets_per_page
        end_idx = start_idx + self.rulesets_per_page
        visible_keys = sorted_keys[start_idx:end_idx]

        for key in visible_keys:
            self.rules_content_box.add(self.rule_boxes[key])
            self.rules_content_box.add(arcade.gui.UISpace(height=self.window.height / 50))

    def next_page(self, event):
        sorted_keys = sorted(self.rule_boxes.keys())
        max_page = (len(sorted_keys) - 1) // self.rulesets_per_page
        if self.current_ruleset_page < max_page:
            self.current_ruleset_page += 1
            self.refresh_rules_display()

    def prev_page(self, event):
        if self.current_ruleset_page > 0:
            self.current_ruleset_page -= 1
            self.refresh_rules_display()

    def on_show_view(self):
        super().on_show_view()

        self.rules_box.add(arcade.gui.UILabel(text="Rules", font_size=20, text_color=arcade.color.BLACK))
        self.rules_box.add(arcade.gui.UISpace(height=self.window.height / 70, width=self.window.width * 0.25))

        add_simple_rule_button = self.rules_box.add(arcade.gui.UIFlatButton(text="Add Simple rule", width=self.window.width * 0.225, height=self.window.height / 25, style=dropdown_style))
        add_simple_rule_button.on_click = lambda event: self.add_rule("simple")

        self.rules_box.add(arcade.gui.UISpace(height=self.window.height / 85))

        add_advanced_rule_button = self.rules_box.add(arcade.gui.UIFlatButton(text="Add Advanced rule", width=self.window.width * 0.225, height=self.window.height / 25, style=dropdown_style))
        add_advanced_rule_button.on_click = lambda event: self.add_rule("advanced")

        self.rules_box.add(arcade.gui.UISpace(height=self.window.height / 85))

        self.rules_box.add(arcade.gui.UIFlatButton(text="Load from file\ncomming soon!", multiline=True, width=self.window.width * 0.225, height=self.window.height / 22.5, style=dropdown_style))
     
        self.rules_box.add(arcade.gui.UISpace(height=self.window.height / 85))

        self.rules_box.add(arcade.gui.UIFlatButton(text="Save to file\ncomming soon!", multiline=True, width=self.window.width * 0.225, height=self.window.height / 22.5, style=dropdown_style))

        self.rules_box.add(arcade.gui.UISpace(height=self.window.height / 70))

        self.nav_buttons_box = self.rules_box.add(arcade.gui.UIBoxLayout(vertical=False, space_between=10))
        prev_button = self.nav_buttons_box.add(arcade.gui.UIFlatButton(text="Previous", width=self.window.width * 0.1, height=self.window.height / 25, style=dropdown_style))
        prev_button.on_click = self.prev_page
        next_button = self.nav_buttons_box.add(arcade.gui.UIFlatButton(text="Next", width=self.window.width * 0.1, height=self.window.height / 25, style=dropdown_style))
        next_button.on_click = self.next_page

        self.rules_box.add(arcade.gui.UISpace(height=self.window.height / 70))

        self.rules_content_box = self.rules_box.add(arcade.gui.UIBoxLayout(align="center"))

        self.add_rule(None, ["on_left_click", "spawn"])

        self.refresh_rules_display()

        self.sprites_box.add(arcade.gui.UILabel(text="Sprites", font_size=24, text_color=arcade.color.BLACK))
        self.sprites_box.add(arcade.gui.UISpace(height=self.window.height / 50))

        for shape in SHAPES:
            self.sprites_box.add(arcade.gui.UILabel(text=shape, font_size=16, text_color=arcade.color.BLACK))
            self.sprites_box.add(arcade.gui.UIImage(texture=SPRITE_TEXTURES[shape], width=self.window.width / 15, height=self.window.width / 15))

        self.sprites_box.add(arcade.gui.UISpace(height=self.window.height / 50))

        self.sprites_box.add(arcade.gui.UIFlatButton(text="Load sprite\ncomming soon!", multiline=True, style=dropdown_style, width=self.window.width * 0.125, height=self.window.height / 10))

        self.triggered_events.append(["game_launch", {}])

    def add_rule(self, ruleset_type=None, force=None):
        self.rulesets[self.current_ruleset_num] = generate_ruleset(ruleset_type) if not force else force
        self.add_ruleset(self.rulesets[self.current_ruleset_num])
        self.current_ruleset_num += 1
        if self.rules_content_box:
            self.refresh_rules_display()

    def get_rule_values(self, ruleset_num, rule_num, rule_dict, event_args):
        args = [self.rule_values[f"{ruleset_num}_{rule_num}_{user_var}_{n}"] for n, user_var in enumerate(rule_dict["user_vars"])]

        return args + [event_args[var] for var in rule_dict.get("vars", []) if not var in rule_dict["user_vars"]]

    def check_rule(self, ruleset_num, rule_num, rule_dict, event_args):
        return rule_dict["func"](*self.get_rule_values(ruleset_num, rule_num, rule_dict, event_args))
    
    def get_action_function(self, action_dict):
        ACTION_FUNCTION_DICT = {
            "global_action": {
                "spawn": self.spawn,
                "change_x_gravity": self.change_x_gravity,
                "change_y_gravity": self.change_y_gravity
            },
            "shape_action": {
                "move_x": self.move_x,
                "move_y": self.move_y,
                "change_x": self.change_x,
                "change_y": self.change_y,
                "change_x_velocity": self.change_x_velocity,
                "change_y_velocity": self.change_y_velocity,
                "change_color": self.change_color,
                "change_size": self.change_size,
                "destroy": self.destroy,
                "morph": self.morph
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
                    
                    if do_rule_dict["action"]["type"] == "shape_action":
                        for shape in self.shapes:                            
                            event_args = trigger_args.copy()
                            if not "event_shape_type" in trigger_args:
                                event_args.update({"event_shape_type": shape.shape_type, "shape_size": shape.shape_size, "shape_x": shape.x, "shape_y": shape.y, "shape": shape, "shape_color": shape.shape_color})

                            if self.check_rule(key, 1, if_rule_dict, event_args):
                                self.run_do_rule(key, 2, do_rule_dict, event_args)
                    else:
                        event_args = trigger_args.copy()
                        if self.check_rule(key, 1, if_rule_dict, event_args):
                            self.run_do_rule(key, 2, do_rule_dict, event_args)
                    
                else:
                    if_rule_dicts = IF_RULES[ruleset[0]], IF_RULES[ruleset[2]]
                    do_rule_dict = DO_RULES[ruleset[3]]

                    if not (if_rule_dicts[0]["trigger"] == trigger and if_rule_dicts[0]["trigger"] == trigger):
                        continue

                    if do_rule_dict["action"]["type"] == "shape_action":
                        for shape in self.shapes:
                            event_args = trigger_args
                            
                            if not "event_shape_type" in trigger_args:
                                event_args.update({"event_shape_type": shape.shape_type, "shape_size": shape.shape_size, "shape_x": shape.x, "shape_y": shape.y, "shape": shape, "shape_color": shape.shape_color})

                            if ruleset[1] == "and":
                                if self.check_rule(key, 1, if_rule_dicts[0], event_args) and self.check_rule(key, 2, if_rule_dicts[1], event_args):
                                    self.run_do_rule(key, 3, do_rule_dict, event_args)

                            elif ruleset[1] == "or":
                                if self.check_rule(key, 1, if_rule_dicts[0], event_args) or self.check_rule(key, 2, if_rule_dicts[1], event_args):
                                    self.run_do_rule(key, 3, do_rule_dict, event_args)
                    else:
                        event_args = trigger_args
                        if ruleset[1] == "and":
                            if self.check_rule(key, 1, if_rule_dicts[0], event_args) and self.check_rule(key, 2, if_rule_dicts[1], event_args):
                                self.run_do_rule(key, 3, do_rule_dict, event_args)

                        elif ruleset[1] == "or":
                            if self.check_rule(key, 1, if_rule_dicts[0], event_args) or self.check_rule(key, 2, if_rule_dicts[1], event_args):
                                self.run_do_rule(key, 3, do_rule_dict, event_args)

        for shape in self.shapes:
            for shape_b in self.shapes:
                if shape.check_collision(shape_b):
                    self.triggered_events.append(["collision", {"event_a_type": shape.shape_type, "event_b_type": shape.shape_type, "shape_size": shape.shape_size, "shape_x": shape.x, "shape_y": shape.y, "shape": shape, "shape_color": shape.color}])

            shape.update(self.x_gravity, self.y_gravity)

            if shape.x < 0 or shape.x > self.window.width or shape.y < 0 or shape.y > self.window.height:
                self.destroy(shape)

        if len(self.shapes) > self.settings.get("max_shapes", 120):
            for shape in self.shapes[:-self.settings.get("max_shapes", 120)]:
                self.destroy(shape)

    def change_rule_value(self, ruleset_num, rule_num, rule, rule_type, variable_type, n, value):
        rule_dict = IF_RULES[rule] if rule_type == "if" else DO_RULES[rule]
        key = f"{ruleset_num}_{rule_num}_{variable_type}_{n}"
        
        self.rule_values[key] = value
        
        values = {}
        for i, variable in enumerate(rule_dict["user_vars"]):
            lookup_key = f"{ruleset_num}_{rule_num}_{variable}_{i}"
            values[VAR_NAMES[i]] = self.rule_values.get(lookup_key, VAR_DEFAULT[variable])
        
        description = rule_dict["description"].format_map(values)
        
        self.rule_labels[f"{ruleset_num}_{rule_num}_desc"].text = description
        self.rule_labels[key].text = f'{VAR_NAMES[n]}: {value}'

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            self.main_exit()
        elif symbol in [ord(key) for key in ALLOWED_INPUT]:
            self.triggered_events.append(["on_input", {"event_key": chr(symbol)}])

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.triggered_events.append(["on_left_click", {}])
        elif button == arcade.MOUSE_BUTTON_RIGHT:
            self.triggered_events.append(["on_right_click", {}])

    def on_mouse_motion(self, x, y, button, modifiers):
        self.triggered_events.append(["on_mouse_move", {}])

    def main_exit(self):
        from menus.main import Main
        self.window.show_view(Main(self.pypresence_client))

    def on_draw(self):
        self.window.clear()
        self.shape_batch.draw()
        self.ui.draw()