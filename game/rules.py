from utils.constants import (
    DO_RULES,
    IF_RULES,
    TRIGGER_RULES,
    FOR_RULES,
    NEEDS_SHAPE,
    PROVIDES_SHAPE,
    button_style,
    slider_style,
    dropdown_style,
    DO_COLOR,
    IF_COLOR,
    FOR_COLOR,
    TRIGGER_COLOR,
    RULE_DEFAULTS,
    VAR_TYPES
)
from typing import List
from utils.preload import button_texture, button_hovered_texture, trash_bin
from arcade.gui.experimental.scroll_area import UIScrollArea, UIScrollBar
from dataclasses import dataclass, field
import arcade, arcade.gui, pyglet, random, re

def get_rule_dict(rule_type):
    if rule_type == "if":
        return IF_RULES
    elif rule_type == "for":
        return FOR_RULES
    elif rule_type == "trigger":
        return TRIGGER_RULES
    elif rule_type == "do":
        return DO_RULES
    
@dataclass
class VarBlock:
    x: float
    y: float
    label: str
    var_type: str
    connected_rule_num: str
    value: str | int

@dataclass
class Block:
    x: float
    y: float
    label: str
    rule_type: str
    rule: str
    rule_num: int
    vars: List["VarBlock"] = field(default_factory=list)
    children: List["Block"] = field(default_factory=list)

