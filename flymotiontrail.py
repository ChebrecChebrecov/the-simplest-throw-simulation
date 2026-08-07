import tkinter as tk
import math
PPM = 10
G = 9.8
class Drawable:
    def __init__(self, canvas):
        self.canvas = canvas
        self.id = None
        self.parts = []
    def draw(self):
        pass
class Updatable:
    def update(self, dt):
        pass
class Hittable:
    def check_hit(self, other):
        pass
class Point:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
class Rectangle(Point):
    def __init__(self, x, y, width, height, color="red"):
        super().__init__(x, y)
        self.width = width
        self.height = height
        self.color = color
    def get_coords(self):
        return (self.x, self.y, self.x + self.width, self.y + self.height)
class Rect(Drawable, Updatable, Hittable):
    def __init__(self, canvas, x, y, width, height, color="red"):
        Drawable.__init__(self, canvas)
        self.rect = Rectangle(x, y, width, height, color)
        self.draw()
    def draw(self):
        coords = self.rect.get_coords()
        self.id = self.canvas.create_rectangle(*coords, fill=self.rect.color)
    def update(self, dt):
        pass
    def check_hit(self, other):
        if not isinstance(other, Ball):
            return None
        obj_x = other.pos.x * PPM
        obj_y = other.pos.y * PPM
        r = other.radius * PPM
        closest_x = max(self.rect.x, min(obj_x, self.rect.x + self.rect.width))
        closest_y = max(self.rect.y, min(obj_y, self.rect.y + self.rect.height))
        dx = obj_x - closest_x
        dy = obj_y - closest_y
        distance = math.hypot(dx, dy)
        if distance < r:
            if abs(dx) > abs(dy):
                return "horizontal"
            else:
                return "vertical"
        return None
    def move_to(self, x, y):
        self.rect.x = x
        self.rect.y = y
        self.canvas.coords(self.id, *self.rect.get_coords())
class Ball(Drawable, Updatable, Hittable):
    def __init__(self, canvas, x, y, radius=0.02):
        Drawable.__init__(self, canvas)
        self.pos = Point(3.0, 78.0)
        self.vel = Point(10.0, -35.0)
        self.k = 0.003
        self.radius = radius
        self.on_ground = False
        self.acc = Point(0, 0)
        self.update_acceleration()
        self.trail = 0
        self.draw()
    def update_acceleration(self):
        speed = math.hypot(self.vel.x, self.vel.y)
        drag_coeff = self.k * speed
        self.acc.x = -drag_coeff * self.vel.x
        self.acc.y = G - drag_coeff * self.vel.y
    def draw(self):
        for part_id in self.parts:
            self.canvas.delete(part_id)
        self.parts = []
        x = self.pos.x * PPM
        y = self.pos.y * PPM
        r = self.radius * PPM
        body = self.canvas.create_oval(x - r, y - r, x + r, y + r, fill='purple')
        self.parts.append(body)
        self.id = body
        self.trail +=1
        if self.trail > 20:
            body = self.canvas.create_oval(x, y, x + 0.01, y + 0.01, fill='red')
            self.trail = 0
    def update(self, dt):
        self.update_acceleration()
        self.vel.x += self.acc.x * dt
        self.vel.y += self.acc.y * dt
        self.pos.x += self.vel.x * dt + 0.5 * self.acc.x * dt * dt
        self.pos.y += self.vel.y * dt + 0.5 * self.acc.y * dt * dt
        field_width = 2000 / PPM
        field_height = 1000 / PPM
        if self.pos.x < self.radius:
            self.pos.x = self.radius
            self.vel.x = -self.vel.x * 0
        elif self.pos.x > field_width - self.radius:
            self.pos.x = field_width - self.radius
            self.vel.x = -self.vel.x * 0
        if self.pos.y > field_height - self.radius:
            self.pos.y = field_height - self.radius
            self.vel.y = -self.vel.y * 0
            self.on_ground = True
        elif self.pos.y < self.radius:
            self.pos.y = self.radius
            self.vel.y = -self.vel.y * 0
        self.draw()
    def check_hit(self, other):
        if isinstance(other, Ball):
            other_x = other.pos.x
            other_y = other.pos.y
            other_r = other.radius
        else:
            other_x = other.pos.x
            other_y = other.pos.y
            other_r = other.radius
        dx = self.pos.x - other_x
        dy = self.pos.y - other_y
        distance = math.hypot(dx, dy)
        if distance < self.radius + other_r:
            if abs(dx) > abs(dy):
                return "horizontal"
            else:
                return "vertical"
        return None
    def bounce(self, rect, side):
        if side == "horizontal":
            self.vel.x = -self.vel.x / 2
            if self.pos.x * PPM < rect.rect.x:
                self.pos.x = (rect.rect.x - self.radius * PPM) / PPM
            else:
                self.pos.x = (rect.rect.x + rect.rect.width + self.radius * PPM) / PPM
        elif side == "vertical":
            self.vel.x = 0
            if self.vel.y > 0:
                self.vel.y = 0
                self.acc.x = 0
            if self.pos.y * PPM < rect.rect.y:
                self.pos.y = (rect.rect.y - self.radius * PPM) / PPM
                self.on_ground = True
            else:
                self.pos.y = (rect.rect.y + rect.rect.height + self.radius * PPM) / PPM
        self.update_acceleration()
root = tk.Tk()
root.title("FlyMotion")
canvas = tk.Canvas(root, width=2000, height=1000, bg='white')
canvas.pack()
drawables = []
updatables = []
hittables = []
time_text = canvas.create_text(300, 200, text=" ", font=('Times New Roman', 12), fill="blue")
dt = 1 / 500
ball = 0
def create_walls():
    walls = [(0, 800, 2000, 200)]
    for x, y, w, h in walls:
        wall = Rect(canvas, x, y, w, h, color='green')
        drawables.append(wall)
        hittables.append(wall)
def create_ball():
    global ball
    ball = Ball(canvas, 500, 400, radius=0.2)
    drawables.append(ball)
    updatables.append(ball)
    hittables.append(ball)
def update():
    for obj in updatables:
        obj.update(dt)
    if ball:
        for obj in hittables:
            if obj is ball:
                continue
            side = obj.check_hit(ball)
            if side:
                ball.bounce(obj, side)
        height_m = 100 - ball.pos.y
        canvas.itemconfig(time_text, text=f"X: {ball.pos.x:.2f} м, Y: {height_m:.2f} м, Vx: {ball.vel.x:.2f}, Vy: {ball.vel.y:.2f}")
        root.after(1, update)
canvas.focus_set()
create_walls()
create_ball()
update()
root.mainloop()