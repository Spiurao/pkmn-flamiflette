from typing import Tuple

import pygame
from pygame.surface import Surface

from engine.graphics.textures import Textures


class Frame:

    POSITIONS = {
        "topLeft": (0, 0),
        "bottomLeft" : (0, 2),
        "left": (0, 1),
        "middle": (1, 1),
        "top" : (1, 0),
        "bottom" : (1, 2),
        "topRight" : (2, 0),
        "right" : (2, 1),
        "bottomRight" : (2, 2)
    }

    FILL_COLOR = (255, 255, 255)

    def __init__(self, rect : Tuple, window : Surface):
        self.__rect = rect
        self.__texture = Textures.getTextures()["frame"]
        self.__window = window



    def draw(self):
        pygame.draw.rect(self.__window, (255, 255, 255), self.__rect)