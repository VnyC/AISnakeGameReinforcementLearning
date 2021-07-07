from typing_extensions import final
from numpy.lib.function_base import append
import torch
import random
import numpy as np
from collections import deque
from snakegame import Blocksize, SnakeGameAI, Point, Direction
from model import Linera_QNet, QTrainer
from helper import plot
import sys

sys.setrecursionlimit(1500)

MaxMemory = 100000
BatchSize = 1000
LR = 0.001
Gamma = 0.9
model_input_size = 11
model_hidden_layer_size = 256
model_output_size = 3

class Agent:
    def __init__(self):
        self.n_games = 0
        self.epsilon = 0
        self.gamma = Gamma
        self.memory = deque(maxlen=MaxMemory)
        self.model = Linera_QNet(model_input_size, model_hidden_layer_size, model_output_size)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)
        self.circle_move = []

    def get_state(self, game):
        head = game.snake[0]
        point_l = Point(head.x - Blocksize, head.y)
        point_r = Point(head.x + Blocksize, head.y)
        point_u = Point(head.x, head.y - Blocksize)
        point_d = Point(head.x, head.y + Blocksize)

        dir_l = game.direction == Direction.LEFT
        dir_r = game.direction == Direction.RIGHT
        dir_u = game.direction == Direction.UP
        dir_d = game.direction == Direction.DOWN

        state = [
            (dir_l and game.is_collision(point_l)) or
            (dir_r and game.is_collision(point_r)) or
            (dir_u and game.is_collision(point_u)) or
            (dir_d and game.is_collision(point_d)),
            
            (dir_l and game.is_collision(point_u)) or
            (dir_r and game.is_collision(point_d)) or
            (dir_u and game.is_collision(point_r)) or
            (dir_d and game.is_collision(point_l)),

            (dir_l and game.is_collision(point_d)) or
            (dir_r and game.is_collision(point_u)) or
            (dir_u and game.is_collision(point_l)) or
            (dir_d and game.is_collision(point_r)),

            dir_l,
            dir_r,
            dir_u,
            dir_d,

            game.food.x < game.head.x,
            game.food.x > game.head.x,
            game.food.y < game.head.y,
            game.food.y > game.head.y
        ]

        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))


    def train_long_memory(self):
        if len(self.memory) > BatchSize:
            mini_sample = random.sample(self.memory, BatchSize)
        else:
            mini_sample = self.memory
        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        self.epsilon = 80 - self.n_games
        final_move = [0,0,0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0,2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype = torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1
        # self.circle_move.insert(0, final_move)
        # if len(self.circle_move) > 2:
        #     final_move = self.circle_movement(state, self.circle_move, final_move)
        #     self.circle_move.pop()
        return final_move

            

def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = SnakeGameAI()
    while True:
        old_state = agent.get_state(game)
        final_move = agent.get_action(old_state)
        reward, game_over, score = game.play_step(final_move)
        new_state = agent.get_state(game)
        agent.train_short_memory(old_state, final_move, reward, new_state, game_over)
        agent.remember(old_state, final_move, reward, new_state, game_over)

        if game_over:
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()

            if score > record:
                record = score
                agent.model.save()

            print("Game number ", agent.n_games, " Current score ", score, " Record ", record)
            
            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)


if __name__ == '__main__':
    train()