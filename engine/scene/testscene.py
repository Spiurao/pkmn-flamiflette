from engine.scene.scene import Scene

class TestScene(Scene):
    def __init__(self, engine, count):
        super().__init__(engine)
        self.__count = str(count)

    def update(self, dt):
        print("Update test scene " + self.__count + " with dt=" + str(dt))

    def draw(self):
        print("Draw test scene " + self.__count)