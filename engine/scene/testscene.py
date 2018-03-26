from engine.scene.scene import Scene
import pygame

class TestScene(Scene):
    def __init__(self, engine, count):
        super().__init__(engine)
        self.__count = count

    def update(self, dt):
        print("Update test scene " + str(self.__count) + " with dt=" + str(dt))

    def draw(self):
        print("Draw test scene " + str(self.__count))
        pygame.draw.rect(self.getEngine().getWindow(), (120, 120, 120), (10 + self.__count * 100, 10 + self.__count * 100, 100, 100))
