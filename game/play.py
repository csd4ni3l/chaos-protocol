import arcade, arcade.gui, pyglet, random

from utils.constants import slider_style, dropdown_style, VAR_NAMES, VAR_DEFAULT, DEFAULT_GRAVITY, VAR_OPTIONS

from game.rules import generate_rules, generate_rule
from game.sprites import *

class Game(arcade.gui.UIView):
    def __init__(self, pypresence_client):
        super().__init__()

        self.pypresence_client = pypresence_client
        self.pypresence_client.update(state="Causing Chaos")

        self.anchor = self.add_widget(arcade.gui.UIAnchorLayout(size_hint=(1, 1)))
        self.rules_box = self.anchor.add(arcade.gui.UIBoxLayout(align="left", size_hint=(0.25, 1)).with_background(color=arcade.color.DARK_GRAY), anchor_x="right", anchor_y="bottom")

        self.gravity = DEFAULT_GRAVITY

        self.rules = generate_rules(1)

        self.rule_labels = {}
        self.rule_sliders = {}

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

    def get_default_values(self, variable_list):
        return {VAR_NAMES[n]: VAR_DEFAULT[variable] for n, variable in enumerate(variable_list)}

    def spawn(self, shape):
        x, y = random.randint(100, self.window.width - 100), random.randint(100, self.window.height - 100)

        if shape == "circle":
            self.shapes.append(Circle(x, y, 10, color=arcade.color.WHITE, batch=self.shape_batch))

        elif shape == "rectangle":
            self.shapes.append(Rectangle(x, y, width=10, height=10, color=arcade.color.WHITE, batch=self.shape_batch))
            
        elif shape == "triangle":
            self.shapes.append(Triangle(x, y, x + 10, y, x + 5, y + 10, color=arcade.color.WHITE, batch=self.shape_batch))

    def create_rule_ui(self, rule_box, rule, rule_type="if"):
        default_values = {VAR_NAMES[n]: VAR_DEFAULT[variable] for n, variable in enumerate(rule["user_vars"])}
        description = rule["description"].format_map(default_values)
        
        rule_box.add(arcade.gui.UILabel(description if rule_type == "if" else f"THEN {description}", font_size=13, width=self.window.width * 0.25))

        for n, variable in enumerate(rule["user_vars"]):
            rule_box.add(arcade.gui.UILabel(f'{VAR_NAMES[n]}: {default_values[VAR_NAMES[n]]}', font_size=11, width=self.window.width * 0.25, height=self.window.height / 25))

            if variable in ["variable", "size"]: 
                slider = rule_box.add(arcade.gui.UISlider(value=default_values[VAR_NAMES[n]], min_value=VAR_OPTIONS[variable][0], max_value=VAR_OPTIONS[variable][1], step=1, style=slider_style, width=self.window.width * 0.25, height=self.window.height / 25))
                slider._render_steps = lambda surface: None
            elif variable in ["shape_type", "target_type", "color"]:
                dropdown = rule_box.add(arcade.gui.UIDropdown(default=default_values[VAR_NAMES[n]], options=VAR_OPTIONS[variable], active_style=dropdown_style, primary_style=dropdown_style, dropdown_style=dropdown_style, width=self.window.width * 0.25, height=self.window.height / 25))
    def create_ruleset_ui(self, ruleset):
        rule_box = self.rules_box.add(arcade.gui.UIBoxLayout(space_between=5, align="left").with_background(color=arcade.color.DARK_SLATE_GRAY))

        if len(ruleset) == 2:
            self.create_rule_ui(rule_box, ruleset[0])
            self.create_rule_ui(rule_box, ruleset[1], "do")                
        
        else:
            self.create_rule_ui(rule_box, ruleset[0], "if")

            rule_box.add(arcade.gui.UILabel(ruleset[1].upper(), font_size=14, width=self.window.width * 0.25))

            self.create_rule_ui(rule_box, ruleset[2], "if")

            self.create_rule_ui(rule_box, ruleset[3], "do")                

        self.rules_box.add(arcade.gui.UISpace(height=self.window.height / 50))

    def on_show_view(self):
        super().on_show_view()

        add_rule_button = self.rules_box.add(arcade.gui.UIFlatButton(text="Add rule", width=self.window.width * 0.25, height=self.window.height / 15, style=dropdown_style))
        add_rule_button.on_click = lambda event: self.add_rule()

        self.rules_box.add(arcade.gui.UISpace(height=self.window.height / 50))

        for ruleset in self.rules:
            self.create_ruleset_ui(ruleset)

    def add_rule(self):
        self.rules.append(generate_rule())
        self.create_ruleset_ui(self.rules[-1])

    def on_draw(self):
        super().on_draw()

        self.shape_batch.draw()