from engine.engine import Engine
import os

class Constants:

    GAME_VARIANT_FLAMIFLETTE = Engine.GAME_VARIANT_1
    GAME_VARIANT_TARTIKEUCHE = Engine.GAME_VARIANT_2

    IMG_PATH = os.path.join("data", "img")
    MAPS_PATH = os.path.join("data", "maps")

    WINDOW_TITLE = {
        GAME_VARIANT_FLAMIFLETTE : "Pokémon Version Flamiflette",
        GAME_VARIANT_TARTIKEUCHE : "Pokémon Version Tartikeuche"
    }

    FRAMERATE = 60
    RESOLUTION = (800, 608)