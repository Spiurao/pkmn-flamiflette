from typing import Tuple, Callable

import pygame
from pygame.surface import Surface

from engine.graphics.fontmanager import FontManager


class DialogRenderer:

    # TODO Add choices here
    # TODO Have a list of texts instead

    # TODO In order : rendering, word wrapping, "scrolling", rich text, letter by letter rendering

    PADDING = 30  # boundary padding on each side, in px

    FONT = "Emerald26Regular"

    def __init__(self, window : Surface, boundaries : Tuple, text : str, endCallback : Callable):
        self.__boundaries = boundaries
        self.__text = text
        self.__endCb = endCallback
        self.__window = window

        self.__firstUpdate = True  # first update should wait for the next frame

        # Loading
        self.__surface = FontManager.getFont(DialogRenderer.FONT).render(self.__text, True, (0, 0, 0, 0))
        self.__caretPosition = (self.__boundaries[2] + self.__boundaries[0] - DialogRenderer.PADDING, self.__boundaries[3] + self.__boundaries[1] - DialogRenderer.PADDING, 20, 20)  # TODO A true caret


    def update(self, dt, events):
        if not self.__firstUpdate:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.__endCb(0)
        self.__firstUpdate = False

    def draw(self):
        # Draw frame
        # TODO A true frame
        pygame.draw.rect(self.__window, (255, 255, 255), self.__boundaries)

        # Draw the caret
        pygame.draw.rect(self.__window, (0, 0, 0), self.__caretPosition)

        # Draw text
        self.__window.blit(self.__surface, (self.__boundaries[0] + DialogRenderer.PADDING, self.__boundaries[1] + DialogRenderer.PADDING))



