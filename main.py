from engine.engine import *
from engine.scene.testscene import *
from data.constants import *
from data.textures import *

FRAMERATE = 30
RESOLUTION = (800, 608)
VARIANT = Constants.GAME_VARIANT_FLAMIFLETTE

if __name__ == '__main__':
    Textures.load()
    print(Textures.getTextures())

    engine = Engine(FRAMERATE, RESOLUTION, VARIANT)

    scene1 = TestScene(engine, 1)
    engine.pushScene(scene1, None)

    engine.run()

    Textures.unload()