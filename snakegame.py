import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

pygame.init()

font = pygame.font.Font('arial.ttf', 25)

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

Point = namedtuple('Point', 'x, y')

WHITE = (255, 255, 255)
BLACK = (0,0,0)
BLUE = (0,0,255)
BLUE1 = (0,100,255)
RED = (255,0,0)

Blocksize = 20
Speed = 200

class SnakeGameAI:

    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h
        self.reset()
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Game')
        self.clock = pygame.time.Clock()

    def reset(self):
        self.direction = Direction.RIGHT
        self.head = Point(self.w/2, self.h/2)
        self.snake =  [ self.head, 
                            Point(self.head.x - Blocksize, self.head.y),
                            Point(self.head.x - (2*Blocksize), self.head.y) ]
        self.score = 0
        self.food = None
        self._place_food()
        self.frame_iteration = 0

    def play_step(self, action):

        self.frame_iteration += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        self._move(action)
        self.snake.insert(0, self.head)
        reward = 0

        game_over = False

        if self.is_collision() or self.frame_iteration > 100*len(self.snake):
            game_over = True
            reward = -10
            return reward, game_over, self.score

        if self.head == self.food:
            self.score += 1
            reward = 10
            self._place_food()
        else:
            self.snake.pop()

        self._update_ui()
        self.clock.tick(Speed)
        return reward, game_over, int(self.score)

    def _place_food(self):
        x = random.randint(0, (self.w - Blocksize)//Blocksize)*Blocksize
        y = random.randint(0, (self.h - Blocksize)//Blocksize)*Blocksize
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()
    
    def _update_ui(self):
        self.display.fill(BLACK)
        for pt in self.snake:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, Blocksize, Blocksize))
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, (Blocksize-8), (Blocksize-8)))

        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, Blocksize, Blocksize))

        text = font.render("Score: "+ str(self.score), True, WHITE)
        self.display.blit(text, [0,0])
        pygame.display.flip()

    def is_collision(self, pt=None):
        pt = self.head
        if pt.x > self.w - Blocksize or pt.x < 0 or pt.y > self.h - Blocksize or pt.y < 0:
            return True
        if pt in self.snake[1:]:
            return True
        return False

    def _move(self, action):

        clockwise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clockwise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):
            new_direction = clockwise[idx]
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4
            new_direction = clockwise[next_idx]
        elif np.array_equal(action, [0,0,1]):
            next_idx = (idx - 1) % 4
            new_direction = clockwise[next_idx]
        
        self.direction = new_direction
    
        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT:
            x += Blocksize
        elif self.direction == Direction.LEFT:
            x -= Blocksize
        elif self.direction == Direction.UP:
            y -= Blocksize
        elif self.direction == Direction.DOWN:
            y += Blocksize
        self.head = Point(x, y)

  