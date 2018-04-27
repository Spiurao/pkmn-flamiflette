import pygame

from engine.engine import Engine
import os

class Constants:

    GAME_VARIANT_FLAMIFLETTE = Engine.GAME_VARIANT_1
    GAME_VARIANT_TARTIKUECHE = Engine.GAME_VARIANT_2

    IMG_PATH = os.path.join("data", "img")
    MAPS_PATH = os.path.join("data", "maps")
    METADATA_PATH = os.path.join("data", "metadata")
    MAPS_METADATA_PATH = os.path.join(METADATA_PATH, "maps")
    TILESETS_PATH = os.path.join("data", "tilesets")
    ACTORS_PATH = os.path.join("data", "actors")
    BGM_PATH = os.path.join("data", "bgm")
    SFX_PATH = os.path.join("data", "sfx")
    FONTS_PATH = os.path.join("data", "fonts")

    COLOR_KEYS_PATH = os.path.join("data", "colorkeys.json")
    STRINGS_PATH = os.path.join("data", "strings")

    WINDOW_TITLE = {
        GAME_VARIANT_FLAMIFLETTE : "Pokémon Version Flamiflette",
        GAME_VARIANT_TARTIKUECHE : "Pokémon Version Tartikueche"
    }

    DEFAULT_CONFIGURATION = "windowed"

    # Framerate, resolution, renderer flags
    CONFIGURATIONS = {
        "windowed": (60, (800, 608), 0),
        "switch": (60, (1280, 704), 0) #can't be (pygame.FULLSCREEN or pygame.DOUBLEBUF or pygame.HWSURFACE) because of a display bug
    }

    MASTER_VOLUME = 1.0
    BGM_VOLUME = 0.1
    SFX_VOLUME = 0.2

    # TODO Add root scene class here (no parameters required) - first scene to be ran by the game when launching
