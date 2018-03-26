import os
from data.constants import *
import glob
import pygame

class Textures:

    __textures = {}

    @staticmethod
    def load():
        size = len(Constants.IMG_PATH)+1
        for f in glob.iglob(os.path.join(Constants.IMG_PATH, '**','*.png'), recursive=True):
            Textures.__textures[f[size:len(f)-4]] = pygame.image.load(f)

    @staticmethod
    def unload():
        Textures.__textures = {}

    @staticmethod
    def getTextures():
        return Textures.__textures