class BlockRenderer:
    def __init__(self, blocks: List[Block], indent: int = 12):
        self.blocks = blocks
        self.indent = indent
        self.shapes = pyglet.graphics.Batch()
        self.shapes_by_rule_num = {}
        self.text_objects = []
        self.text_by_rule_num = {}
        self.var_widgets = {}  
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
        self.var_widgets = {}
        for b in self.blocks.values():
            self._build_block(b, b.x, b.y)

    def _build_var_ui(self, var: VarBlock, x: int, y: int, rule_num: int) -> tuple:
        var_width = max(60, len(str(var.value)) * 8 + 20)
        var_height = 24
        var_color = (255, 255, 255) 
        var_rect = pyglet.shapes.BorderedRectangle(
            x, y - var_height // 2, var_width, var_height, 
            2, var_color, arcade.color.BLACK, batch=self.shapes
        )
        
        var_text = pyglet.text.Label(
            text=str(var.value), 
            x=x + var_width // 2, 
            y=y, 
            color=arcade.color.BLACK, 
            font_size=10,
            anchor_x='center',
            anchor_y='center'
        )
        
        if rule_num not in self.shapes_by_rule_num:
            self.shapes_by_rule_num[rule_num] = []
        if rule_num not in self.text_by_rule_num:
            self.text_by_rule_num[rule_num] = []
        if rule_num not in self.var_widgets:
            self.var_widgets[rule_num] = []
            
        self.shapes_by_rule_num[rule_num].append(var_rect)
        self.text_by_rule_num[rule_num].append(var_text)
        self.text_objects.append(var_text)
        
        self.var_widgets[rule_num].append({
            'var': var,
            'rect': var_rect,
            'text': var_text,
            'x': x,
            'y': y,
            'width': var_width,
            'height': var_height
        })
        
        return var_width, var_height

    def _build_block_with_vars(self, b: Block, x: int, y: int) -> None:
        lx, ly = x, y - 42
        
        current_x = lx + 10
        current_y = ly + 28
        
        pattern = r' ([a-z]) '
        parts = re.split(pattern, b.label)
        
        var_index = 0
        for i, part in enumerate(parts):
            if i % 2 == 0:
                if part:
                    text_obj = pyglet.text.Label(
                        text=part, 
                        x=current_x, 
                        y=current_y - 3, 
                        color=arcade.color.BLACK, 
                        font_size=12, 
                        weight="bold"
                    )
                    self.text_objects.append(text_obj)
                    self.text_by_rule_num[b.rule_num].append(text_obj)
                    
                    current_x += len(part) * 10
            else:
                if var_index < len(b.vars):
                    var = b.vars[var_index]
                    var_width, var_height = self._build_var_ui(
                        var, current_x, current_y, b.rule_num
                    )
                    current_x += var_width + 7
                    var_index += 1

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
        
        if b.vars:
            self._build_block_with_vars(b, x, y)
        else:
            text_obj = pyglet.text.Label(
                text=b.label, 
                x=lx + 7, 
                y=ly + 20, 
                color=arcade.color.BLACK, 
                font_size=12, 
                weight="bold"
            )
            self.text_objects.append(text_obj)
            self.text_by_rule_num[b.rule_num].append(text_obj)

        next_y = ly
        if is_wrap:
            iy = next_y
            for child in b.children:
                child.x = lx + self.indent + 5
                child.y = iy
                iy = self._build_block(child, lx + self.indent + 5, iy)
            
            bar_h = next_y - iy 
            bar_filled = pyglet.shapes.Rectangle(lx + 2, iy + 2, self.indent, bar_h, color, batch=self.shapes)
            line1 = pyglet.shapes.Line(lx, next_y, lx, iy, 2, arcade.color.BLACK, batch=self.shapes)
            bottom = pyglet.shapes.BorderedRectangle(lx, iy - 8, w, 24, 2, color, arcade.color.BLACK, batch=self.shapes)

            self.shapes_by_rule_num[b.rule_num].extend([bar_filled, line1, bottom])
            
            return iy - 24
        else:
            for child in b.children:
                child.x = lx
                child.y = next_y
                ly = self._build_block(child, lx, next_y)
            return ly - 16

    def move_block(self, x, y, rule_num):
        for element in self.shapes_by_rule_num[rule_num] + self.text_by_rule_num[rule_num]:
            element.x += x
            element.y += y
        
        if rule_num in self.var_widgets:
            for widget in self.var_widgets[rule_num]:
                widget['x'] += x
                widget['y'] += y

        block = self._find_block(rule_num)

        for child in block.children:
            self.move_block(x, y, child.rule_num)

    def get_var_at_position(self, x, y):
        for rule_num, widgets in self.var_widgets.items():
            for widget in widgets:
                wx, wy = widget['x'], widget['y']
                ww, wh = widget['width'], widget['height']
                if (wx <= x <= wx + ww and 
                    wy - wh // 2 <= y <= wy + wh // 2):
                    return widget['var'], rule_num
        return None, None

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

class VarEditDialog(arcade.gui.UIAnchorLayout):
    def __init__(self, var: VarBlock, on_save, on_cancel):
        super().__init__()
        self.var = var
        self.on_save_callback = on_save
        self.on_cancel_callback = on_cancel
        
        self.background = self.add(
            arcade.gui.UISpace(color=(0, 0, 0, 180)),
            anchor_x="center",
            anchor_y="center"
        )
        
        dialog_box = arcade.gui.UIBoxLayout(
            space_between=10,
            width=300,
            height=200
        )
        
        dialog_box.with_padding(all=20)
        dialog_box.with_background(color=(60, 60, 80))
        
        dialog_box.add(arcade.gui.UILabel(
            text=f"Edit {var.label}",
            font_size=16,
            text_color=arcade.color.WHITE
        ))
        
        if var.var_type == "variable":
            self.input_field = arcade.gui.UIInputText(
                text=str(var.value),
                width=260,
                height=40
            )
            dialog_box.add(self.input_field)
        elif var.var_type in ["shape_type", "target_type", "color", "key_input", "comparison"]:
            from utils.constants import VAR_OPTIONS
            options = VAR_OPTIONS[var.var_type]
            self.dropdown = arcade.gui.UIDropdown(
                default=str(var.value),
                options=options,
                width=260,
                height=40,
                style=dropdown_style
            )
            dialog_box.add(self.dropdown)
        elif var.var_type == "size":
            self.slider = arcade.gui.UISlider(
                value=int(var.value),
                min_value=1,
                max_value=200,
                width=260,
                height=40,
                style=slider_style
            )
            dialog_box.add(self.slider)
        
        button_layout = arcade.gui.UIBoxLayout(vertical=False, space_between=10)
        
        save_btn = arcade.gui.UIFlatButton(
            text="Save",
            width=125,
            height=40
        )
        save_btn.on_click = self._on_save
        
        cancel_btn = arcade.gui.UIFlatButton(
            text="Cancel",
            width=125,
            height=40
        )
        cancel_btn.on_click = self._on_cancel
        
        button_layout.add(save_btn)
        button_layout.add(cancel_btn)
        dialog_box.add(button_layout)
        
        self.add(dialog_box, anchor_x="center", anchor_y="center")
    
    def _on_save(self, event):
        if hasattr(self, 'input_field'):
            try:
                self.var.value = int(self.input_field.text)
            except ValueError:
                self.var.value = self.input_field.text
        elif hasattr(self, 'dropdown'):
            self.var.value = self.dropdown.value
        elif hasattr(self, 'slider'):
            self.var.value = int(self.slider.value)
        
        self.on_save_callback()
    
    def _on_cancel(self, event):
        self.on_cancel_callback()

class RuleUI(arcade.gui.UIAnchorLayout):
    def __init__(self, window: arcade.Window):
        super().__init__(size_hint=(1, 0.875))

        self.window = window
        self.current_rule_num = 0
        self.rule_values = {}
        self.var_edit_dialog = None

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
        self.scroll_area.scroll_speed = 0
        self.create_sidebar.add(self.scroll_area)

        self.scrollbar = UIScrollBar(self.scroll_area)
        self.scrollbar.size_hint = (0.075, 1)
        self.create_sidebar.add(self.scrollbar)

        self.create_box = self.scroll_area.add(arcade.gui.UIBoxLayout(space_between=10))

        self.add_rule_create_box("trigger")
        self.add_rule_create_box("if")
        self.add_rule_create_box("do")
        self.add_rule_create_box("for")

        self.trash_spritelist = arcade.SpriteList()
        self.trash_sprite = trash_bin
        self.trash_sprite.scale = 0.5
        self.trash_sprite.position = (self.window.width * 0.9, self.window.height * 0.2)
        self.trash_spritelist.append(self.trash_sprite)

    def add_rule_create_box(self, rule_type):
        self.create_box.add(arcade.gui.UISpace(height=self.window.height / 100))
        self.create_box.add(arcade.gui.UILabel(text=f"{rule_type.capitalize()} Rules", font_size=18))
        self.create_box.add(arcade.gui.UISpace(height=self.window.height / 200))
        for rule in get_rule_dict(rule_type):
            create_button = self.create_box.add(arcade.gui.UITextureButton(text=RULE_DEFAULTS[rule_type][rule][0], width=self.window.width * 0.135, multiline=True, height=self.window.height * 0.05, style=button_style, texture=button_texture, texture_hovered=button_hovered_texture))
            create_button.on_click = lambda event, rule=rule: self.add_rule(rule_type, rule)

    def generate_pos(self):
        return random.randint(
            self.window.width * 0.1, int(self.window.width * 0.9)
        ), random.randint(self.window.height * 0.1, int(self.window.height * 0.7))

    def add_rule(self, rule_type, rule):
        rule_dict = get_rule_dict(rule_type)[rule]
        rule_box = Block(
            *self.generate_pos(),
            RULE_DEFAULTS[rule_type][rule][0],
            rule_type,
            rule,
            self.current_rule_num,
            [
                VarBlock(
                    *self.generate_pos(),
                    VAR_TYPES[var_type],
                    var_type,
                    self.current_rule_num,
                    RULE_DEFAULTS[rule_type][rule][1][n]
                ) 

                for n, var_type in enumerate(rule_dict["user_vars"])
            ],
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
        if self.dragged_rule_ui.rule_type == "trigger":
            return

        for block in blocks:
            if block == self.dragged_rule_ui or (self.dragged_rule_ui.rule in NEEDS_SHAPE and block.rule not in PROVIDES_SHAPE):
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
        if self.var_edit_dialog:
            super().on_event(event)
            return

        super().on_event(event)

        if isinstance(event, arcade.gui.UIMouseDragEvent):
            if event.buttons == arcade.MOUSE_BUTTON_LEFT:
                if self.dragged_rule_ui is not None:
                    self.dragged_rule_ui.x += event.dx
                    self.dragged_rule_ui.y += event.dy
                    self.block_renderer.move_block(event.dx, event.dy, self.dragged_rule_ui.rule_num)

        elif isinstance(event, arcade.gui.UIMousePressEvent):
            projected_vec = self.camera.unproject((event.x, event.y))
            var, _ = self.block_renderer.get_var_at_position(projected_vec.x, projected_vec.y)
            
            if var:
                self.open_var_edit_dialog(var)
                return
            
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

    def open_var_edit_dialog(self, var: VarBlock):
        def on_save():
            self.close_var_edit_dialog()
            self.block_renderer.refresh()
        
        def on_cancel():
            self.close_var_edit_dialog()
        
        self.var_edit_dialog = VarEditDialog(var, on_save, on_cancel)
        self.add(self.var_edit_dialog)
    
    def close_var_edit_dialog(self):
        if self.var_edit_dialog:
            self.remove(self.var_edit_dialog)
            self.var_edit_dialog = None
            self.trigger_full_render()

    def on_update(self, dt):
        if self.dragged_rule_ui:
            block_vec = self.camera.unproject((self.dragged_rule_ui.x, self.dragged_rule_ui.y))
            if self.trash_sprite.rect.intersection(arcade.LBWH(block_vec.x, block_vec.y, 280, 44)) and not self.trash_sprite._current_keyframe_index == self.trash_sprite.animation.num_frames - 1:
                self.trash_sprite.update_animation()
        else:
            self.trash_sprite.time = 0
            self.trash_sprite.update_animation()

