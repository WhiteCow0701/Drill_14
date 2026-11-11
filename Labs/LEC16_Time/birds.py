from collections import deque
from math import exp

from pico2d import get_canvas_height, get_canvas_width, load_image

import game_framework


SPRITE_COLUMNS = 5
SPRITE_ROWS = 3
FRAME_COUNT = 14
CELL_WIDTH = 183
CELL_HEIGHT = 168
IMAGE_HEIGHT = 506

BIRD_COUNT = 10
FORMATION_GAP = 62.0
FOLLOW_DELAY = 0.12
FOLLOW_STEERING = 7.0
CRUISE_SPEED = 125.0
TURN_ACCELERATION = 3.5
EDGE_MARGIN = 70.0
DRAW_WIDTH = 100
DRAW_HEIGHT = 92


class Bird:
    image = None

    def __init__(self, x, y, index):
        if Bird.image is None:
            Bird.image = load_image('bird_animation.png')
        self.x = x
        self.y = y
        self.index = index
        self.frame = index % FRAME_COUNT
        self.direction = 1

    def update_animation(self, frame_time):
        self.frame = (self.frame + 8.0 * frame_time) % FRAME_COUNT

    def draw(self):
        frame = int(self.frame)
        row, column = divmod(frame, SPRITE_COLUMNS)
        source_x = column * CELL_WIDTH
        source_y = IMAGE_HEIGHT - (row + 1) * CELL_HEIGHT
        flip = '' if self.direction == 1 else 'h'
        self.image.clip_composite_draw(
            source_x,
            source_y,
            CELL_WIDTH,
            CELL_HEIGHT,
            0,
            flip,
            self.x,
            self.y,
            DRAW_WIDTH,
            DRAW_HEIGHT,
        )


class BirdFlock:
    def __init__(self):
        canvas_width = get_canvas_width()
        canvas_height = get_canvas_height()
        self.elapsed = 0.0
        self.direction = 1
        self.velocity_x = CRUISE_SPEED
        self.left_bound = EDGE_MARGIN
        self.right_bound = max(
            self.left_bound,
            canvas_width - EDGE_MARGIN,
        )
        leader_x = min(
            self.right_bound,
            self.left_bound + FORMATION_GAP * (BIRD_COUNT - 1),
        )
        leader_y = canvas_height * 0.68
        self.leader_y = leader_y
        self.birds = [
            Bird(leader_x, leader_y, index)
            for index in range(BIRD_COUNT)
        ]
        self.trail = deque(maxlen=240)
        self.trail.append((self.elapsed, leader_x, leader_y))

        for index, bird in enumerate(self.birds[1:], start=1):
            bird.x = leader_x - FORMATION_GAP * index
            bird.y = leader_y + self.formation_y(index)

    @staticmethod
    def formation_y(index):
        offsets = (0.0, 24.0, -24.0, 48.0, -48.0)
        return offsets[index % len(offsets)]

    def update_direction(self, leader):
        if leader.x >= self.right_bound:
            leader.x = self.right_bound
            self.direction = -1
        elif leader.x <= self.left_bound:
            leader.x = self.left_bound
            self.direction = 1

    def sample_trail(self, target_time):
        for timestamp, x, y in reversed(self.trail):
            if timestamp <= target_time:
                return x, y
        _, x, y = self.trail[0]
        return x, y

    def update(self):
        frame_time = game_framework.frame_time
        self.elapsed += frame_time
        leader = self.birds[0]
        self.update_direction(leader)

        target_velocity = self.direction * CRUISE_SPEED
        turn_factor = min(1.0, TURN_ACCELERATION * frame_time)
        self.velocity_x += (target_velocity - self.velocity_x) * turn_factor
        leader.x += self.velocity_x * frame_time
        leader.y = self.leader_y
        leader.direction = self.direction
        leader.update_animation(frame_time)

        self.trail.append((self.elapsed, leader.x, leader.y))
        for index, bird in enumerate(self.birds[1:], start=1):
            target_time = self.elapsed - FOLLOW_DELAY * index
            trail_x, trail_y = self.sample_trail(target_time)
            target_x = trail_x - self.direction * FORMATION_GAP * index
            target_y = trail_y + self.formation_y(index)
            steering = 1.0 - exp(-FOLLOW_STEERING * frame_time)
            bird.x += (target_x - bird.x) * steering
            bird.y += (target_y - bird.y) * steering
            bird.direction = self.direction
            bird.update_animation(frame_time)

    def draw(self):
        for bird in self.birds:
            bird.draw()
