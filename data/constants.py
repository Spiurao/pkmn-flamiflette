from engine.engine import Engine
import os

class Constants:

    GAME_VARIANT_FLAMIFLETTE = Engine.GAME_VARIANT_1
    GAME_VARIANT_TARTIKUECHEKEUCHE = Engine.GAME_VARIANT_2

    IMG_PATH = os.path.join("data", "img")
    MAPS_PATH = os.path.join("data", "maps")
    METADATA_PATH = os.path.join("data", "metadata")
    MAPS_METADATA_PATH = os.path.join(METADATA_PATH, "maps")
    TILESETS_PATH = os.path.join("data", "tilesets")
    ACTORS_PATH = os.path.join("data", "actors")
    BGM_PATH = os.path.join("data", "bgm")
    SFX_PATH = os.path.join("data", "sfx")

    COLOR_KEYS_PATH = os.path.join("data", "colorkeys.json")
    STRINGS_PATH = os.path.join("data", "strings.json")

    WINDOW_TITLE = {
        GAME_VARIANT_FLAMIFLETTE : "Pokémon Version Flamiflette",
        GAME_VARIANT_TARTIKUECHEKEUCHE : "Pokémon Version Tartikuechekeuche"
    }

    FRAMERATE = 60
    RESOLUTION = (800, 608)

    FONT_NAME = "System"

    MASTER_VOLUME = 1.0
    BGM_VOLUME = 0.1
    SFX_VOLUME = 0.2

    # TODO Add root scene class here (no parameters required) - first scene to be ran by the game when launching
