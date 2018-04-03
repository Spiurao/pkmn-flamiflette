from data.textures import *
from engine.scene.testmapscene import TestMapScene
from engine.scene.testnotslowmapscene import TestNotSlowMapScene

VARIANT = Constants.GAME_VARIANT_FLAMIFLETTE

if __name__ == '__main__':
    Textures.load()

    engine = Engine(Constants.FRAMERATE, Constants.RESOLUTION, VARIANT)

    scene1 = TestNotSlowMapScene(engine, "test", (10, 10))
    #scene1 = TestNotSlowMapScene(engine, "test_tiny", (4, 4))
    #scene1 = TweenScene(engine)
    engine.pushScene(scene1, None)

    engine.run()

    Textures.unload()