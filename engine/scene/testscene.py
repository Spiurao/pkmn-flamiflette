from engine.scene.scene import Scene
from random import choice
import pygame
from data.textures import *
class TestScene(Scene):
    def __init__(self, engine, count):
        super().__init__(engine)
        self.__count = count
        #self.__color = (rng(0, 255), rng(0, 255), rng(0, 255))
        self.__tex = Textures.getTextures()[choice(list(Textures.getTextures().keys()))]

    def update(self, dt, events):
        print("Update test scene " + str(self.__count) + " with dt=" + str(dt))
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.getEngine().pushScene(TestScene(self.getEngine(), self.__count+1), None)

    def draw(self):
        print("Draw test scene " + str(self.__count))
        #pygame.draw.rect(self.getEngine().getWindow(), self.__color, (10 + self.__count * 100, 10 + self.__count * 100, 100, 100))
        self.getEngine().getWindow().blit(self.__tex, (10 + self.__count * 16, 10 + self.__count * 16))
