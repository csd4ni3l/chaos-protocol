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
from utils.preload import button_texture, button_hovered_texture, trash_bin
from collections import deque, defaultdict
import arcade, arcade.gui, random

IF_KEYS = tuple(IF_RULES.keys())
DO_KEYS = tuple(DO_RULES.keys())

BAD_WHEN = {tuple(sorted(pair)) for pair in NON_COMPATIBLE_WHEN}
BAD_DO_WHEN = {tuple(pair) for pair in NON_COMPATIBLE_DO_WHEN}

def generate_rule(rule_type):
    if rule_type == "if":
        return random.choice(IF_KEYS)
    elif rule_type == "do":
        return random.choice(DO_KEYS)
    else:
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

def connection_between(p0, p3, start_dir_y, end_dir_y):
    offset = max(abs(p3[1] - p0[1]) * 0.5, 20)
    c1 = (p0[0], p0[1] + start_dir_y * offset)
    c2 = (p3[0], p3[1] + end_dir_y * offset)

    return cubic_bezier_points(p0, c1, c2, p3, segments=100)

def connected_component(edges, start):
    graph = defaultdict(set)
    for u, v in edges:
        graph[u].add(v)
        graph[v].add(u)

    seen = set([start])
    queue = deque([start])

    while queue:
        node = queue.popleft()
        for neighbor in graph[node]:
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)

    return list(seen)

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

