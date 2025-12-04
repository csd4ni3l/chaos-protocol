from utils.constants import (
    DO_RULES,
    IF_RULES,
    LOGICAL_OPERATORS,
    NON_COMPATIBLE_WHEN,
    NON_COMPATIBLE_DO_WHEN,
    VAR_NAMES,
    VAR_DEFAULT,
    VAR_OPTIONS,
    dropdown_style,
    slider_style,
    button_style,
)
from utils.preload import button_texture, button_hovered_texture
import arcade, arcade.gui, random

IF_KEYS = tuple(IF_RULES.keys())
DO_KEYS = tuple(DO_RULES.keys())

BAD_WHEN = {tuple(sorted(pair)) for pair in NON_COMPATIBLE_WHEN}
BAD_DO_WHEN = {tuple(pair) for pair in NON_COMPATIBLE_DO_WHEN}

def generate_if_rule():
    return random.choice(IF_KEYS)

def generate_do_rule():
    return random.choice(DO_KEYS)

def generate_comparison():
    return random.choice(LOGICAL_OPERATORS)

def per_widget_height(height, widget_count):
    return height // widget_count

def cubic_bezier_point(p0, p1, p2, p3, t):
    u = 1 - t
    x = (u ** 3) * p0[0] + 3 * (u ** 2) * t * p1[0] + 3 * u * (t ** 2) * p2[0] + (t ** 3) * p3[0]
    y = (u ** 3) * p0[1] + 3 * (u ** 2) * t * p1[1] + 3 * u * (t ** 2) * p2[1] + (t ** 3) * p3[1]
    return x, y

def cubic_bezier_points(p0, p1, p2, p3, segments=40):
    return [cubic_bezier_point(p0, p1, p2, p3, i / segments) for i in range(segments + 1)]

def connection_between(p0, p3):
    dx = p3[0] - p0[0]
    offset = max(60, abs(dx) * 0.45)
    c1 = (p0[0] + offset, p0[1])
    c2 = (p3[0] - offset, p3[1])

    return cubic_bezier_points(p0, c1, c2, p3, segments=100)

def get_rule_defaults(rule_type):
    if rule_type == "if":
        return {
            rule_key: (
                rule_dict["description"].format_map(
                    {
                        VAR_NAMES[n]: VAR_NAMES[n]
                        for n, variable in enumerate(rule_dict["user_vars"])
                    }
                ),
                {
                    VAR_NAMES[n]: VAR_DEFAULT[variable]
                    for n, variable in enumerate(rule_dict["user_vars"])
                },
            )
            for rule_key, rule_dict in IF_RULES.items()
        }

    elif rule_type == "do":
        return {
            rule_key: (
                rule_dict["description"].format_map(
                    {
                        VAR_NAMES[n]: VAR_NAMES[n]
                        for n, variable in enumerate(rule_dict["user_vars"])
                    }
                ),
                {
                    VAR_NAMES[n]: VAR_DEFAULT[variable]
                    for n, variable in enumerate(rule_dict["user_vars"])
                },
            )
            for rule_key, rule_dict in DO_RULES.items()
        }


class ComparisonBox(arcade.gui.UITextureButton):
    def __init__(self, x, y, comparison, rule_num):
        super().__init__(
            x=x,
            y=y,
            text=comparison,
            style=button_style,
            texture=button_texture,
            texture_hovered=button_hovered_texture,
        )

        self.rule_num = rule_num

