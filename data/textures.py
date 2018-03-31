import os
from data.constants import *
import glob
import pygame

class Textures:

    COLOR_KEYS = {
        "tilesets.overworld" : (255, 255, 255)
    }

    __textures = {}

    @staticmethod
    def load():
        # Load all textures
        size = len(Constants.IMG_PATH)+1
        for f in glob.iglob(os.path.join(Constants.IMG_PATH, '**','*.png'), recursive=True):
            textureName = f[size:len(f)-4]
            textureName = textureName.replace(os.path.sep, ".")
            Textures.__textures[textureName] = pygame.image.load(f)

        # Apply color keys when necessary
        for c in Textures.COLOR_KEYS:
            if c in Textures.__textures:
                Textures.__textures[c].set_colorkey(Textures.COLOR_KEYS[c])
            else:
                print("Error while applying color key to texture " + c + " : texture does not exist")


    @staticmethod
    def unload():
        Textures.__textures = {}

    @staticmethod
    def getTextures():
        return Textures.__textures