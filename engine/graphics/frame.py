from typing import Tuple

import pygame
from pygame.surface import Surface

from engine.graphics.textures import Textures


class Frame:

    TILE_SIZE = 44

    COORDS = {
        "topLeft": (0, 0),
        "bottomLeft": (0, 84),
        "left": (0, 42),
        "top": (42, 0),
        "bottom": (42, 84),
        "topRight": (84, 0),
        "right": (84, 42),
        "bottomRight": (84, 84)
    }

    FRAME_THICKNESS = 20  # changes the size of the color filling
    PADDING = FRAME_THICKNESS + 10  # not used in this class

    FILL_COLOR = (248, 248, 248)

    def __init__(self, rect : Tuple, window : Surface):
        self.__rect = rect
        self.__texture = Textures.getTexture("gui.frame")
        self.__window = window

        self.__size = (self.__rect[2], self.__rect[3])
        self.__pos = (self.__rect[0], self.__rect[1])

        self.__surface = pygame.Surface(self.__size, pygame.SRCALPHA, 32)

        #Middle
        pygame.draw.rect(self.__surface, Frame.FILL_COLOR, (Frame.FRAME_THICKNESS, Frame.FRAME_THICKNESS, self.__size[0] - Frame.FRAME_THICKNESS*2, self.__size[1] - Frame.FRAME_THICKNESS*2))

        #Sides
        # X
        draw = Frame.TILE_SIZE
        while draw < self.__size[0] - Frame.TILE_SIZE:
            self.__surface.blit(self.__texture, (draw, 0), Frame.COORDS["top"] + (Frame.TILE_SIZE, Frame.TILE_SIZE))
            self.__surface.blit(self.__texture, (draw, self.__size[1] - Frame.TILE_SIZE), Frame.COORDS["bottom"] + (Frame.TILE_SIZE, Frame.TILE_SIZE))
            draw += Frame.TILE_SIZE

        # Y
        draw = Frame.TILE_SIZE
        while draw < self.__size[1] - Frame.TILE_SIZE:
            self.__surface.blit(self.__texture, (0, draw), Frame.COORDS["left"] + (Frame.TILE_SIZE, Frame.TILE_SIZE))
            self.__surface.blit(self.__texture, (self.__size[0] - Frame.TILE_SIZE, draw), Frame.COORDS["right"] + (Frame.TILE_SIZE, Frame.TILE_SIZE))
            draw += Frame.TILE_SIZE

        #Corners
        self.__surface.blit(self.__texture, (0, 0), Frame.COORDS["topLeft"] + (Frame.TILE_SIZE, Frame.TILE_SIZE))
        self.__surface.blit(self.__texture, (self.__size[0] - Frame.TILE_SIZE, 0), Frame.COORDS["topRight"] + (Frame.TILE_SIZE, Frame.TILE_SIZE))
        self.__surface.blit(self.__texture, (0, self.__size[1] - Frame.TILE_SIZE), Frame.COORDS["bottomLeft"] + (Frame.TILE_SIZE, Frame.TILE_SIZE))
        self.__surface.blit(self.__texture, (self.__size[0] - Frame.TILE_SIZE, self.__size[1] - Frame.TILE_SIZE), Frame.COORDS["bottomRight"] + (Frame.TILE_SIZE, Frame.TILE_SIZE))

    def draw(self):
        self.__window.blit(self.__surface, self.__pos)