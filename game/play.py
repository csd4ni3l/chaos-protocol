import arcade, arcade.gui, pyglet, random, json

from dataclasses import asdict

from utils.preload import SPRITE_TEXTURES, button_texture, button_hovered_texture
from utils.constants import button_style, DO_RULES, IF_RULES, SPRITES, ALLOWED_INPUT

from game.rules import RuleUI, Block, VarBlock
from game.sprites import BaseShape, Rectangle, Circle, Triangle, TexturedRectangle
from game.file_manager import FileManager

class Game(arcade.gui.UIView):
    def __init__(self, pypresence_client):
        super().__init__()

        self.pypresence_client = pypresence_client
        self.pypresence_client.update(state="Causing Chaos")

        with open("settings.json", "r") as file:
            self.settings = json.load(file)

        self.anchor = self.add_widget(arcade.gui.UIAnchorLayout(size_hint=(1, 1)))

        self.rules_box = RuleUI(self.window)

        self.file_manager = FileManager(self.window.width * 0.95, self.window.height * 0.875, (0.95, 0.875), [".json"]).with_border()

        self.ui_selector_box = self.anchor.add(arcade.gui.UIBoxLayout(vertical=False, space_between=self.window.width / 100), anchor_x="left", anchor_y="bottom", align_y=5, align_x=self.window.width / 100)
        self.add_ui_selector("Simulation", lambda event: self.simulation())
        self.add_ui_selector("Rules", lambda event: self.rules())
        self.add_ui_selector("Sprites", lambda event: self.sprites())
        self.add_ui_selector("Import", lambda event: self.import_file())
        self.add_ui_selector("Export", lambda event: self.export_file())
        self.mode = "simulation"

        self.x_gravity = self.settings.get("default_x_gravity", 0)
        self.y_gravity = self.settings.get("default_y_gravity", 5)
        self.triggered_events = []

        self.rulesets = self.rules_box.rulesets

        self.sprite_add_filemanager = FileManager(self.window.width * 0.9, self.window.height * 0.75, (0.9, 0.75), [".png", ".jpg", ".jpeg", ".bmp", ".gif"])
        self.sprite_add_ui = arcade.gui.UIBoxLayout(size_hint=(0.95, 0.9), space_between=10)
        self.sprite_add_ui.add(arcade.gui.UILabel(text="Add Sprite", font_size=24, text_color=arcade.color.WHITE))
        
        self.sprite_add_ui.add(arcade.gui.UILabel(text="Sprite Name:", font_size=18, text_color=arcade.color.WHITE))
        self.sprite_name_input = self.sprite_add_ui.add(arcade.gui.UIInputText(width=self.window.width * 0.4, height=self.window.height * 0.05).with_border(color=arcade.color.WHITE))

        self.sprite_add_ui.add(arcade.gui.UILabel(text="Select a texture for the sprite:", font_size=18, text_color=arcade.color.WHITE))
        self.sprite_add_ui.add(self.sprite_add_filemanager, anchor_x="center", anchor_y="bottom", align_y=25)

        self.sprites_ui = arcade.gui.UIAnchorLayout(size_hint=(0.95, 0.9))
        self.sprite_types = SPRITES

        self.shapes = []
        self.shape_batch = pyglet.graphics.Batch()

        self.simulation()

    def add_ui_selector(self, button_text, on_click):
        button = self.ui_selector_box.add(arcade.gui.UITextureButton(text=button_text, width=self.window.width / 5.5, height=self.window.height / 15, style=button_style, texture=button_texture, texture_hovered=button_hovered_texture))
        button.on_click = on_click

    def move_x(self, a, shape):
        a = float(a)
        if isinstance(shape, Triangle):
            shape.x += a
            shape.x2 += a
            shape.x3 += a
        else:
            shape.x += a

    def move_y(self, a, shape):
        a = float(a)
        if isinstance(shape, Triangle):
            shape.y += a
            shape.y2 += a
            shape.y3 += a
        else:
            shape.y += a

    def change_x(self, a, shape):
        a = float(a)
        if isinstance(shape, Triangle):
            offset_x2 = shape.x2 - shape.x
            offset_x3 = shape.x3 - shape.x
            
            shape.x = a
            shape.x2 = a + offset_x2
            shape.x3 = a + offset_x3
        else:
            shape.x = a
    
    def change_y(self, a, shape):
        a = float(a)
        if isinstance(shape, Triangle):
            offset_y2 = shape.y2 - shape.y
            offset_y3 = shape.y3 - shape.y
            
            shape.y = a
            shape.y2 = a + offset_y2
            shape.y3 = a + offset_y3
        else:
            shape.y = a

    def change_x_velocity(self, a, shape):
        a = float(a)
        shape.x_velocity = a
        self.triggered_events.append(["x_velocity_change", {"event_shape_type": shape.shape_type, "shape_size": shape.shape_size, "shape_x": shape.x, "shape_y": shape.y, "shape": shape, "shape_color": shape.shape_color}])

    def change_y_velocity(self, a, shape):
        a = float(a)
        shape.y_velocity = a
        self.triggered_events.append(["y_velocity_change", {"event_shape_type": shape.shape_type, "shape_size": shape.shape_size, "shape_x": shape.x, "shape_y": shape.y, "shape": shape, "shape_color": shape.shape_color}])

    def change_x_gravity(self, a):
        a = float(a)
        self.x_gravity = a
        self.triggered_events.append(["x_gravity_change", {}])

    def change_y_gravity(self, a):
        a = float(a)
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
        a = float(a)
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
        
        else:
            self.shapes.append(TexturedRectangle(shape_type, img=SPRITE_TEXTURES.get(shape_type, SPRITE_TEXTURES["rectangle"]), x=x, y=y, batch=self.shape_batch))

        shape = self.shapes[-1]

        self.triggered_events.append(["spawn", {"event_shape_type": shape.shape_type, "shape_size": shape.shape_size, "shape_x": shape.x, "shape_y": shape.y, "shape": shape, "shape_color": shape.shape_color}])

    def add_sprite(self):
        self.disable_previous()

        self.mode = "sprite_add"

        self.anchor.add(self.sprite_add_ui, anchor_x="center", anchor_y="center")

        def check_selection(delta_time):
            if self.sprite_add_filemanager.submitted_content:
                texture = arcade.load_texture(self.sprite_add_filemanager.submitted_content)

                SPRITE_TEXTURES[self.sprite_name_input.text] = texture
                SPRITES[self.sprite_name_input.text] = self.sprite_add_filemanager.submitted_content

                self.sprites_grid.clear()

                for n, shape in enumerate(SPRITES):
                    row, col = n % 8, n // 8
                    box = self.sprites_grid.add(arcade.gui.UIBoxLayout(), row=row, column=col)
                    box.add(arcade.gui.UILabel(text=shape, font_size=16, text_color=arcade.color.WHITE))
                    box.add(arcade.gui.UIImage(texture=SPRITE_TEXTURES[shape], width=self.window.width / 15, height=self.window.width / 15))

                self.anchor.remove(self.sprite_add_ui)
                arcade.unschedule(check_selection)

        arcade.schedule(check_selection, 0.1)

    def on_show_view(self):
        super().on_show_view()

        self.sprites_ui.add(arcade.gui.UILabel(text="Sprites", font_size=24, text_color=arcade.color.WHITE), anchor_x="center", anchor_y="top")

        self.sprites_grid = self.sprites_ui.add(arcade.gui.UIGridLayout(columns=8, row_count=8, align="left", vertical_spacing=10, horizontal_spacing=10, size_hint=(0.95, 0.85), width=self.window.width * 0.95, height=self.window.height * 0.85), anchor_x="center", anchor_y="center")

        for n, shape in enumerate(SPRITES):
            row, col = n % 8, n // 8
            box = self.sprites_grid.add(arcade.gui.UIBoxLayout(), row=row, column=col)
            box.add(arcade.gui.UILabel(text=shape, font_size=16, text_color=arcade.color.WHITE))
            box.add(arcade.gui.UIImage(texture=SPRITE_TEXTURES[shape], width=self.window.width / 15, height=self.window.width / 15))

        add_sprite_button = self.sprites_ui.add(arcade.gui.UITextureButton(text="Add Sprite", width=self.window.width / 2, height=self.window.height / 10, texture=button_texture, texture_hovered=button_hovered_texture, style=button_style), anchor_x="center", anchor_y="bottom", align_y=10)
        add_sprite_button.on_click = lambda event: self.add_sprite()

        self.triggered_events.append(["start", {}])

    def get_vars(self, rule_dict, vars, event_args):
        args = [vars[n].value for n in range(len(rule_dict["user_vars"]))]

        return args + [event_args[var] for var in rule_dict.get("vars", []) if not var in rule_dict["user_vars"]]

    def check_rule(self, rule_dict, vars, event_args):
        return rule_dict["func"](*self.get_vars(rule_dict, vars, event_args))
    
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
                "destroy": self.destroy
            }
        }

        return ACTION_FUNCTION_DICT[action_dict["type"]][action_dict["name"]]

    def run_do_rule(self, rule_dict, vars, event_args):
        self.get_action_function(rule_dict["action"])(*self.get_vars(rule_dict, vars, event_args))

    def recursive_execute_rule(self, rule, trigger_args):
        for child_rule in rule.children:
            child_rule_type = child_rule.rule_type

            if child_rule_type == "for": # TODO: Extend this when i add more FOR loop types
                if child_rule.rule == "every_shape":
                    for shape in self.shapes:
                        event_args = trigger_args.copy()
                        event_args.update({"event_shape_type": shape.shape_type, "shape_size": shape.shape_size, "shape_x": shape.x, "shape_y": shape.y, "shape": shape, "shape_color": shape.shape_color})
                        
                        self.recursive_execute_rule(child_rule, event_args)
                
            elif child_rule_type == "if":
                if self.check_rule(IF_RULES[child_rule.rule], child_rule.vars, trigger_args):
                    self.recursive_execute_rule(child_rule, trigger_args)

            elif child_rule_type == "do":
                self.run_do_rule(DO_RULES[child_rule.rule], child_rule.vars, trigger_args)

    def get_max_rule_num(self):
        max_num = -1
        
        def recurse(block: Block):
            nonlocal max_num
            max_num = max(max_num, block.rule_num)
            for child in block.children:
                recurse(child)
        
        for block in self.rulesets.values():
            recurse(block)
        
        return max_num

    def on_update(self, delta_time):
        if self.mode == "import" and self.file_manager.submitted_content:
            with open(self.file_manager.submitted_content, "r") as file:
                data = json.load(file)

            self.triggered_events = []
            self.rulesets = {}

            if not data:
                self.add_widget(arcade.gui.UIMessageBox(message_text="Invalid file. Could not import rules.", width=self.window.width * 0.5, height=self.window.height * 0.25))
                return
            
            for rule_num, ruleset in data["rulesets"].items():
                kwargs = ruleset
                kwargs["children"] = [Block(**child) for child in ruleset["children"]]
                kwargs["vars"] = [VarBlock(**var) for var in ruleset["vars"]]
                block = Block(**kwargs)
                self.rulesets[rule_num] = block

            self.sprite_types = data.get("sprites", SPRITES)
            for sprite_name, sprite_path in self.sprite_types.items():
                if not sprite_name in SPRITE_TEXTURES:
                    SPRITE_TEXTURES[sprite_name] = arcade.load_texture(sprite_path)
            
            self.rules_box.rulesets = self.rulesets
            self.rules_box.current_rule_num = self.get_max_rule_num() + 1
            self.rules_box.block_renderer.refresh()

            self.rules()

        if self.mode == "export" and self.file_manager.submitted_content:
            with open(self.file_manager.submitted_content, "w") as file:
                file.write(json.dumps(
                    {
                        "rules": {
                            rule_num: asdict(block) for rule_num, block in self.rulesets.items()
                        },
                        "sprites": self.sprite_types
                    
                    },
                indent=4))

            self.add_widget(arcade.gui.UIMessageBox(message_text="Rules and Sprites exported successfully!", width=self.window.width * 0.5, height=self.window.height * 0.25))

        if not self.mode == "simulation":
            return

        self.triggered_events.append(["every_update", {}])

        while len(self.triggered_events) > 0:
            trigger, trigger_args = self.triggered_events.pop(0)

            for rule_num, rule in self.rulesets.items():
                if not rule.rule_type == "trigger" or not trigger == rule.rule:
                    continue
                
                self.recursive_execute_rule(rule, trigger_args)

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

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            self.main_exit()
        elif self.mode == "simulation" and symbol in [ord(key) if len(key) == 1 else getattr(arcade.key, key.upper()) for key in ALLOWED_INPUT]:
            self.triggered_events.append(["on_input", {"event_key": chr(symbol)}])

    def on_mouse_press(self, x, y, button, modifiers):
        if not self.mode == "simulation":
            return
        
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.triggered_events.append(["on_left_click", {}])
        elif self.mode == "simulation" and button == arcade.MOUSE_BUTTON_RIGHT:
            self.triggered_events.append(["on_right_click", {}])

    def on_mouse_motion(self, x, y, button, modifiers):
        if not self.mode == "simulation":
            return

        self.triggered_events.append(["on_mouse_move", {}])

    def on_mouse_drag(self, x, y, dx, dy, _buttons, _modifiers):
        if self.mode == "rules" and arcade.MOUSE_BUTTON_MIDDLE == _buttons:
            self.rules_box.camera.position -= (dx, dy)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if self.mode == "rules":
            self.rules_box.camera.zoom *= 1 + scroll_y * 0.1

    def disable_previous(self):
        if self.mode in ["import", "export"]:
            self.anchor.remove(self.file_manager)
        elif self.mode == "rules":
            self.anchor.remove(self.rules_box)
        elif self.mode == "sprites":
            self.anchor.remove(self.sprites_ui)
        elif self.mode == "sprite_add":
            self.anchor.remove(self.sprite_add_ui)

        self.anchor.trigger_full_render()

    def rules(self):
        self.disable_previous()

        self.mode = "rules"

        self.anchor.add(self.rules_box, anchor_x="center", anchor_y="top")

    def export_file(self):
        self.disable_previous()
        
        self.mode = "export"

        self.file_manager.change_mode("export")
        self.anchor.add(self.file_manager, anchor_x="center", anchor_y="top", align_y=-self.window.height * 0.025)

    def import_file(self):
        self.disable_previous()

        self.mode = "import"

        self.file_manager.change_mode("import")
        self.anchor.add(self.file_manager, anchor_x="center", anchor_y="top", align_y=-self.window.height * 0.025)

    def sprites(self):
        self.disable_previous()

        self.mode = "sprites"

        self.anchor.add(self.sprites_ui, anchor_x="center", anchor_y="top")

    def simulation(self):
        self.disable_previous()
        self.x_gravity = self.settings.get("default_x_gravity", 0)
        self.y_gravity = self.settings.get("default_y_gravity", 5)
        self.triggered_events = []
        self.rulesets = self.rules_box.rulesets
        self.mode = "simulation"

    def main_exit(self):
        from menus.main import Main
        self.window.show_view(Main(self.pypresence_client))

    def on_draw(self):
        self.window.clear()
        
        if self.mode == "simulation":
            self.shape_batch.draw()
        elif self.mode == "rules":
            with self.rules_box.camera.activate():
                self.rules_box.draw()
                
            self.rules_box.draw_unproject()
   
        self.ui.draw()