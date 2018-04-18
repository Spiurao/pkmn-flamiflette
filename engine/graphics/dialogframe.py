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
    grammar = "<b>", attr("text", Text), "</b>"

class UnderlineText(pypeg2.List):
    grammar = "<u>", attr("text", Text), "</u>"

class ShakingText(pypeg2.List):
    grammar = "<shaking>", attr("text", Text), "</shaking>"

class StrikeText(pypeg2.List):
    grammar = "<strike>", attr("text", Text), "</strike>"

class ItalicText(pypeg2.List):
    grammar = "<i>", attr("text", Text), "</i>"

class WavingText(pypeg2.List):
    grammar = "<waving>", attr("text", Text), "</waving>"

class SmallText(pypeg2.List):
    grammar = "<small>", attr("text", Text), "</small>"

class BigText(pypeg2.List):
    grammar = "<big>", attr("text", Text), "</big>"

class SlowText(pypeg2.List):
    grammar = "<slow>", attr("text", Text), "</slow>"

class FastText(pypeg2.List):
    grammar = "<fast>", attr("text", Text), "</fast>"

class ColoredText(pypeg2.List):
    grammar = "<color ", pypeg2.Symbol, ">", attr("text", Text), "</color>"

# Ugh not this again
Text.grammar = attr("text", contiguous(maybe_some([SlowText, FastText, SmallText, BigText, ColoredText, WavingText, StrikeText, ShakingText, ItalicText, BoldText, UnderlineText,
                                                   re.compile(r"[^<>*]")])))

class DialogFrame:

    # TODO Add choices here
    # TODO In order : true word wrapping, more rich text rendering, "scrolling", letter by letter rendering, caret at right position
    # TODO Add sound


    LINE_HEIGHT = 40
    DEFAULT_TEXT_COLOR = (0, 0, 0, 0)
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
        self.__caretPosition = (self.__boundaries[2] + self.__boundaries[0] - Frame.PADDING*2, self.__boundaries[3] + self.__boundaries[1] - Frame.PADDING*2, 20, 20)

        # Rich text parsing and rendering
        self.__tree = parse(self.__text, Text)
        self.__lines = [[]]  # list of lines containing a list of things to draw (surface, info about this surface)
        self.__surfaces = []
        self.__states = {}

        self.buildRichText(self.__tree)

        xOffset = 0
        for surface in self.__surfaces:
            if xOffset + surface.get_width() <= self.__boundaries[2] - Frame.FRAME_THICKNESS*2:
                self.__lines[-1].append(surface)
                xOffset += surface.get_width()
            else:
                xOffset = surface.get_width()
                self.__lines.append([])
                self.__lines[-1].append(surface)

    def stateEnabled(self, name):
        return name in self.__states and self.__states[name]

    def buildRichText(self, thing):
        for text in thing.text:
            textType = type(text)
            if textType == str:
                font = FontManager.getFont(DialogFrame.FONT)

                font.set_bold(self.stateEnabled("BoldText"))
                font.set_italic(self.stateEnabled("ItalicText"))
                font.set_underline(self.stateEnabled("UnderlineText"))

                # TODO Add other states

                surface = font.render(text, True, DialogFrame.DEFAULT_TEXT_COLOR)
                self.__surfaces.append(surface)
            else:
                typeStr = textType.__name__
                self.__states[typeStr] = True
                self.buildRichText(text.text)
                self.__states[typeStr] = False

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
        offsetX = 0
        offsetY = 0
        for line in self.__lines:
            for surface in line:
                self.__window.blit(surface, (self.__boundaries[0] + Frame.PADDING + offsetX, self.__boundaries[1] + Frame.PADDING + offsetY))
                offsetX += surface.get_width()
            offsetX = 0
            offsetY += DialogFrame.LINE_HEIGHT



