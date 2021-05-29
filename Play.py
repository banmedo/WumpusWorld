import pygame
import pygame.locals

from src.environment import Environment
from src.utils import log
from src.config import *
from src.renderer import Renderer


def quit(env, renderer):
    env.end_game()
    renderer.show_end_message()


def refresh(env, renderer, state):
    print(state)
    renderer.refresh_world()
    # state = env.check_environment()
    if (not state[1]):
        quit(env, renderer)
    else:
        renderer.show_percept_messages(state)


def startGame(env, renderer):
    state = env.check_environment()
    refresh(env, renderer, state)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Usually wise to be able to close your program.
                raise SystemExit
            elif event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_q):
                   raise SystemExit 
                elif (event.key == pygame.K_r):
                    newGame()
                elif (env.is_game_on()):
                    if event.key == pygame.K_UP:
                        action = "forward"
                    elif event.key == pygame.K_RIGHT:
                        action = "turn_right"
                    elif event.key == pygame.K_LEFT:
                        action = "turn_left"
                    elif event.key == pygame.K_a:
                        action = "grab"
                    elif event.key == pygame.K_s:
                        action = "shoot"
                    elif event.key == pygame.K_w:
                        action = "climb"
                    else:
                        continue
                    
                    refresh(env, renderer, env.perform(action))


def newGame():
    env = Environment(GAME_SETTINGS.SIZE_X, GAME_SETTINGS.SIZE_Y, GAME_SETTINGS.CLIMB_EMPTY, GAME_SETTINGS.PIT_PROB)
    renderer = Renderer(env)
    renderer.refresh_world()
    startGame(env, renderer)


if __name__ == "__main__":
    newGame()
