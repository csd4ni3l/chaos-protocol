import pyglet

from utils.constants import DEFAULT_X_VELOCITY, DEFAULT_Y_VELOCITY

class BaseShape():
    def __init__(self):
        self.shape_type = ""
        self.x_velocity = DEFAULT_X_VELOCITY
        self.y_velocity = DEFAULT_Y_VELOCITY

    def update(self, gravity):
        self.x += self.x_velocity
        self.y += self.y_velocity
        self.y -= gravity

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
        return self.x2 - self.x