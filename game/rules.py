from utils.constants import (
    DO_RULES,
    IF_RULES,
    NON_COMPATIBLE_WHEN,
    NON_COMPATIBLE_DO_WHEN,
    VAR_NAMES,
    VAR_DEFAULT,
    TRIGGER_RULES,
    FOR_RULES,
    button_style,
    DO_COLOR,
    IF_COLOR,
    FOR_COLOR,
    TRIGGER_COLOR
)
from typing import List
from utils.preload import button_texture, button_hovered_texture, trash_bin
from arcade.gui.experimental.scroll_area import UIScrollArea, UIScrollBar
from dataclasses import dataclass, field
import arcade, arcade.gui, pyglet, random

IF_KEYS = tuple(IF_RULES.keys())
DO_KEYS = tuple(DO_RULES.keys())

BAD_WHEN = {tuple(sorted(pair)) for pair in NON_COMPATIBLE_WHEN}
BAD_DO_WHEN = {tuple(pair) for pair in NON_COMPATIBLE_DO_WHEN}

def generate_rule(rule_type):
    if rule_type == "if":
        return random.choice(IF_KEYS)
    elif rule_type == "do":
        return random.choice(DO_KEYS)
    
def get_rule_description(rule_type, rule):
    if rule_type == "if":
        return IF_RULES[rule]["description"]
    if rule_type == "for":
        return FOR_RULES[rule]["description"]
    if rule_type == "trigger":
        return TRIGGER_RULES[rule]["description"]
    if rule_type == "do":
        return DO_RULES[rule]["description"]
    
def per_widget_height(height, widget_count):
    return height // widget_count

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

@dataclass
class Block:
    x: float
    y: float
    label: str
    rule_type: str
    rule: str
    rule_num: int
    rule_values: dict[str, int | str]
    children: List["Block"] = field(default_factory=list)

class BlockRenderer:
    def __init__(self, blocks: List[Block], indent: int = 10):
        self.blocks = blocks
        self.indent = indent
        self.shapes = pyglet.graphics.Batch()
        self.shapes_by_rule_num = {}
        self.text_objects = []
        self.text_by_rule_num = {}
        self.refresh()

    def refresh(self):
        for shapes_list in self.shapes_by_rule_num.values():
            for shape in shapes_list:
                shape.delete()
        
        for text_list in self.text_by_rule_num.values():
            for text in text_list:
                text.delete()

        self.shapes = pyglet.graphics.Batch()
        self.shapes_by_rule_num = {}
        self.text_objects = []
        self.text_by_rule_num = {}
        for b in self.blocks.values():
            self._build_block(b, b.x, b.y)

    def _build_block(self, b: Block, x: int, y: int) -> int:
        is_wrap = b.rule_type != "do"
        h, w = 42, 280

        if b.rule_type == "if":
            color = IF_COLOR
        elif b.rule_type == "trigger":
            color = TRIGGER_COLOR
        elif b.rule_type == "do":
            color = DO_COLOR
        elif b.rule_type == "for":
            color = FOR_COLOR

        lx, ly = x, y - h 
        
        if b.rule_num not in self.shapes_by_rule_num:
            self.shapes_by_rule_num[b.rule_num] = []
        if b.rule_num not in self.text_by_rule_num:
            self.text_by_rule_num[b.rule_num] = []
        
        rect = pyglet.shapes.BorderedRectangle(lx, ly, w, h, 2, color, arcade.color.BLACK, batch=self.shapes)
        self.shapes_by_rule_num[b.rule_num].append(rect)
        
        text_obj = pyglet.text.Label(text=b.label, x=lx + 10, y=ly + 20, color=arcade.color.BLACK, font_size=12, weight="bold")
        self.text_objects.append(text_obj)
        self.text_by_rule_num[b.rule_num].append(text_obj)

        ny = ly
        if is_wrap:
            iy = ny
            for child in b.children:
                child.x = lx + self.indent + 5
                child.y = iy - 2
                iy = self._build_block(child, lx + self.indent + 5, iy - 2)
            
            bar_h = ny - iy 
            bar_filled = pyglet.shapes.Rectangle(lx + 2, iy + 2, self.indent, bar_h, color, batch=self.shapes)
            line1 = pyglet.shapes.Line(lx, ny, lx, iy, 2, arcade.color.BLACK, batch=self.shapes)
            bottom = pyglet.shapes.BorderedRectangle(lx, iy - 8, w, 24, 2, color, arcade.color.BLACK, batch=self.shapes)

            self.shapes_by_rule_num[b.rule_num].extend([bar_filled, line1, bottom])
            
            return iy - 24
        else:
            for child in b.children:
                ny = self._build_block(child, lx, ny)
            return ny

    def move_block(self, x, y, rule_num):
        for element in self.shapes_by_rule_num[rule_num] + self.text_by_rule_num[rule_num]:
            element.x += x
            element.y += y

        block = self._find_block(rule_num)

        for child in block.children:
            self.move_block(x, y, child.rule_num)

    def _find_block(self, rule_num):
        if rule_num in self.blocks:
            return self.blocks[rule_num]
        
        for block in self.blocks.values():
            found = self._find_block_recursive(block, rule_num)
            if found:
                return found
        return None

    def _find_block_recursive(self, block, rule_num):
        for child in block.children:
            if child.rule_num == rule_num:
                return child
            found = self._find_block_recursive(child, rule_num)
            if found:
                return found
        return None

    def draw(self):
        self.shapes.draw()
        for t in self.text_objects:
            t.draw()

