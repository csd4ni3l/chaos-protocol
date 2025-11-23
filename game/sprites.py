import pyglet, arcade.color

from utils.constants import DEFAULT_X_VELOCITY, DEFAULT_Y_VELOCITY

class BaseShape():
    def __init__(self):
        self.shape_type = ""
        self.x_velocity = DEFAULT_X_VELOCITY
        self.y_velocity = DEFAULT_Y_VELOCITY
        self._shape_color = "WHITE"

    def update(self, x_gravity, y_gravity):
        self.x += self.x_velocity
        self.y += self.y_velocity
        self.x -= x_gravity
        self.y -= y_gravity

    @property
    def shape_color(self):
        return self._shape_color
    
    @shape_color.setter
    def shape_color(self, color):
        self._shape_color = color
        self.color = getattr(arcade.color, color)

class Circle(pyglet.shapes.Circle, BaseShape):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        BaseShape.__init__(self)
        self.shape_type = "circle"

    @property
    def shape_size(self):
        return self.radius

class Rectangle(pyglet.shapes.Rectangle, BaseShape):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        BaseShape.__init__(self)
        self.shape_type = "rectangle"

    @property
    def shape_size(self):
        return self.width

class Triangle(pyglet.shapes.Triangle, BaseShape):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        BaseShape.__init__(self)
        self.shape_type = "triangle"

    @property
    def shape_size(self):
        return max(self.x, self.x2, self.x3) - min(self.x, self.x2, self.x3)