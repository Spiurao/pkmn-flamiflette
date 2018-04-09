import glob
import os
import pygame


class SFX:

    __sfx = {}

    @staticmethod
    def load():
        # Load all SFXs
        from data.constants import Constants
        size = len(Constants.SFX_PATH) + 1
        for f in glob.iglob(os.path.join(Constants.SFX_PATH, '**', '*.ogg'), recursive=True):
            sfxName = f[size:len(f) - 4]
            sound =  pygame.mixer.Sound(f)
            sound.set_volume(Constants.MASTER_VOLUME * Constants.SFX_VOLUME)
            SFX.__sfx[sfxName] = sound

    @staticmethod
    def unload():
        SFX.__sfx = None

    @staticmethod
    def play(sfx : str):
        if sfx not in SFX.__sfx:
            raise Exception("Unknown SFX " + sfx)

        SFX.__sfx[sfx].play()