class RuleUI(arcade.gui.UIAnchorLayout):
    def __init__(self, window: arcade.Window):
        super().__init__(size_hint=(1, 0.875))

        self.window = window
        self.current_rule_num = 0
        self.rule_values = {}

        self.rulesets: dict[int, Block] = {}

        self.block_renderer = BlockRenderer(self.rulesets)
        self.camera = arcade.Camera2D()
    
        self.dragged_rule_ui: Block | None = None

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

        self.create_sidebar = self.add(arcade.gui.UIBoxLayout(size_hint=(0.15, 1), vertical=False, space_between=5), anchor_x="left", anchor_y="bottom")

        self.scroll_area = UIScrollArea(size_hint=(0.95, 1)) # center on screen
        self.scroll_area.scroll_speed = -50
        self.create_sidebar.add(self.scroll_area)

        self.scrollbar = UIScrollBar(self.scroll_area)
        self.scrollbar.size_hint = (0.075, 1)
        self.create_sidebar.add(self.scrollbar)

        self.create_box = self.scroll_area.add(arcade.gui.UIBoxLayout(space_between=10))

        self.create_box.add(arcade.gui.UISpace(height=self.window.height / 100))
        self.create_box.add(arcade.gui.UILabel(text="Trigger Rules", font_size=18))
        self.create_box.add(arcade.gui.UISpace(height=self.window.height / 200))
        for trigger_rule, trigger_rule_data in TRIGGER_RULES.items():
            create_button = self.create_box.add(arcade.gui.UITextureButton(text=trigger_rule_data["description"].format_map({
                "a": "a",
                "b": "b",
                "c": "c"
            }), width=self.window.width * 0.125, multiline=True, height=self.window.height * 0.05, style=button_style, texture=button_texture, texture_hovered=button_hovered_texture))
            create_button.on_click = lambda event, trigger_rule=trigger_rule: self.add_rule("trigger", trigger_rule)

        self.create_box.add(arcade.gui.UISpace(height=self.window.height / 100))
        self.create_box.add(arcade.gui.UILabel(text="IF Rules", font_size=18))
        self.create_box.add(arcade.gui.UISpace(height=self.window.height / 200))
        for if_rule, if_rule_data in IF_RULES.items():
            create_button = self.create_box.add(arcade.gui.UITextureButton(text=if_rule_data["description"].format_map({
                "a": "a",
                "b": "b",
                "c": "c"
            }), width=self.window.width * 0.135, multiline=True, height=self.window.height * 0.05, style=button_style, texture=button_texture, texture_hovered=button_hovered_texture))
            create_button.on_click = lambda event, if_rule=if_rule: self.add_rule("if", if_rule)

        self.create_box.add(arcade.gui.UISpace(height=self.window.height / 100))
        self.create_box.add(arcade.gui.UILabel(text="DO Rules", font_size=18))
        self.create_box.add(arcade.gui.UISpace(height=self.window.height / 200))
        for do_rule, do_rule_data in DO_RULES.items():
            create_button = self.create_box.add(arcade.gui.UITextureButton(text=do_rule_data["description"].format_map({
                "a": "a",
                "b": "b",
                "c": "c"
            }), width=self.window.width * 0.135, multiline=True, height=self.window.height * 0.05, style=button_style, texture=button_texture, texture_hovered=button_hovered_texture))
            create_button.on_click = lambda event, do_rule=do_rule: self.add_rule("do", do_rule)
            
        self.create_box.add(arcade.gui.UISpace(height=self.window.height / 100))
        self.create_box.add(arcade.gui.UILabel(text="For Rules", font_size=18))
        self.create_box.add(arcade.gui.UISpace(height=self.window.height / 200))
        for for_rule, for_rule_data in FOR_RULES.items():
            create_button = self.create_box.add(arcade.gui.UITextureButton(text=for_rule_data["description"].format_map({
                "a": "a",
                "b": "b",
                "c": "c"
            }), width=self.window.width * 0.135, multiline=True, height=self.window.height * 0.05, style=button_style, texture=button_texture, texture_hovered=button_hovered_texture))
            create_button.on_click = lambda event, for_rule=for_rule: self.add_rule("for", for_rule)
            
        self.trash_spritelist = arcade.SpriteList()
        self.trash_sprite = trash_bin
        self.trash_sprite.scale = 0.5
        self.trash_sprite.position = (self.window.width * 0.9, self.window.height * 0.2)
        self.trash_spritelist.append(self.trash_sprite)

    def get_rulesets(self):
        # TODO: remove this
        return [], []

    def generate_pos(self):
        return random.randint(
            self.window.width * 0.1, int(self.window.width * 0.9)
        ), random.randint(self.window.height * 0.1, int(self.window.height * 0.7))

    def add_rule(self, rule_type, force=None):
        rule = force or generate_rule(rule_type)
        rule_box = Block(
            *self.generate_pos(),
            get_rule_description(rule_type, rule),
            rule_type,
            rule,
            self.current_rule_num,
            {},
            []
        )

        self.rulesets[self.current_rule_num] = rule_box
        self.current_rule_num += 1
        self.block_renderer.refresh()

        return rule_box

    def draw(self):
        self.block_renderer.draw()

    def draw_unproject(self):
        self.trash_spritelist.draw()

    def drag_n_drop_check(self, blocks):
        for block in blocks:
            if block == self.dragged_rule_ui:
                continue

            if arcade.LBWH(block.x, block.y - 44, 280, 44).intersection(arcade.LBWH(self.dragged_rule_ui.x, self.dragged_rule_ui.y - 44, 280, 44)):
                block.children.append(self.dragged_rule_ui)
                del self.rulesets[self.dragged_rule_ui.rule_num]
                self.block_renderer.refresh()
                break
            else:
                self.drag_n_drop_check(block.children)

    def remove_from_parent(self, block_to_remove, parents):
        for parent in parents:
            if block_to_remove in parent.children:
                self.rulesets[block_to_remove.rule_num] = block_to_remove 
                parent.children.remove(block_to_remove)
                return True
            if self.remove_from_parent(block_to_remove, parent.children):
                return True
        return False

    def press_check(self, event, blocks):
        for block in blocks:
            if block == self.dragged_rule_ui:
                continue

            projected_vec = self.camera.unproject((event.x, event.y))
            if arcade.LBWH(block.x, block.y - 44, 280, 44).point_in_rect((projected_vec.x, projected_vec.y)):
                if block not in list(self.rulesets.values()):  # its children
                    self.remove_from_parent(block, list(self.rulesets.values()))
                    self.block_renderer.refresh()
                self.dragged_rule_ui = block
                break
            else:
                self.press_check(event, block.children)

    def on_event(self, event):
        super().on_event(event)

        if isinstance(event, arcade.gui.UIMouseDragEvent):
            if event.buttons == arcade.MOUSE_BUTTON_LEFT:
                if self.dragged_rule_ui is not None:
                    self.dragged_rule_ui.x += event.dx
                    self.dragged_rule_ui.y += event.dy
                    self.block_renderer.move_block(event.dx, event.dy, self.dragged_rule_ui.rule_num)

        elif isinstance(event, arcade.gui.UIMousePressEvent):
            self.press_check(event, list(self.rulesets.values()))

        elif isinstance(event, arcade.gui.UIMouseReleaseEvent):
            if self.dragged_rule_ui:
                block_vec = self.camera.unproject((self.dragged_rule_ui.x, self.dragged_rule_ui.y))
                if self.trash_sprite.rect.intersection(arcade.LBWH(block_vec.x, block_vec.y, 280, 44)) and not self.trash_sprite._current_keyframe_index == self.trash_sprite.animation.num_frames - 1:
                    del self.rulesets[self.dragged_rule_ui.rule_num]
                    self.dragged_rule_ui = None
                    self.block_renderer.refresh()
                    return

                self.drag_n_drop_check(list(self.rulesets.values()))

            self.dragged_rule_ui = None

    def on_update(self, dt):
        if self.dragged_rule_ui:
            block_vec = self.camera.unproject((self.dragged_rule_ui.x, self.dragged_rule_ui.y))
            if self.trash_sprite.rect.intersection(arcade.LBWH(block_vec.x, block_vec.y, 280, 44)) and not self.trash_sprite._current_keyframe_index == self.trash_sprite.animation.num_frames - 1:
                self.trash_sprite.update_animation()
        else:
            self.trash_sprite.time = 0
            self.trash_sprite.update_animation()