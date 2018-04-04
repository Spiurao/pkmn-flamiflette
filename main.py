from data.textures import *
from engine.scene.map.mapscene import MapScene

VARIANT = Constants.GAME_VARIANT_FLAMIFLETTE

if __name__ == '__main__':
    Textures.load()

    engine = Engine(Constants.FRAMERATE, Constants.RESOLUTION, VARIANT)

    scene1 = MapScene(engine, "test", (10, 10))
    #scene1 = MapScene(engine, "test_tiny", (4, 4))
    engine.pushScene(scene1, None)

    engine.run()

    Textures.unload()