import os
from data.constants import *
import glob
import pygame

class Textures:

    COLOR_KEYS = {
        "maps/test" : (255, 255, 255)
    }

    __textures = {}

    @staticmethod
    def load():
        # Load all textures
        size = len(Constants.IMG_PATH)+1
        for f in glob.iglob(os.path.join(Constants.IMG_PATH, '**','*.png'), recursive=True):
            Textures.__textures[f[size:len(f)-4]] = pygame.image.load(f)

        # Apply color keys when necessary
        for c in Textures.COLOR_KEYS:
            Textures.__textures[c].set_colorkey(Textures.COLOR_KEYS[c])


    @staticmethod
    def unload():
        Textures.__textures = {}

    @staticmethod
    def getTextures():
        return Textures.__textures