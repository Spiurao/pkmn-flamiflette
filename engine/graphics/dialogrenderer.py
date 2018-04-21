import random
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
from engine.tween.easing import Easing
from engine.tween.tween import Tween
from engine.tween.tweensubject import TweenSubject


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
        self.yOffset = 0  # used to compensate the big and small text size
        self.animationXOffset = TweenSubject(0)  # used to animate letters
        self.animationYOffset = TweenSubject(0)

class DialogRenderer:

    # TODO Add choices here
    # TODO In order : more rich text rendering, "scrolling", letter by letter rendering
    # TODO Add sound

    STATE_PARSING = 0
    STATE_CHUNKING = 1
    STATE_WRAPPING = 2
    STATE_READY = 3

    LINE_HEIGHT = 40
    DEFAULT_TEXT_COLOR = (0, 0, 0, 0)
    FONT = "Dialog"

    Y_OFFSET = -4

    CARET_TIMER_DURATION = 100
    SHAKING_TIMER_DURATION = 20
    WAVING_TIMER_DURATION = 400

    WAVING_X_AMPLITUDE = 3
    WAVING_Y_AMPLITUDE = 8
    WAVING_OFFSET = 10  # ms offset between each letter

    def __init__(self, window : Surface, frame : Frame, text : str, endCallback : Callable):
        self.__boundaries = frame.rect
        self.__text = text
        self.__endCb = endCallback
        self.__window = window

        self.__caretTexture = Textures.getTexture("gui.caret")
        self.__caretStep = 0  # the current step in the caret texture
        self.__caretTimer = Timer("caret", DialogRenderer.CARET_TIMER_DURATION, self.caretTimerCb)
        self.__shakingTimer = Timer("shaking", DialogRenderer.SHAKING_TIMER_DURATION, self.shakingTimerCb)

        self.__regularFont = FontManager.getFont(DialogRenderer.FONT + "Regular")
        self.__smallFont = FontManager.getFont(DialogRenderer.FONT + "Small")
        self.__bigFont = FontManager.getFont(DialogRenderer.FONT + "Big")

        self.__font = self.__regularFont

        self.__linesMax = int((self.__boundaries[3] - Frame.PADDING * 2) / (self.__font.size("H")[1]))

        self.__frame = frame

        self.__state = DialogRenderer.STATE_PARSING

        self.__states = {}
        self.__stateChanged = True

        self.__textChunks = []  # list of TextChunk instances
        self.__wrappedTextChunks = [[]]

        self.__currentLine = 0
        self.__alive = True

        self.__shakingChunks = []
        self.__wavingChunksTweens = []

    def shakingTimerCb(self, tag):
        for chunk in self.__shakingChunks:
            chunk.animationXOffset.value = random.randint(-2, 2)
            chunk.animationYOffset.value = random.randint(-2, 2)
        self.__shakingTimer.restart()

    def setFontProperties(self, state):
        if self.stateEnabled(state, "Big"):
            self.__font = self.__bigFont
        elif self.stateEnabled(state, "Small"):
            self.__font = self.__smallFont
        else:
            self.__font = self.__regularFont

        self.__font.set_italic(self.stateEnabled(state, "Italic"))
        self.__font.set_underline(self.stateEnabled(state, "Underline"))
        self.__font.set_bold(self.stateEnabled(state, "Bold"))

    def createNewChunk(self, chunk, text):
        newChunk = TextChunk()
        newChunk.text = text
        newChunk.state = chunk.state
        newChunk.yOffset = chunk.yOffset
        newChunk.animationXOffset = TweenSubject(chunk.animationXOffset.value)
        newChunk.animationYOffset = TweenSubject(chunk.animationYOffset.value)
        newChunk.surface = self.__font.render(newChunk.text, True, DialogRenderer.DEFAULT_TEXT_COLOR)
        return newChunk

    def createNewChunks(self, chunk, text):
        if self.stateEnabled(chunk.state, "Shaking"):
            list = []
            for letter in text:
                newChunk = self.createNewChunk(chunk, letter)
                self.__shakingChunks.append(newChunk)
                list.append(newChunk)
            return list
        elif self.stateEnabled(chunk.state, "Waving"):
            list = []
            letterIndex = 0
            for letter in text:
                newChunk = self.createNewChunk(chunk, letter)
                newChunk.animationXOffset.value = -DialogRenderer.WAVING_X_AMPLITUDE
                newChunk.animationYOffset.value = -DialogRenderer.WAVING_Y_AMPLITUDE

                xtween = Tween(None, newChunk.animationXOffset, DialogRenderer.WAVING_X_AMPLITUDE, DialogRenderer.WAVING_TIMER_DURATION, Easing.easingInOutSine, None)
                xtween.runningSince = xtween.duration/2  # fast forward half the time to offset X and Y animations

                ytween = Tween(None, newChunk.animationYOffset, DialogRenderer.WAVING_Y_AMPLITUDE, DialogRenderer.WAVING_TIMER_DURATION, Easing.easingInOutSine, None)

                xtween.runningSince += DialogRenderer.WAVING_OFFSET * letterIndex
                ytween.runningSince += DialogRenderer.WAVING_OFFSET * letterIndex

                self.__wavingChunksTweens.append(xtween)
                self.__wavingChunksTweens.append(ytween)
                list.append(newChunk)
                letterIndex += 1
            return list
        else:
            return [self.createNewChunk(chunk, text)]

    def wordWrap(self):
        xOffset = 0
        for chunk in self.__textChunks:
            self.setFontProperties(chunk.state)

            text = ""

            words = chunk.text.split(" ")
            for word in words:
                word = word + " "
                wordLength = self.__font.size(word)[0]

                isCarriageReturn = word[0:1] == "\n"
                isPageBreak = word[0:1] == "\t"

                if (wordLength + xOffset <= self.__boundaries[2] - Frame.PADDING * 2) and not (isCarriageReturn or isPageBreak):
                    text += word
                    xOffset += wordLength
                else:
                    if not (isCarriageReturn or isPageBreak):
                        text = text[:-1]
                        if text != "":
                            newChunk = self.createNewChunks(chunk, text)
                            self.__wrappedTextChunks[-1].extend(newChunk)

                    if not isPageBreak:
                        self.__wrappedTextChunks.append([])
                    else:
                        for x in range(0, (self.__linesMax - len(self.__wrappedTextChunks) % self.__linesMax) + 1):
                            self.__wrappedTextChunks.append([])

                    if not (isCarriageReturn or isPageBreak):
                        text = word
                        xOffset = wordLength
                    else:
                        text = ""
                        xOffset = 0

            text = text[:-1]

            if text != "":
                newChunk = self.createNewChunks(chunk, text)
                self.__wrappedTextChunks[-1].extend(newChunk)

    def stateEnabled(self, state, name):
        return name in state and state[name]

    def buildChunks(self, thing):
        for text in thing.text:
            textType = type(text)
            if textType == str:
                if self.__stateChanged:
                    chunk = TextChunk()
                    chunk.state = {**self.__states}

                    if self.stateEnabled(chunk.state, "Small"):
                        chunk.yOffset = 10
                    elif self.stateEnabled(chunk.state, "Big"):
                        chunk.yOffset = -5

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
        if not self.__alive:
            return

        self.__caretTimer.update(dt)
        self.__shakingTimer.update(dt)

        for tween in self.__wavingChunksTweens:
            tween.update(dt)
            if not tween.alive:
                tween.reverse()

        # Keys
        if self.__state == DialogRenderer.STATE_PARSING:
            self.__tree = parse(self.__text, Text)
            self.__state = DialogRenderer.STATE_CHUNKING
        elif self.__state == DialogRenderer.STATE_CHUNKING:
            self.buildChunks(self.__tree)
            self.__state = DialogRenderer.STATE_WRAPPING
        elif self.__state == DialogRenderer.STATE_WRAPPING:
            self.wordWrap()
            self.__state = DialogRenderer.STATE_READY
        elif self.__state == DialogRenderer.STATE_READY:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.__currentLine += self.__linesMax
                        if self.__currentLine > len(self.__wrappedTextChunks):
                            self.__alive = False
                            self.__endCb(0)

    def draw(self):
        if not self.__alive:
            return

        # Draw frame
        self.__frame.draw()

        if self.__state != DialogRenderer.STATE_READY:
            return

        # Draw text
        yOffset = 0
        xOffset = 0
        lastYOffset = 0
        lastXOffset = 0

        for line in self.__wrappedTextChunks[self.__currentLine:self.__currentLine+self.__linesMax]:
            for chunk in line:
                self.__window.blit(chunk.surface, (self.__boundaries[0] + Frame.PADDING + xOffset + chunk.animationXOffset.value, self.__boundaries[1] + Frame.PADDING + yOffset + DialogRenderer.Y_OFFSET + chunk.yOffset + chunk.animationYOffset.value))
                xOffset += chunk.surface.get_width()
            lastYOffset = yOffset
            yOffset += DialogRenderer.LINE_HEIGHT
            lastXOffset = xOffset
            xOffset = 0

        # Draw the caret
        self.__window.blit(self.__caretTexture, (lastXOffset + 32, self.__boundaries[1] + Frame.PADDING + lastYOffset), (0, self.__caretStep, 32, 32))




