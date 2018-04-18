import re
from typing import Tuple, Callable

import pygame
import pypeg2
from pygame.surface import Surface
from pypeg2 import contiguous, attr, parse, word, maybe_some

from engine.graphics.fontmanager import FontManager
from engine.graphics.frame import Frame
from engine.graphics.textures import Textures
from engine.timer import Timer

class Text(pypeg2.List):
    pass

class BoldText(pypeg2.List):
    grammar = "<b>", Text, "</b>"

class UnderlineText(pypeg2.List):
    grammar = "<u>", Text, "</u>"

class ShakingText(pypeg2.List):
    grammar = "<shaking>", Text, "</shaking>"

class StrikeText(pypeg2.List):
    grammar = "<strike>", Text, "</strike>"

class ItalicText(pypeg2.List):
    grammar = "<i>", Text, "</i>"

class WavingText(pypeg2.List):
    grammar = "<waving>", Text, "</waving>"

class SmallText(pypeg2.List):
    grammar = "<small>", Text, "</small>"

class BigText(pypeg2.List):
    grammar = "<big>", Text, "</big>"

class SlowText(pypeg2.List):
    grammar = "<slow>", Text, "</slow>"

class FastText(pypeg2.List):
    grammar = "<fast>", Text, "</fast>"

class ColoredText(pypeg2.List):
    grammar = "<color ", pypeg2.Symbol, ">", Text, "</color>"

# Ugh not this again
Text.grammar = attr("text", contiguous(maybe_some([SlowText, FastText, SmallText, BigText, ColoredText, WavingText, StrikeText, ShakingText, ItalicText, BoldText, UnderlineText,
                                                   re.compile(r"[^<>*]")])))

class DialogFrame:

    # TODO Add choices here
    # TODO Have a list of texts instead

    # TODO In order : rendering, rich text, word wrapping, "scrolling", letter by letter rendering

    # TODO Add sound

    # TODO Move the caret at the end of the text for each "page"

    FONT = "Emerald32Regular"

    CARET_TIMER_DURATION = 100

    def __init__(self, window : Surface, boundaries : Tuple, text : str, endCallback : Callable):
        self.__boundaries = boundaries
        self.__text = text
        self.__endCb = endCallback
        self.__window = window

        self.__firstUpdate = True  # first update should wait for the next frame

        self.__caretTexture = Textures.getTexture("gui.caret")
        self.__caretStep = 0  # the current step in the caret texture
        self.__caretTimer = Timer("caret", DialogFrame.CARET_TIMER_DURATION, self.caretTimerCb)

        # Loading
        self.__frame = Frame(boundaries, self.__window)
        self.__surface = FontManager.getFont(DialogFrame.FONT).render(self.__text, True, (0, 0, 0, 0))
        self.__caretPosition = (self.__boundaries[2] + self.__boundaries[0] - Frame.PADDING*2, self.__boundaries[3] + self.__boundaries[1] - Frame.PADDING*2, 20, 20)

        # Rich text parsing
        self.__tree = parse(self.__text, Text)
        

    def caretTimerCb(self, tag):
        self.__caretStep = (self.__caretStep + 1) % 4
        self.__caretTimer.restart()

    def update(self, dt, events):
        self.__caretTimer.update(dt)

        if not self.__firstUpdate:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.__endCb(0)
        self.__firstUpdate = False

    def draw(self):
        # Draw frame
        self.__frame.draw()

        # Draw the caret
        self.__window.blit(self.__caretTexture, self.__caretPosition, (0, self.__caretStep, 32, 32))

        # Draw text
        self.__window.blit(self.__surface, (self.__boundaries[0] + Frame.PADDING, self.__boundaries[1] + Frame.PADDING))



