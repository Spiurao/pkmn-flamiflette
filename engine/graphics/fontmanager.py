import os
from enum import Enum

import pygame


class FontStyle(Enum):
    REGULAR = 0b1
    BOLD = 0b10
    ITALIC = 0b100
    UNDERLINE = 0b1000

class FontManager:

    FONT_FILES = {
        "Emerald" : "Pokémon Emerald Pro.ttf"
    }

    # File name, size, style
    FONT_FACES = {
        "Emerald26Regular" : ("Emerald", 26, FontStyle.REGULAR),
        "Emerald32Bold" : ("Emerald", 32, FontStyle.BOLD)
    }

    __fonts = {}

    @staticmethod
    def load():
        from data.constants import Constants
        for fontFace in FontManager.FONT_FACES:
            fontName = FontManager.FONT_FILES[FontManager.FONT_FACES[fontFace][0]]
            font = pygame.font.Font(os.path.join(Constants.FONTS_PATH, fontName), FontManager.FONT_FACES[fontFace][1])

            fontFlags = FontManager.FONT_FACES[fontFace][2]

            if (0xff and fontFlags) != FontStyle.REGULAR:
                if (0xff and fontFlags) == FontStyle.BOLD:
                    font.set_bold(True)
                if (0xff and fontFlags) == FontStyle.ITALIC:
                    font.set_italic(True)
                if (0xff and fontFlags) == FontStyle.UNDERLINE:
                    font.set_underline(True)

            FontManager.__fonts[fontFace] = font

    @staticmethod
    def unload():
        FontManager.__fonts = {}

    @staticmethod
    def getFont(name : str) -> pygame.font.Font:
        return FontManager.__fonts[name]