class RuleBox(arcade.gui.UIBoxLayout):
    def __init__(self, x, y, width, height, rule_num, rule_type, rule):
        super().__init__(space_between=10, x=x, y=y, width=width, height=height)

        self.rule = rule
        self.rule_num = rule_num
        self.rule_type = rule_type
        self.rule_dict = (
            IF_RULES[self.rule] if self.rule_type == "if" else DO_RULES[self.rule]
        )
        self.defaults = get_rule_defaults(self.rule_type)
        self.rule_values = {}
        self.var_labels = {}
        self.var_changers = {}

        self.per_widget_height = per_widget_height(
            self.height, 2 + 2 * len(self.rule_dict["user_vars"])
        )

        self.init_ui()

    def init_ui(self):
        dropdown_options = [desc for desc, _ in self.defaults.values()]
        self.desc_label = self.add(
            arcade.gui.UIDropdown(
                default=self.defaults[self.rule][0],
                options=dropdown_options,
                font_size=13,
                active_style=dropdown_style,
                primary_style=dropdown_style,
                dropdown_style=dropdown_style,
                width=self.width,
            )
        )
        # self.desc_label.on_change = lambda event, rule_type=self.rule_type, rule_num=self.rule_num: self.change_rule_type(rule_num, rule_type, event.new_value)

        if self.rule_type == "do":
            self.add_connection_button()

        for n, variable_type in enumerate(self.rule_dict["user_vars"]):
            key = f"{variable_type}_{n}"

            defaults = get_rule_defaults(self.rule_type)
            default_values = defaults[self.rule][1]
            self.rule_values[key] = default_values[VAR_NAMES[n]]

            self.var_labels[key] = self.add(
                arcade.gui.UILabel(
                    f"{VAR_NAMES[n]}: {self.rule_values[key]}",
                    font_size=11,
                    text_color=arcade.color.WHITE,
                    width=self.width,
                    height=self.per_widget_height,
                )
            )

            if variable_type in ["variable", "size"]:
                slider = self.add(
                    arcade.gui.UISlider(
                        value=self.rule_values[key],
                        min_value=VAR_OPTIONS[variable_type][0],
                        max_value=VAR_OPTIONS[variable_type][1],
                        step=1,
                        style=slider_style,
                        width=self.width,
                        height=self.per_widget_height,
                    )
                )
                slider._render_steps = lambda surface: None
                slider.on_change = (
                    lambda event,
                    variable_type=variable_type,
                    n=n: self.change_var_value(variable_type, n, event.new_value)
                )

                self.var_changers[key] = slider

            else:
                dropdown = self.add(
                    arcade.gui.UIDropdown(
                        default=self.rule_values[key],
                        options=VAR_OPTIONS[variable_type],
                        active_style=dropdown_style,
                        primary_style=dropdown_style,
                        dropdown_style=dropdown_style,
                        width=self.width,
                        height=self.per_widget_height,
                    )
                )
                dropdown.on_change = (
                    lambda event,
                    variable_type=variable_type,
                    n=n: self.change_var_value(variable_type, n, event.new_value)
                )

                self.var_changers[key] = dropdown

        if self.rule_type == "if":
            self.add_connection_button()

    def add_connection_button(self):
        self.connection_button = self.add(
            arcade.gui.UITextureButton(
                text="+",
                width=self.width,
                style=button_style,
                texture=button_texture,
                texture_hovered=button_hovered_texture,
            )
        )

    def change_var_value(self, variable_type, n, value):
        key = f"{variable_type}_{n}"

        self.rule_values[key] = value

        values = {}
        for i, variable in enumerate(self.rule_dict["user_vars"]):
            lookup_key = f"{variable}_{i}"
            values[VAR_NAMES[i]] = self.rule_values.get(
                lookup_key, VAR_DEFAULT[variable]
            )

        description = self.rule_dict["description"].format_map(values)

        self.desc_label.text = description
        self.var_labels[key].text = f"{VAR_NAMES[n]}: {value}"


