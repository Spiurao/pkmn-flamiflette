import json

from data.constants import *
import glob
import pygame


class Textures:

    __textures = {}

    @staticmethod
    def load():
        # Load all textures
        size = len(Constants.IMG_PATH)+1
        for f in glob.iglob(os.path.join(Constants.IMG_PATH, '**','*.png'), recursive=True):
            textureName = f[size:len(f)-4]
            textureName = textureName.replace(os.path.sep, ".")
            Textures.__textures[textureName] = pygame.image.load(f).convert()

        # Apply color keys when necessary
        with open(Constants.COLOR_KEYS_PATH, "r") as f:
            colorKeys = json.loads(f.read())
            for c in colorKeys:
                if c in Textures.__textures:
                    Textures.__textures[c].set_colorkey(colorKeys[c])
                else:
                    raise Exception("Error while applying color key to texture " + c + " : texture does not exist")


    @staticmethod
    def unload():
        Textures.__textures = {}

    @staticmethod
    def getTextures():
        return Textures.__textures