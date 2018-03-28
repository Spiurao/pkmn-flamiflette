from data.savedatafields import SaveDataFields
from engine.engine import *
from engine.scene.testmapscene import TestMapScene
from engine.scene.testscene import *
from data.constants import *
from data.textures import *
from engine.savemanager import *
from engine.scene.tweenscene import TweenScene
from engine.tween.Easing import Easing

VARIANT = Constants.GAME_VARIANT_FLAMIFLETTE

if __name__ == '__main__':
    Textures.load()

    engine = Engine(Constants.FRAMERATE, Constants.RESOLUTION, VARIANT)

    #scene1 = TestMapScene(engine, "test")
    scene1 = TweenScene(engine)
    engine.pushScene(scene1, None)

    engine.run()

    Textures.unload()