class RuleUI(arcade.gui.UIAnchorLayout):
    def __init__(self, window):
        super().__init__(size_hint=(0.95, 0.875))

        self.window = window
        self.current_rule_num = 0
        self.rule_values = {}

        self.dragged_rule_ui = None
        self.rule_ui: dict[str, RuleBox | ComparisonBox] = {}
        self.connections = []
        self.to_connect = []

        self.rules_label = self.add(
            arcade.gui.UILabel(
                text="Rules", font_size=20, text_color=arcade.color.WHITE
            ),
            anchor_x="center",
            anchor_y="top",
        )

        self.add(
            arcade.gui.UISpace(
                height=self.window.height / 70, width=self.window.width * 0.25
            )
        )

        self.add_button_box = self.add(
            arcade.gui.UIBoxLayout(space_between=10),
            anchor_x="center",
            anchor_y="bottom",
        )

        self.add_if_rule_button = self.add_button_box.add(
            arcade.gui.UIFlatButton(
                text="Add IF rule",
                width=self.window.width * 0.225,
                height=self.window.height / 25,
                style=dropdown_style,
            )
        )
        self.add_if_rule_button.on_click = lambda event: self.add_if_rule()

        self.add_do_rule_button = self.add_button_box.add(
            arcade.gui.UIFlatButton(
                text="Add DO rule",
                width=self.window.width * 0.225,
                height=self.window.height / 25,
                style=dropdown_style,
            )
        )
        self.add_do_rule_button.on_click = lambda event: self.add_do_rule()

        self.add_comparison_button = self.add_button_box.add(
            arcade.gui.UIFlatButton(
                text="Add comparison",
                width=self.window.width * 0.225,
                height=self.window.height / 25,
                style=dropdown_style,
            )
        )
        self.add_comparison_button.on_click = lambda event: self.add_comparison()

        self.rule_space = self.add(arcade.gui.UIWidget(size_hint=(1, 1)))

        # self.trash_image = self.add(arcade.gui.UIImage(texture=trash_texture), anchor_x="right", anchor_y="bottom")

    def connection(self, rule_ui):
        if len(self.to_connect) == 1:
            rule_type = self.to_connect[0].rule_type

            if (rule_type == "if" and rule_ui.rule_type == "if") or (rule_type == "do" and rule_type in ["do", "comparison"]):
                return
            
        self.to_connect.append(rule_ui.rule_num)

        if len(self.to_connect) == 2:
            self.connections.append(self.to_connect)
            self.to_connect = []

    @property
    def rulesets(self):  # dinamically generate them? maybe bad idea?
        return {}

    def generate_pos(self):
        return random.randint(
            self.window.width * 0.1, int(self.window.width * 0.9)
        ), random.randint(self.window.height * 0.1, int(self.window.height * 0.7))

    def add_if_rule(self):
        rule_box = RuleBox(
            *self.generate_pos(),
            self.window.width * 0.2,
            self.window.height * 0.1,
            self.current_rule_num,
            "if",
            generate_if_rule(),
        )

        self.rule_space.add(rule_box)
        self.rule_ui[self.current_rule_num] = rule_box
        self.current_rule_num += 1

    def add_do_rule(self):
        rule_box = RuleBox(
            *self.generate_pos(),
            self.window.width * 0.2,
            self.window.height * 0.1,
            self.current_rule_num,
            "do",
            generate_do_rule(),
        )

        self.rule_space.add(rule_box)
        self.rule_ui[self.current_rule_num] = rule_box
        self.current_rule_num += 1

    def add_comparison(self):
        comparison_box = ComparisonBox(
            *self.generate_pos(), generate_comparison(), self.current_rule_num
        )

        self.rule_ui[self.current_rule_num] = comparison_box
        self.add(comparison_box)
        self.current_rule_num += 1

    def draw(self):
        self.bezier_points = []

        for conn in self.connections:
            start_id, end_id = conn
            start_rule_ui = self.rule_ui[start_id]
            end_rule_ui = self.rule_ui[end_id]

            start_pos = start_rule_ui.top if start_rule_ui.rule_type == "do" else start_rule_ui.bottom 
            end_pos = end_rule_ui.top if end_rule_ui.rule_type == "do" else end_rule_ui.bottom 

            points = self.connection_between(start_pos, end_pos)
            self.bezier_points.append(points)

            arcade.draw_line_strip(points, arcade.color.WHITE, 6)

    def on_event(self, event):
        super().on_event(event)

        if isinstance(event, arcade.gui.UIMouseDragEvent):
            if self.dragged_rule_ui is not None:
                self.dragged_rule_ui.center_x += event.dx
                self.dragged_rule_ui.center_y += event.dy
        elif isinstance(event, arcade.gui.UIMouseReleaseEvent):
            self.dragged_rule_ui = None
        elif isinstance(event, arcade.gui.UIMousePressEvent):
            if event.button == arcade.MOUSE_BUTTON_RIGHT:
                ...

            elif event.button == arcade.MOUSE_BUTTON_LEFT:
                for rule_ui in self.rule_ui.values():
                    if rule_ui.rect.point_in_rect((event.x, event.y)):
                        self.dragged_rule_ui = rule_ui
