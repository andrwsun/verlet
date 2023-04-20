import math
import random
import sys

import pygame

# Initialize pygame
pygame.init()
running = True

# Set up window
window_width = 1200
window_height = 800
background_color = (0, 0, 0)
window = pygame.display.set_mode((window_width, window_height))
window.fill(background_color)
pygame.display.flip()

# fps
clock = pygame.time.Clock()
FPS = 60  # desired frame rate

# Define gravity and bounce values for physics simulation
bounce = 0.1
gravity = 0.23
# Define friction value for points' velocity damping
friction = 0.98


# Define classes for Point, Anchor, and Stick objects
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.oldx = x + random.uniform(-5.5, 10.5)
        self.oldy = y + random.uniform(-5.5, 2.5)
        self.color = (255, 255, 255)
        self.radius = 0


class Anchor:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.start_x = x + 0.1
        self.start_y = y
        self.color = (255, 255, 255)
        self.radius = 3


class Stick:
    def __init__(self, p0, p1):
        self.p0 = p0
        self.p1 = p1
        self.length = get_distance(p0, p1)
        self.color = (255, 255, 255)


# Function to calculate distance between two points
def get_distance(p0, p1):
    dx = p1.x - p0.x
    dy = p1.y - p0.y
    distance = math.sqrt(dx * dx + dy * dy)
    if distance != 0:
        return distance
    else:
        return 0.0000001


# Create lists to hold Anchor, Point, and Stick objects
anchors = []
points = []
sticks = []


# Function to create anchors along the top of the window
def create_anchors(anchors):
    n = 100
    segment = window_width / n
    created_anchors = [Anchor(segment * i, -10) for i in range(9, 89)]
    anchors.extend(created_anchors)


# Create anchors
create_anchors(anchors)


# Function to create points anchored to the anchors and sticks connecting them
def create_anchored_points(points, anchors, sticks):
    created_points = []
    created_sticks = []
    i = 0
    for anchor in anchors:
        created_points.append(Point(anchor.x, anchor.y + 10))
    points += created_points
    for i in range(len(anchors)):
        created_sticks.append(Stick(anchors[i], points[i]))
        if i > 0:
            created_sticks.append(Stick(points[i], points[i - 1]))

        i += 1
    sticks.extend(created_sticks)



create_anchored_points(points, anchors, sticks)


# Function to create fabric connectors (points) that will later on be all connected by sticks
def create_fabric_connectors(points, rows, spacing):
    move = 5
    created_points = []

    for i in range(rows-1):
        for point in points:
            created_points.append(Point(point.x, point.y + 5*i + spacing * move))
    points.extend(created_points)

# Creates rows rows of fabric connectors with 1 spacing
create_fabric_connectors(points, 55, 1)


# Function to connect fabric connectors together with sticks
def connect_fabric_connectors(points, sticks):
    created_sticks = []
    # Connects horizontally
    for i in range(80, len(points) - 1):
        if (i + 1) % 80 != 0:
            created_sticks.append(Stick(points[i], points[i + 1]))
    # Connects vertically
    for i in range(0, len(points) - 80):
        created_sticks.append(Stick(points[i], points[i + 80]))
    sticks.extend(created_sticks)


connect_fabric_connectors(points, sticks)

# Updates and renders all Anchors, Points, and Sticks
def update():

    update_anchors()
    update_points()
    constrain_points()
    update_sticks()
    render_points()
    render_sticks()
    pygame.display.flip()


# Updates Points movements using verlet integration
def update_points():
    for point in points:
        vx = (point.x - point.oldx) * friction  # gets the velocity
        vy = (point.y - point.oldy) * friction

        point.oldx = point.x  # updates old points
        point.oldy = point.y

        point.x += vx  # moves points by x and y
        point.y += vy

        point.y += gravity  # moves point by gravity

