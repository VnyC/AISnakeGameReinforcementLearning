import pygame
import random
from enum import Enum
from collections import namedtuple

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
Speed = 10

class SnakeGame:

    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Game')
        self.clock = pygame.time.Clock()

        self.direction = Direction.RIGHT

        self.head = Point(self.w/2, self.h/2)
        self.snake =  [ self.head, 
                            Point(self.head.x - Blocksize, self.head.y),
                            Point(self.head.x - (2*Blocksize), self.head.y) ]

        self.score = 0
        self.food = None

        self._place_food()

    def _place_food(self):
        x = random.randint(0, (self.w - Blocksize)//Blocksize)*Blocksize
        y = random.randint(0, (self.h - Blocksize)//Blocksize)*Blocksize
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()

    def play_step(self):

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.direction = Direction.LEFT
                elif event.key == pygame.K_RIGHT:
                    self.direction = Direction.RIGHT
                elif event.key == pygame.K_UP:
                    self.direction = Direction.UP
                elif event.key == pygame.K_DOWN:
                    self.direction = Direction.DOWN
        
        self._move(self.direction)
        self.snake.insert(0, self.head)

        game_over = False
        if self._is_collision():
            game_over = True
            return game_over, self.score

        if self.head == self.food:
            self.score += 1
            self._place_food()
        else:
            self.snake.pop()

        self._update_ui()
        self.clock.tick(Speed)

        return game_over, self.score
    
    def _update_ui(self):
        self.display.fill(BLACK)
        for pt in self.snake:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, Blocksize, Blocksize))
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, (Blocksize-8), (Blocksize-8)))

        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, Blocksize, Blocksize))

        text = font.render("Score: "+ str(self.score), True, WHITE)
        self.display.blit(text, [0,0])
        pygame.display.flip()

    def _is_collision(self):
        if self.head.x > self.w - Blocksize or self.head.x < 0 or self.head.y > self.h - Blocksize or self.head.y < 0:
            return True
        if self.head in self.snake[1:]:
            return True
        return False

    def _move(self, direction):
        x = self.head.x
        y = self.head.y
        if direction == Direction.RIGHT:
            x += Blocksize
        elif direction == Direction.LEFT:
            x -= Blocksize
        elif direction == Direction.UP:
            y -= Blocksize
        elif direction == Direction.DOWN:
            y += Blocksize
        self.head = Point(x, y)


if __name__ == '__main__':
    game = SnakeGame()

    while True:
        game_over, score = game.play_step()

        if game_over == True:
            break

    print('Opps Game Khallas, Your Score: ', score)


    pygame.quit
    