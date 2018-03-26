from engine.engine import *
from engine.scene.testscene import *

FRAMERATE = 30

if __name__ == '__main__':
    engine = Engine(FRAMERATE)

    scene1 = TestScene(engine, 1)
    engine.pushScene(scene1, None)

    scene2 = TestScene(engine, 2)
    engine.pushScene(scene2, None)

    engine.run()