# Constrains points within the game screen window
def constrain_points():
    for point in points:
        vx = (point.x - point.oldx) * friction  # * point.mass # gets the velocity
        vy = (point.y - point.oldy) * friction  # * point.a #

        if point.x > window_width:
            point.x = window_width
            point.oldx = point.x + vx * bounce  # calculates the velocity when hitting a wall and slows it by a rate of bounce
        elif point.x < 0:
            point.x = 0
            point.oldx = point.x + vx * bounce  # calculates the velocity when hitting a wall and slows it by a rate of bounce

        if point.y > window_height:

            point.y = window_height
            point.oldy = point.y + vy * bounce  # calculates the velocity when hitting a wall and slows it by a rate of bounce
        elif point.y < 0:
            point.y = 0
            point.oldy = point.y + vy * bounce  # calculates the velocity when hitting a wall and slows it by a rate of bounce

# Ensures that Sticks are the correct length between points
def update_sticks():
    for stick in sticks:
        new_length = get_distance(stick.p0, stick.p1)
        difference = stick.length - new_length
        adjust_percentage = difference / new_length / 2

        offset_x = (stick.p1.x - stick.p0.x) * adjust_percentage  # distance between x0 and x1 * by the adjustment value
        offset_y = (stick.p1.y - stick.p0.y) * adjust_percentage

        stick.p0.x -= offset_x  # adjust the points
        stick.p0.y -= offset_y
        stick.p1.x += offset_x
        stick.p1.y += offset_y

        if new_length >= 100:
            sticks.remove(stick)



# Prevents Anchors from moving
def update_anchors():
    for anchor in anchors:
        anchor.x = anchor.start_x
        anchor.y = anchor.start_y

# Draw all points
def render_points():
    for point in points:
        pygame.draw.circle(window, point.color, (point.x, point.y), point.radius)

# Draw all sticks
def render_sticks():
    for stick in sticks:
        pygame.draw.line(window, stick.color, (stick.p0.x, stick.p0.y), (stick.p1.x, stick.p1.y), 1)



# Adds Point wherever the location clicked and attaches a stick between the two nearest points
def add_point(x, y):
    clicked_x = int(x)
    clicked_y = int(y)
    closest_points = []
    new_point = Point(clicked_x, clicked_y)

    points.append(new_point)

    for point in points:
        distance = get_distance(new_point, point)
        if distance > 0.1:
            if not closest_points or distance <= closest_points[0][0]:
                closest_points.insert(0, (distance, point))
            else:
                closest_points.append((distance, point))

    distances = [distance for distance, _ in closest_points]
    index = distances.index(min(distances))
    distances.append(min(distances))
    closest_points.append((points[index], points[index]))

    point_a = closest_points[0][1]
    point_b = closest_points[1][1]

    sticks.append(Stick(point_a, new_point))
    sticks.append(Stick(new_point, point_b))

# Removes Point wherever the location is clicked
def remove_point(x, y):
    clicked_x = int(x)
    clicked_y = int(y)
    radius = 12
    for point in points:
        if point.x - radius <= clicked_x <= point.x + radius and point.y - radius <= clicked_y <= point.y + radius:
            points.remove(point)
            for stick in reversed(sticks):
                if stick.p0 == point or stick.p1 == point:
                    sticks.remove(stick)

# main loop
right_button_down = False  # Initialize flag for right mouse button state

while running:
    clock.tick(144)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


# Handles mouse events
    pressed_buttons = pygame.mouse.get_pressed()
    if pressed_buttons[0] == 1:  # Left mouse button is held down
        clicked_x, clicked_y = str(pygame.mouse.get_pos()).replace("(", "").replace(")", "").split(",")
        remove_point(clicked_x, clicked_y)
    elif pressed_buttons[2] == 1 and not right_button_down:  # Right mouse button is pressed and not previously down
        clicked_x, clicked_y = str(pygame.mouse.get_pos()).replace("(", "").replace(")", "").split(",")
        add_point(clicked_x, clicked_y)
        right_button_down = True  # Set flag to indicate right mouse button is down
    elif pressed_buttons[2] == 0 and right_button_down:  # Right mouse button is released and previously down
        right_button_down = False  # Reset flag to indicate right mouse button is not down

    update()
    window.fill(background_color)
