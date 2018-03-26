from engine.scene.scene import Scene
from random import randint as rng
import pygame

class TestScene(Scene):
    def __init__(self, engine, count):
        super().__init__(engine)
        self.__count = count
        self.__color = (rng(0, 255), rng(0, 255), rng(0, 255))

    def update(self, dt, events):
        print("Update test scene " + str(self.__count) + " with dt=" + str(dt))
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.getEngine().pushScene(TestScene(self.getEngine(), self.__count+1), None)

    def draw(self):
        print("Draw test scene " + str(self.__count))
        pygame.draw.rect(self.getEngine().getWindow(), self.__color, (10 + self.__count * 100, 10 + self.__count * 100, 100, 100))
