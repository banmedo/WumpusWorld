import pygame

from .config import *

class Renderer:
    """This is the interactive renderer for the game.
    """
    def __init__(self, env):
        self.env = env
        
        WIDTH = env.size_x * DIMS.CELL_SIZE
        HEIGHT = env.size_y * DIMS.CELL_SIZE

        pygame.init()
        self.window_surface = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)
        self.window_surface.fill((255,255,255))

    # show in game message
    def show_message(self, message):
        font = pygame.font.Font('freesansbold.ttf', 20)
        text = font.render(message, True, (0,0,0), (255,255,255))
        text_rect = text.get_rect()
        text_rect.center = (self.window_surface.get_width() // 2, self.window_surface.get_height() // 2)
        self.window_surface.blit(text, text_rect)
        pygame.display.flip()

    # show game end message
    def show_end_message(self):
        points = self.env.get_points()
        self.show_message(f"Game Over! your points = {points}")

    # show percept messages
    def show_percept_messages(self, state):
        message = ""
        if (state[2]):
            message = message + "There's a foul smell in the air.\n"
        if (state[3]):
            message = message + "There is a gentle breeze.\n"
        if (state[4]):
            message = message + "The room is sparkling!!\n"
        if (state[5]):
            message = message + "There's a wall there!\n"
        if (state[6]):
            message = message + "A woeful screech can be heard.\n"
        # self.show_message(message)
        print(message)

    # get pixel coordinates from grid x, y
    def get_screen_XY(self, coords):
        return [ coords[0] * DIMS.CELL_SIZE, ( self.env.size_y - coords[1] - 1 ) * DIMS.CELL_SIZE]    

    # refresh the world render
    def refresh_world(self):
        Y = self.env.size_y
        X = self.env.size_x
        # draw world grid
        for y in range(0, Y):
            for x in range (0, X):
                dims = [l * DIMS.CELL_SIZE for l in [x, y, x+1, y+1]]
                # dims = self.get_screen_XY([x,y+1])+self.get_screen_XY([x+1, y])
                pygame.draw.rect(
                    self.window_surface,
                    COLORS.CELL_FILL,
                    pygame.Rect(*dims),
                )
                pygame.draw.rect(
                    self.window_surface,
                    COLORS.CELL_OUTLINE,
                    pygame.Rect(*dims),
                    DIMS.CELL_OUT_WIDTH
                )

        # draw pits
        pits = self.env.pit_locs
        for pit in pits:
            pygame.draw.circle(
                self.window_surface,
                COLORS.PIT,
                [a + DIMS.CELL_SIZE / 2 for a in self.get_screen_XY(pit)],
                DIMS.CELL_SIZE * 1 / 3
            )

        # draw wumpus 
        wumpus = self.env.wumpus.get_location()
        pygame.draw.circle(
            self.window_surface,
            COLORS.WUMPUS,
            [a + DIMS.CELL_SIZE / 2 for a in self.get_screen_XY(wumpus)],
            DIMS.CELL_SIZE * 1 / 4
        )

        # draw agent 
        agent = self.env.agent.get_location()
        agent_center = [a + DIMS.CELL_SIZE / 2 for a in self.get_screen_XY(agent)]
        ax = agent_center[0]
        ay = agent_center[1]
        off = DIMS.CELL_SIZE * 1/5
        poly = [[ax, ay-off], [ax+off, ay], [ax, ay+off], [ax-off, ay]]
        facing = self.env.agent.get_facing()
        ind_del = (facing + 2) % 4
        del(poly[ind_del])
        pygame.draw.polygon(
            self.window_surface,
            COLORS.AGENT,
            poly,
        )

        # draw gold
        if (self.env.agent.has_gold()):
            gold = agent
        else:
            gold = self.env.gold_loc

        pygame.draw.circle(
            self.window_surface,
            COLORS.GOLD,
            [a + DIMS.CELL_SIZE / 2 for a in self.get_screen_XY(gold)],
            DIMS.CELL_SIZE * 1 / 7
        )

        pygame.display.flip()
