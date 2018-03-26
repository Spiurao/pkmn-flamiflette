from engine.scene.scene import Scene
from random import choice
import pygame
from data.textures import *
class TestScene(Scene):
    def __init__(self, engine, count):
        super().__init__(engine)
        self.__count = count
        self.__tex = Textures.getTextures()[choice(list(Textures.getTextures().keys()))]

    def update(self, dt, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.getEngine().pushScene(TestScene(self.getEngine(), self.__count+1), None)

    def draw(self):
        self.getEngine().getWindow().blit(self.__tex, (self.__count * 16, self.__count * 16))
