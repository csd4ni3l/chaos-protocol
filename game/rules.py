from utils.constants import DO_RULES, IF_RULES, LOGICAL_OPERATORS, NON_COMPATIBLE_WHEN, NON_COMPATIBLE_DO_WHEN, VAR_NAMES, VAR_DEFAULT, VAR_OPTIONS, dropdown_style, slider_style
import arcade, arcade.gui, random

IF_KEYS = tuple(IF_RULES.keys())
DO_KEYS = tuple(DO_RULES.keys())

BAD_WHEN = {tuple(sorted(pair)) for pair in NON_COMPATIBLE_WHEN}
BAD_DO_WHEN = {tuple(pair) for pair in NON_COMPATIBLE_DO_WHEN}

def generate_ruleset(ruleset_type):
    when_a = random.choice(IF_KEYS)

    if ruleset_type == "advanced":
        valid_b = [
            b for b in IF_KEYS
            if b != when_a and tuple(sorted((when_a, b))) not in BAD_WHEN
        ]

        if not valid_b:
            return [when_a, random.choice(DO_KEYS)]

        when_b = random.choice(valid_b)
        logical = random.choice(LOGICAL_OPERATORS)
    else:
        when_b = None
        logical = None

    if when_b:
        valid_do = [
            d for d in DO_KEYS
            if (when_a, d) not in BAD_DO_WHEN
            and (when_b, d) not in BAD_DO_WHEN
            and (d, when_a) not in BAD_DO_WHEN
            and (d, when_b) not in BAD_DO_WHEN
        ]
    else:
        valid_do = [
            d for d in DO_KEYS
            if (when_a, d) not in BAD_DO_WHEN
            and (d, when_a) not in BAD_DO_WHEN
        ]

    do = random.choice(valid_do)

    if logical:
        return [when_a, logical, when_b, do]
    else:
        return [when_a, do]
    
class RuleUIBox(arcade.gui.UIBoxLayout):
    def __init__(self, window):
        super().__init__(space_between=10, align="center", size_hint=(0.95, 0.75))
        self.window = window
        self.current_ruleset_num = 0
        self.current_ruleset_page = 0
        self.rulesets_per_page = 2
        self.rulesets = {}
        self.rule_values = {}

        self.rule_labels = {}
        self.rule_var_changers = {}
        self.rule_boxes = {}

        self.nav_buttons_box = None

        self.rules_label = self.add(arcade.gui.UILabel(text="Rules", font_size=20, text_color=arcade.color.WHITE))
        self.add(arcade.gui.UISpace(height=self.window.height / 70, width=self.window.width * 0.25))

        self.add_simple_rule_button = self.add(arcade.gui.UIFlatButton(text="Add Simple rule", width=self.window.width * 0.225, height=self.window.height / 25, style=dropdown_style))
        self.add_simple_rule_button.on_click = lambda event: self.add_rule("simple")

        self.add(arcade.gui.UISpace(height=self.window.height / 85))

        self.add_advanced_rule_button = self.add(arcade.gui.UIFlatButton(text="Add Advanced rule", width=self.window.width * 0.225, height=self.window.height / 25, style=dropdown_style))
        self.add_advanced_rule_button.on_click = lambda event: self.add_rule("advanced")
    
        self.add(arcade.gui.UISpace(height=self.window.height / 85))

        self.nav_buttons_box = self.add(arcade.gui.UIBoxLayout(vertical=False, space_between=10))
        
        self.prev_button = self.nav_buttons_box.add(arcade.gui.UIFlatButton(text="Previous", width=self.window.width * 0.1, height=self.window.height / 25, style=dropdown_style))
        self.prev_button.on_click = self.prev_page
        
        self.next_button = self.nav_buttons_box.add(arcade.gui.UIFlatButton(text="Next", width=self.window.width * 0.1, height=self.window.height / 25, style=dropdown_style))
        self.next_button.on_click = self.next_page

        self.rules_content_box = self.add(arcade.gui.UIBoxLayout(align="center"))

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
        
    def create_rule_ui(self, rule_box: arcade.gui.UIBoxLayout, rule, rule_type, rule_num=1, is_import=False):
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

            if not is_import:
                self.rule_values[key] = default_values[VAR_NAMES[n]]

            label = rule_box.add(arcade.gui.UILabel(f'{VAR_NAMES[n]}: {self.rule_values[key]}', font_size=11, width=self.window.width * 0.225, height=self.window.height / 30))
            self.rule_labels[key] = label

            if variable_type in ["variable", "size"]: 
                slider = rule_box.add(arcade.gui.UISlider(value=self.rule_values[key], min_value=VAR_OPTIONS[variable_type][0], max_value=VAR_OPTIONS[variable_type][1], step=1, style=slider_style, width=self.window.width * 0.225, height=self.window.height / 30))
                slider._render_steps = lambda surface: None  
                slider.on_change = lambda event, variable_type=variable_type, rule=rule, rule_type=rule_type, ruleset_num=ruleset_num, rule_num=rule_num, n=n: self.change_rule_value(ruleset_num, rule_num, rule, rule_type, variable_type, n, event.new_value)
                self.rule_var_changers[key] = slider

            else:
                dropdown = rule_box.add(arcade.gui.UIDropdown(default=self.rule_values[key], options=VAR_OPTIONS[variable_type], active_style=dropdown_style, primary_style=dropdown_style, dropdown_style=dropdown_style, width=self.window.width * 0.225, height=self.window.height / 30))
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

    def add_ruleset(self, ruleset, is_import=False):
        rule_box = arcade.gui.UIBoxLayout(space_between=5, align="left")
        self.rule_boxes[self.current_ruleset_num] = rule_box

        if len(ruleset) == 2:
            self.rulesets[self.current_ruleset_num] = ruleset
            
            self.create_rule_ui(rule_box, ruleset[0], "if", 1, is_import)
            self.create_rule_ui(rule_box, ruleset[1], "do", 2, is_import)

        else:
            self.rulesets[self.current_ruleset_num] = ruleset

            self.create_rule_ui(rule_box, ruleset[0], "if", 1, is_import)
            rule_box.add(arcade.gui.UILabel(ruleset[1].upper(), font_size=14, width=self.window.width * 0.25))
            self.create_rule_ui(rule_box, ruleset[2], "if", 2, is_import)
            self.create_rule_ui(rule_box, ruleset[3], "do", 3, is_import)

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

    def add_rule(self, ruleset_type=None, force=None):
        self.rulesets[self.current_ruleset_num] = generate_ruleset(ruleset_type) if not force else force
        self.add_ruleset(self.rulesets[self.current_ruleset_num])
        self.current_ruleset_num += 1
        if self.rules_content_box:
            self.refresh_rules_display()