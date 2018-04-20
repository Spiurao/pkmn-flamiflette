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
                                                   re.compile(r"[^<>]")])))

class TextChunk:
    def __init__(self):
        self.text = ""
        self.surface = None
        self.state = {}

class DialogFrame:

    # TODO Add choices here
    # TODO In order : caret ar right position, more rich text rendering, "scrolling", letter by letter rendering
    # TODO Add sound

    LINE_HEIGHT = 40
    DEFAULT_TEXT_COLOR = (0, 0, 0, 0)
    FONT = "Dialog"

    Y_OFFSET = -4

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

        self.__font = FontManager.getFont(DialogFrame.FONT)

        self.__linesMax = int((self.__boundaries[3] - Frame.PADDING * 2) / (self.__font.size("H")[1]))

        # Loading
        self.__frame = Frame(boundaries, self.__window)
        self.__caretPosition = (self.__boundaries[2] + self.__boundaries[0] - Frame.PADDING*2, self.__boundaries[3] + self.__boundaries[1] - Frame.PADDING*2, 20, 20)

        # Rich text parsing and rendering
        self.__tree = parse(self.__text, Text)
        self.__states = {}
        self.__stateChanged = True

        self.__textChunks = []  # list of TextChunk instances
        self.__wrappedTextChunks = [[]]

        self.__currentLine = 0
        self.__alive = True

        self.buildChunks(self.__tree)  # fills textChunks
        self.wordWrap()  # fills wrappedTextChunks
        self.renderText()  # fills wrappedTextChunks surfaces

    def setFontProperties(self, state):
        self.__font.set_italic(self.stateEnabled(state, "Italic"))
        self.__font.set_underline(self.stateEnabled(state, "Underline"))
        self.__font.set_bold(self.stateEnabled(state, "Bold"))

    def renderText(self):
        for line in self.__wrappedTextChunks:
            for chunk in line:
                self.setFontProperties(chunk.state)

                # TODO Add other states here

                chunk.surface = self.__font.render(chunk.text, True, DialogFrame.DEFAULT_TEXT_COLOR)

    def wordWrap(self):
        xOffset = 0
        for chunk in self.__textChunks:
            self.setFontProperties(chunk.state)

            text = ""

            words = chunk.text.split(" ")
            for word in words:
                word = word + " "
                wordLength = self.__font.size(word)[0]

                if wordLength + xOffset <= self.__boundaries[2] - Frame.PADDING * 2:
                    text += word
                    xOffset += wordLength
                else:
                    text = text[:-1]
                    if text != "":
                        newChunk = TextChunk()
                        newChunk.text = text
                        newChunk.state = chunk.state
                        self.__wrappedTextChunks[-1].append(newChunk)

                    self.__wrappedTextChunks.append([])

                    text = word
                    xOffset = wordLength

            text = text[:-1]

            if text != "":
                newChunk = TextChunk()
                newChunk.text = text
                newChunk.state = chunk.state
                self.__wrappedTextChunks[-1].append(newChunk)

    def stateEnabled(self, state, name):
        return name in state and state[name]

    def buildChunks(self, thing):
        for text in thing.text:
            textType = type(text)
            if textType == str:
                if self.__stateChanged:
                    chunk = TextChunk()
                    chunk.state = {**self.__states}
                    self.__textChunks.append(chunk)
                    self.__stateChanged = False

                self.__textChunks[-1].text += text
            else:
                typeStr = textType.__name__[:-4]

                self.__stateChanged = True
                self.__states[typeStr] = True

                self.buildChunks(text.text)

                self.__stateChanged = True
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
                        self.__currentLine += self.__linesMax
                        if self.__currentLine > len(self.__wrappedTextChunks):
                            self.__alive = False
                            self.__endCb(0)
        self.__firstUpdate = False

    def draw(self):
        if not self.__alive:
            return

        # Draw frame
        self.__frame.draw()

        # Draw the caret
        self.__window.blit(self.__caretTexture, self.__caretPosition, (0, self.__caretStep, 32, 32))

        # Draw text
        yOffset = 0
        xOffset = 0
        for line in self.__wrappedTextChunks[self.__currentLine:self.__currentLine+self.__linesMax]:
            for chunk in line:
                self.__window.blit(chunk.surface, (self.__boundaries[0] + Frame.PADDING + xOffset, self.__boundaries[1] + Frame.PADDING + yOffset + DialogFrame.Y_OFFSET))
                xOffset += chunk.surface.get_width()
            yOffset += DialogFrame.LINE_HEIGHT
            xOffset = 0



