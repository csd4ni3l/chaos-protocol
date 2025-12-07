import pyglet, arcade.color, math, json

# I am so sorry but this file has AI code cause i didn't have enough time to implement collision :C

with open("settings.json", "r") as file:
    settings = json.load(file)

class BaseShape():
    def __init__(self):
        self.shape_type = ""

        self.x_velocity = settings.get("default_x_velocity", 0)
        self.y_velocity = settings.get("default_y_velocity", 0)
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
    
    def check_collision(self, other):
        if isinstance(other, Circle):
            return self._collides_with_circle(other)
        elif isinstance(other, BaseRectangle):
            return self._collides_with_rectangle(other)
        elif isinstance(other, Triangle):
            return self._collides_with_triangle(other)
        return False

class Circle(pyglet.shapes.Circle, BaseShape):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        BaseShape.__init__(self)
        self.shape_type = "circle"
    
    @property
    def shape_size(self):
        return self.radius
    
    def _collides_with_circle(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        distance = math.sqrt(dx * dx + dy * dy)
        return distance < (self.radius + other.radius)
    
    def _collides_with_rectangle(self, rect):
        closest_x = max(rect.x, min(self.x, rect.x + rect.width))
        closest_y = max(rect.y, min(self.y, rect.y + rect.height))
        
        dx = self.x - closest_x
        dy = self.y - closest_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        return distance < self.radius
    
    def _collides_with_triangle(self, tri):
        if self._point_in_triangle(self.x, self.y, tri):
            return True
        
        edges = [
            (tri.x, tri.y, tri.x2, tri.y2),
            (tri.x2, tri.y2, tri.x3, tri.y3),
            (tri.x3, tri.y3, tri.x, tri.y)
        ]
        
        for x1, y1, x2, y2 in edges:
            if self._distance_to_segment(x1, y1, x2, y2) < self.radius:
                return True
        
        return False
    
    def _distance_to_segment(self, x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1
        
        if dx == 0 and dy == 0:
            return math.sqrt((self.x - x1)**2 + (self.y - y1)**2)
        
        t = max(0, min(1, ((self.x - x1) * dx + (self.y - y1) * dy) / (dx * dx + dy * dy)))
        
        closest_x = x1 + t * dx
        closest_y = y1 + t * dy
        
        return math.sqrt((self.x - closest_x)**2 + (self.y - closest_y)**2)
    
    def _point_in_triangle(self, px, py, tri):
        def sign(x1, y1, x2, y2, x3, y3):
            return (x1 - x3) * (y2 - y3) - (x2 - x3) * (y1 - y3)
        
        d1 = sign(px, py, tri.x, tri.y, tri.x2, tri.y2)
        d2 = sign(px, py, tri.x2, tri.y2, tri.x3, tri.y3)
        d3 = sign(px, py, tri.x3, tri.y3, tri.x, tri.y)
        
        has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
        has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
        
        return not (has_neg and has_pos)

class BaseRectangle(BaseShape):
    def __init__(self):
        super().__init__()

    @property
    def shape_size(self):
        return self.width
    
    def _collides_with_circle(self, circle):
        return circle._collides_with_rectangle(self)
    
    def _collides_with_rectangle(self, other):
        return (self.x < other.x + other.width and
                self.x + self.width > other.x and
                self.y < other.y + other.height and
                self.y + self.height > other.y)
    
    def _collides_with_triangle(self, tri):
        vertices = [(tri.x, tri.y), (tri.x2, tri.y2), (tri.x3, tri.y3)]
        for vx, vy in vertices:
            if (self.x <= vx <= self.x + self.width and
                self.y <= vy <= self.y + self.height):
                return True
        
        rect_vertices = [
            (self.x, self.y),
            (self.x + self.width, self.y),
            (self.x + self.width, self.y + self.height),
            (self.x, self.y + self.height)
        ]
        for rx, ry in rect_vertices:
            if self._point_in_triangle(rx, ry, tri):
                return True
        
        tri_edges = [
            (tri.x, tri.y, tri.x2, tri.y2),
            (tri.x2, tri.y2, tri.x3, tri.y3),
            (tri.x3, tri.y3, tri.x, tri.y)
        ]
        rect_edges = [
            (self.x, self.y, self.x + self.width, self.y),
            (self.x + self.width, self.y, self.x + self.width, self.y + self.height),
            (self.x + self.width, self.y + self.height, self.x, self.y + self.height),
            (self.x, self.y + self.height, self.x, self.y)
        ]
        
        for t_edge in tri_edges:
            for r_edge in rect_edges:
                if self._segments_intersect(*t_edge, *r_edge):
                    return True
        
        return False
    
    def _point_in_triangle(self, px, py, tri):
        def sign(x1, y1, x2, y2, x3, y3):
            return (x1 - x3) * (y2 - y3) - (x2 - x3) * (y1 - y3)
        
        d1 = sign(px, py, tri.x, tri.y, tri.x2, tri.y2)
        d2 = sign(px, py, tri.x2, tri.y2, tri.x3, tri.y3)
        d3 = sign(px, py, tri.x3, tri.y3, tri.x, tri.y)
        
        has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
        has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
        
        return not (has_neg and has_pos)
    
    def _segments_intersect(self, x1, y1, x2, y2, x3, y3, x4, y4):
        def ccw(ax, ay, bx, by, cx, cy):
            return (cy - ay) * (bx - ax) > (by - ay) * (cx - ax)
        
        return (ccw(x1, y1, x3, y3, x4, y4) != ccw(x2, y2, x3, y3, x4, y4) and
                ccw(x1, y1, x2, y2, x3, y3) != ccw(x1, y1, x2, y2, x4, y4))

class Rectangle(pyglet.shapes.Rectangle, BaseRectangle):
    def __init__(self, *args, **kwargs):
        BaseRectangle.__init__(self)
        super().__init__(*args, **kwargs)
        self.shape_type = "rectangle"

class TexturedRectangle(pyglet.sprite.Sprite, BaseRectangle):
    def __init__(self, img, x=0, y=0, *args, **kwargs):
        BaseRectangle.__init__(self)
        self.shape_type = kwargs.pop("shape_type", "textured_rectangle")
        super().__init__(img, x, y, *args, **kwargs)

    def update(self, x_gravity, y_gravity):
        BaseShape.update(self, x_gravity, y_gravity)

class Triangle(pyglet.shapes.Triangle, BaseShape):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        BaseShape.__init__(self)
        self.shape_type = "triangle"
    
    @property
    def shape_size(self):
        return max(self.x, self.x2, self.x3) - min(self.x, self.x2, self.x3)
    
    def _collides_with_circle(self, circle):
        return circle._collides_with_triangle(self)
    
    def _collides_with_rectangle(self, rect):
        return rect._collides_with_triangle(self)
    
    def _collides_with_triangle(self, other):
        vertices_self = [(self.x, self.y), (self.x2, self.y2), (self.x3, self.y3)]
        vertices_other = [(other.x, other.y), (other.x2, other.y2), (other.x3, other.y3)]
        
        for vx, vy in vertices_self:
            if self._point_in_triangle(vx, vy, other):
                return True
        
        for vx, vy in vertices_other:
            if self._point_in_triangle(vx, vy, self):
                return True
        
        edges_self = [
            (self.x, self.y, self.x2, self.y2),
            (self.x2, self.y2, self.x3, self.y3),
            (self.x3, self.y3, self.x, self.y)
        ]
        edges_other = [
            (other.x, other.y, other.x2, other.y2),
            (other.x2, other.y2, other.x3, other.y3),
            (other.x3, other.y3, other.x, other.y)
        ]
        
        for e1 in edges_self:
            for e2 in edges_other:
                if self._segments_intersect(*e1, *e2):
                    return True
        
        return False
    
    def _point_in_triangle(self, px, py, tri):
        def sign(x1, y1, x2, y2, x3, y3):
            return (x1 - x3) * (y2 - y3) - (x2 - x3) * (y1 - y3)
        
        d1 = sign(px, py, tri.x, tri.y, tri.x2, tri.y2)
        d2 = sign(px, py, tri.x2, tri.y2, tri.x3, tri.y3)
        d3 = sign(px, py, tri.x3, tri.y3, tri.x, tri.y)
        
        has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
        has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
        
        return not (has_neg and has_pos)
    
    def _segments_intersect(self, x1, y1, x2, y2, x3, y3, x4, y4):
        def ccw(ax, ay, bx, by, cx, cy):
            return (cy - ay) * (bx - ax) > (by - ay) * (cx - ax)
        
        return (ccw(x1, y1, x3, y3, x4, y4) != ccw(x2, y2, x3, y3, x4, y4) and
                ccw(x1, y1, x2, y2, x3, y3) != ccw(x1, y1, x2, y2, x4, y4))