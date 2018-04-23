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

class CharacterChunk:
    def __init__(self):
        self.char = ""
        self.surface = None
        self.state = {}
        self.yOffset = 0  # used to compensate the big and small text size
        self.animationXOffset = TweenSubject(0)  # used to animate letters
        self.animationYOffset = TweenSubject(0)

class DialogRenderer:

    # TODO Add choices here
    # TODO In order : letter by letter rendering, skip text, more rich text rendering
    # TODO Add sound

    STATE_PARSING = 0
    STATE_BUILDING = 1
    STATE_READY = 2

    LINE_HEIGHT = 40
    DEFAULT_TEXT_COLOR = (0, 0, 0, 0)
    FONT = "Dialog"

    Y_OFFSET = -4

    CARET_TIMER_DURATION = 100
    SHAKING_TIMER_DURATION = 20
    WAVING_TIMER_DURATION = 600
    LETTER_DURATION = 20  # TODO Make this a user choice

    WAVING_X_AMPLITUDE = 3
    WAVING_Y_AMPLITUDE = 8
    WAVING_OFFSET = 15  # ms offset between each letter

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

        self.__parserState = DialogRenderer.STATE_PARSING

        self.__states = {}

        self.__lines = [[]]
        self.__linesCharactersIndex = [0]

        self.__currentPageOffset = 0
        self.__currentlyDrawingLine = 0
        self.__alive = True

        self.__shakingChunks = []
        self.__wavingChunksTweens = []

        # Rich text parser variables
        self.__lastWhitespacePosOnTheLine = 0
        self.__currentPosOnTheLine = 0
        self.__xOffset = 0

    def buildLines(self, tree):
        for text in tree.text:
            textType = type(text)
            if textType == str:
                if text == " ":
                    self.__lastWhitespacePosOnTheLine = self.__currentPosOnTheLine

                self.setFontProperties(self.__states)

                chunk = CharacterChunk()
                chunk.char = text
                chunk.surface = self.__font.render(text, True, DialogRenderer.DEFAULT_TEXT_COLOR)  # TODO Right color
                chunk.state = {**self.__states}

                if self.stateEnabled(chunk.state, "Small"):
                    chunk.yOffset = 10
                elif self.stateEnabled(chunk.state, "Big"):
                    chunk.yOffset = -5

                if text == "\n":
                    self.__lines.append([])
                    self.__linesCharactersIndex.append(0)
                elif text == "\t":
                    for x in range(0, (self.__linesMax - len(self.__lines) % self.__linesMax) + 1):
                        self.__lines.append([])
                        self.__linesCharactersIndex.append(0)
                elif self.__xOffset + chunk.surface.get_width() >= self.__boundaries[2] - Frame.PADDING * 2:
                    # Rewind until the previous whitespace to put the previous
                    # word on the newly created line
                    newLine = self.__lines[-1][self.__lastWhitespacePosOnTheLine+1:self.__currentPosOnTheLine+1]

                    self.__lines[-1] = self.__lines[-1][:self.__lastWhitespacePosOnTheLine+1]

                    # Ignore empty new lines (overflowing whitespace)
                    if len(newLine) > 0:
                        # If the first char of the line is a whitespace
                        # remove its chunk
                        firstChar = newLine[0].char
                        if firstChar == " ":
                            newLine = newLine[1:]

                    # Append new line and reset
                    self.__xOffset = sum(x.surface.get_width() for x in newLine)
                    self.__lines.append(newLine)
                    self.__linesCharactersIndex.append(0)

                    self.__currentPosOnTheLine = len(newLine)

                if text != "\n" and text != "\t":
                    self.__lines[-1].append(chunk)
                    self.__xOffset += chunk.surface.get_width()

                    if self.stateEnabled(chunk.state, "Shaking"):
                        self.__shakingChunks.append(chunk)
                    elif self.stateEnabled(chunk.state, "Waving"):
                        chunk.animationXOffset.value = -DialogRenderer.WAVING_X_AMPLITUDE
                        chunk.animationYOffset.value = -DialogRenderer.WAVING_Y_AMPLITUDE

                        xtween = Tween(None, chunk.animationXOffset, DialogRenderer.WAVING_X_AMPLITUDE,
                                       DialogRenderer.WAVING_TIMER_DURATION, Easing.easingInOutSine, None)
                        xtween.runningSince = xtween.duration / 2  # fast forward half the time to offset X and Y animations

                        ytween = Tween(None, chunk.animationYOffset, DialogRenderer.WAVING_Y_AMPLITUDE,
                                       DialogRenderer.WAVING_TIMER_DURATION, Easing.easingInOutSine, None)

                        xtween.runningSince += DialogRenderer.WAVING_OFFSET * self.__currentPosOnTheLine
                        ytween.runningSince += DialogRenderer.WAVING_OFFSET * self.__currentPosOnTheLine

                        self.__wavingChunksTweens.append(xtween)
                        self.__wavingChunksTweens.append(ytween)

                self.__currentPosOnTheLine += 1
            else:
                typeStr = textType.__name__[:-4]
                self.__states[typeStr] = True
                self.buildLines(text.text)
                self.__states[typeStr] = False

    def shakingTimerCb(self, tag):
        for chunk in self.__shakingChunks:
            chunk.animationXOffset.value = random.randint(-1, 1)
            chunk.animationYOffset.value = random.randint(-1, 1)
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

    def stateEnabled(self, state, name):
        return name in state and state[name]

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
        if self.__parserState == DialogRenderer.STATE_PARSING:
            self.__tree = parse(self.__text, Text)
            self.__parserState = DialogRenderer.STATE_BUILDING
        elif self.__parserState == DialogRenderer.STATE_BUILDING:
            self.buildLines(self.__tree)
            self.__characterTimer = Timer(None, DialogRenderer.LETTER_DURATION, self.characterTimerCb)
            self.__parserState = DialogRenderer.STATE_READY
        elif self.__parserState == DialogRenderer.STATE_READY:
            self.__characterTimer.update(dt)
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if (event.key == pygame.K_RETURN) and ((self.__currentlyDrawingLine == self.__currentPageOffset + self.__linesMax) or (not self.__characterTimer.alive)):
                        self.__currentPageOffset += self.__linesMax
                        self.__currentlyDrawingLine = self.__currentPageOffset
                        if self.__currentPageOffset > len(self.__lines):
                            self.__alive = False
                            self.__endCb(0)

    def characterTimerCb(self, tag):
        if self.__currentlyDrawingLine == self.__currentPageOffset + self.__linesMax:
            # Wait for user to press action to continue drawing lines
            self.__characterTimer.restart()
            return

        if self.__linesCharactersIndex[self.__currentlyDrawingLine] + 1 > len(self.__lines[self.__currentlyDrawingLine]):
            self.__currentlyDrawingLine += 1

        try:
            self.__linesCharactersIndex[self.__currentlyDrawingLine] += 1
        except IndexError:
            # Reached the end of the text
            return

        self.__characterTimer.restart()

    def draw(self):
        if not self.__alive:
            return

        # Draw frame
        self.__frame.draw()

        if self.__parserState != DialogRenderer.STATE_READY:
            return

        # Draw text
        xOffset = 0
        yOffset = 0
        lastXOffset = 0
        lastYOffset = 0
        lineIndex = self.__currentPageOffset

        for line in self.__lines[self.__currentPageOffset:self.__currentPageOffset + self.__linesMax]:
            if len(line) == 0:
                continue

            for chunk in line[:self.__linesCharactersIndex[lineIndex]]:
                cx = self.__boundaries[0] + Frame.PADDING + xOffset + chunk.animationXOffset.value
                cy = self.__boundaries[1] + Frame.PADDING + yOffset + DialogRenderer.Y_OFFSET + chunk.yOffset + chunk.animationYOffset.value

                self.__window.blit(chunk.surface, (cx, cy))

                if self.stateEnabled(chunk.state, "Strike"):
                    pygame.draw.rect(self.__window, DialogRenderer.DEFAULT_TEXT_COLOR, (cx - 4, cy + 2 + chunk.surface.get_height() / 2, chunk.surface.get_width() + 4, 2))  # TODO Put right text color here

                xOffset += chunk.surface.get_width()
                lastXOffset = xOffset if chunk.char != " " else lastXOffset

            lastYOffset = yOffset

            yOffset += DialogRenderer.LINE_HEIGHT
            xOffset = 0
            lineIndex += 1


        # Draw the caret
        if (self.__currentlyDrawingLine == self.__currentPageOffset + self.__linesMax) or (not self.__characterTimer.alive):
            self.__window.blit(self.__caretTexture, (lastXOffset + 32, self.__boundaries[1] + Frame.PADDING + lastYOffset), (0, self.__caretStep, 32, 32))