class RuleBox(arcade.gui.UIBoxLayout):
    def __init__(self, x, y, width, height, rule_num, rule_type, rule):
        super().__init__(space_between=5, x=x, y=y, width=width, height=height)

        self.rule = rule
        self.rule_num = rule_num
        self.rule_type = rule_type
        self.initialize_rule()

    def initialize_rule(self):
        if not self.rule_type == "comparison":
            self.rule_dict = (
                IF_RULES[self.rule] if self.rule_type == "if" else DO_RULES[self.rule]
            )
            self.defaults = get_rule_defaults(self.rule_type)
            self.rule_values = {}
            self.var_labels = {}
            self.var_changers = {}

            widget_count = 2 + len(self.rule_dict["user_vars"])

            self.per_widget_height = per_widget_height(
                self.height, 
                widget_count
            )
        else:
            self.per_widget_height = per_widget_height(
                self.height,
                2
            )

        self.init_ui()
    
    def init_ui(self):
        if self.rule_type == "do":
            self.previous_button, self.drag_button = self.add_extra_buttons(["IF/Comparison", "Drag"])
        elif self.rule_type == "if":
            self.drag_button = self.add_extra_buttons("Drag")[0]
        elif self.rule_type == "comparison":
            self.previous_button_1, self.previous_button_2, self.drag_button = self.add_extra_buttons(["IF 1", "IF 2", "Drag"])

        dropdown_options = [desc for desc, _ in self.defaults.values()] if not self.rule_type == "comparison" else LOGICAL_OPERATORS
        self.desc_label = self.add(
            arcade.gui.UIDropdown(
                default=self.defaults[self.rule][0] if not self.rule_type == "comparison" else dropdown_options[0],
                options=dropdown_options,
                font_size=13,
                active_style=dropdown_style,
                primary_style=dropdown_style,
                dropdown_style=dropdown_style,
                width=self.width,
                height=self.per_widget_height
            )
        )
        self.desc_label.on_change = lambda event: self.change_rule_type(event.new_value)
        
        if self.rule_type == "comparison":
            self.next_button = self.add_extra_buttons("Do / Comparison")[0]
            return

        for n, variable_type in enumerate(self.rule_dict["user_vars"]):
            key = f"{variable_type}_{n}"

            defaults = get_rule_defaults(self.rule_type)
            default_values = defaults[self.rule][1]
            self.rule_values[key] = default_values[VAR_NAMES[n]]

            box = self.add(
                arcade.gui.UIBoxLayout(
                    vertical=False, 
                    width=self.width, 
                    height=self.per_widget_height * 2
                )
            )

            self.var_labels[key] = box.add(
                arcade.gui.UILabel(
                    f"{VAR_NAMES[n]}: " if not variable_type in ["variable", "size"] else f"{VAR_NAMES[n]}: {self.rule_values[key]}",
                    font_size=11,
                    text_color=arcade.color.WHITE,
                    width=self.width,
                    height=self.per_widget_height,
                )
            )

            if variable_type in ["variable", "size"]:
                slider = box.add(
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
                dropdown = box.add(
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
            self.next_button = self.add_extra_buttons("Do / Comparison")[0]

    def add_extra_buttons(self, texts: list[str] | str):
        if not isinstance(texts, list):
            texts = [texts]
            box = self
        else:
            box = self.add(
                arcade.gui.UIBoxLayout(
                    vertical=False, 
                    width=self.width, 
                    height=self.per_widget_height
                )
            )

        return [
            box.add(
                arcade.gui.UITextureButton(
                    text=text,
                    width=self.width / len(texts),
                    height=self.per_widget_height,
                    style=button_style,
                    texture=button_texture,
                    texture_hovered=button_hovered_texture,
                )
            )
            for text in texts
        ]

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

        if variable_type in ["variable", "size"]:
            self.var_labels[key].text = f"{VAR_NAMES[n]}: {value}"

    def change_rule_type(self, new_rule_desc):
        self.rule = next(key for key, default_list in self.defaults.items() if default_list[0] == new_rule_desc) if self.rule_type != "comparison" else new_rule_desc
        self.clear()
        self.initialize_rule()

def get_connection_pos(rule_ui: RuleBox, idx):
    if rule_ui.rule_type == "comparison":
        if idx == 1:
            button = rule_ui.previous_button_1
            y = button.top
            direction = 1
        elif idx == 2:
            button = rule_ui.previous_button_2
            y = button.top
            direction = 1
        else:
            button = rule_ui.next_button
            y = button.bottom
            direction = -1
    elif rule_ui.rule_type == "if":
        button = rule_ui.next_button
        y = button.bottom
        direction = -1
    elif rule_ui.rule_type == "do":
        button = rule_ui.previous_button
        y = button.top
        direction = 1
    
    return (button.center_x, y), direction

class RuleUI(arcade.gui.UIAnchorLayout):
    def __init__(self, window: arcade.Window):
        super().__init__(size_hint=(0.95, 0.875))

        self.window = window
        self.current_rule_num = 0
        self.rule_values = {}

        self.dragged_rule_ui: RuleBox | None = None
        self.rule_ui: dict[str, RuleBox] = {}
        
        self.connections = []
        self.to_connect = None
        self.to_connect_idx = None
        self.allowed_next_connection = []

        self.rules_label = self.add(
            arcade.gui.UILabel(
                text="Rules", font_size=20, text_color=arcade.color.WHITE
            ),
            anchor_x="center",
            anchor_y="top"
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
        self.add_if_rule_button.on_click = lambda event: self.add_rule("if")

        self.add_do_rule_button = self.add_button_box.add(
            arcade.gui.UIFlatButton(
                text="Add DO rule",
                width=self.window.width * 0.225,
                height=self.window.height / 25,
                style=dropdown_style,
            )
        )
        self.add_do_rule_button.on_click = lambda event: self.add_rule("do")

        self.add_comparison_button = self.add_button_box.add(
            arcade.gui.UIFlatButton(
                text="Add comparison",
                width=self.window.width * 0.225,
                height=self.window.height / 25,
                style=dropdown_style,
            )
        )
        self.add_comparison_button.on_click = lambda event: self.add_rule("comparison")

        self.rule_space = self.add(arcade.gui.UIWidget(size_hint=(1, 1)))

        # self.create_connected_ruleset([("if", "x_position_compare"), ("do", "move_x")])

        self.trash_spritelist = arcade.SpriteList()
        self.trash_sprite = trash_bin
        self.trash_sprite.position = (self.window.width * 0.9, self.window.height * 0.2)
        self.trash_spritelist.append(self.trash_sprite)

    def connection(self, rule_ui, allowed_next_connection, idx):
        if self.to_connect is not None:
            old_rule_type = self.rule_ui[self.to_connect].rule_type
            if (
                    rule_ui.rule_type not in self.allowed_next_connection or
                    old_rule_type not in allowed_next_connection or 
                    (old_rule_type == "if" and rule_ui.rule_type == "if") or
                    (old_rule_type == "do" and rule_ui.rule_type in ["do", "comparison"]) or 
                    rule_ui.rule_num == self.to_connect
                ):

                return
            
            self.connections.append([self.to_connect, rule_ui.rule_num, self.to_connect_idx, idx])
            self.allowed_next_connection = None
            self.to_connect = None
            self.to_connect_idx = None
        else:
            self.allowed_next_connection = allowed_next_connection
            self.to_connect = rule_ui.rule_num
            self.to_connect_idx = idx

    def drag(self, rule_ui):
        if self.dragged_rule_ui:
            if self.dragged_rule_ui.rect.intersection(self.trash_sprite.rect):
                self.rule_ui.pop(self.dragged_rule_ui.rule_num)

                if self.dragged_rule_ui.rule_num == self.to_connect:
                    self.to_connect = None

                for connection in self.connections:
                    if self.dragged_rule_ui.rule_num in connection:
                        self.connections.remove(connection)

                self.remove(self.dragged_rule_ui)
                del self.dragged_rule_ui

            self.dragged_rule_ui = None
        else:
            self.dragged_rule_ui = rule_ui

    def get_rulesets(self):
        if self.connections:
            components = connected_component(self.connections, 0)
            print(components)

        return {}

    def generate_pos(self):
        return random.randint(
            self.window.width * 0.1, int(self.window.width * 0.9)
        ), random.randint(self.window.height * 0.1, int(self.window.height * 0.7))

    def add_rule(self, rule_type, force=None):
        rule_box = RuleBox(
            *self.generate_pos(),
            self.window.width * 0.15,
            self.window.height * 0.15,
            self.current_rule_num,
            rule_type,
            force or generate_rule(rule_type),
        )
        if rule_type == "if":
            rule_box.next_button.on_click = lambda event, rule_box=rule_box: self.connection(rule_box, ["do", "comparison"], 1)
        elif rule_type == "comparison":
            rule_box.previous_button_1.on_click = lambda event, rule_box=rule_box: self.connection(rule_box, ["if", "comparison"], 1)
            rule_box.previous_button_2.on_click = lambda event, rule_box=rule_box: self.connection(rule_box, ["if", "comparison"], 2)
            rule_box.next_button.on_click = lambda event, rule_box=rule_box: self.connection(rule_box, ["do", "comparison"], 3)
        elif rule_type == "do":
            rule_box.previous_button.on_click = lambda event, rule_box=rule_box: self.connection(rule_box, ["if", "comparison"], 1)

        rule_box.drag_button.on_click = lambda event, rule_box=rule_box: self.drag(rule_box)

        self.rule_space.add(rule_box)
        self.rule_ui[self.current_rule_num] = rule_box
        self.rule_ui[self.current_rule_num].fit_content()

        self.current_rule_num += 1

        return rule_box

    def create_connected_ruleset(self, rules):
        previous = None

        for rule_type, rule in rules:
            rule_box = self.add_rule(rule_type, rule)

            if previous:
                self.connections.append((previous.rule_num, rule_box.rule_num))

            previous = rule_box

    def draw(self):
        self.bezier_points = []

        for conn in self.connections:
            start_id, end_id, start_conn_idx, end_conn_idx = conn
            start_rule_ui = self.rule_ui[start_id]
            end_rule_ui = self.rule_ui[end_id]

            start_pos, start_dir_y = get_connection_pos(start_rule_ui, start_conn_idx)
            end_pos, end_dir_y = get_connection_pos(end_rule_ui, end_conn_idx)

            points = connection_between(start_pos, end_pos, start_dir_y, end_dir_y)
            self.bezier_points.append(points)

            arcade.draw_line_strip(points, arcade.color.WHITE, 6)

        if self.to_connect is not None:
            mouse_x, mouse_y = self.window.mouse.data.get("x", 0), self.window.mouse.data.get("y", 0)
            start_pos, start_dir = get_connection_pos(self.rule_ui[self.to_connect], self.to_connect_idx)
            end_pos, end_dir = (mouse_x, mouse_y), 1
            points = connection_between(start_pos, end_pos, start_dir, end_dir)
            arcade.draw_line_strip(points, arcade.color.WHITE, 6)

        self.trash_spritelist.draw()

    def on_event(self, event):
        super().on_event(event)

        if isinstance(event, arcade.gui.UIMouseMovementEvent):
            if self.dragged_rule_ui is not None:
                self.dragged_rule_ui.center_x += event.dx
                self.dragged_rule_ui.center_y += event.dy

    def on_update(self, dt):
        if self.dragged_rule_ui and self.trash_sprite.rect.point_in_rect((self.window.mouse.data["x"], self.window.mouse.data["y"])):
            if not self.trash_sprite._current_keyframe_index == self.trash_sprite.animation.num_frames - 1:
                self.trash_sprite.update_animation()
        else:
            self.trash_sprite.time = 0
            self.trash_sprite.update_animation()