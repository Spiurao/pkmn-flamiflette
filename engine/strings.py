import json
import random

from data.savedatafields import SaveDataFields
from engine.savemanager import SaveManager


class StringsFormatter:
    def __init__(self, engine):
        self.__engine = engine

    def __format__(self, format_spec):
        value = None
        if format_spec == "playerName":
            value = SaveManager.getCurrentSaveValue(SaveDataFields.PLAYER_NAME)
        else:
            raise Exception("Unknown format placeholder " + format_spec)

        if value is None:
            value = "n/a"

        return value


class Strings:
    __strings = {}
    __formatter = None
    __engine = None

    @staticmethod
    def load(engine):
        Strings.__engine = engine

        # Load the strings
        from data.constants import Constants
        with open(Constants.STRINGS_PATH) as f:
            Strings.__strings = json.loads(f.read())

        # Prepare the formatter
        Strings.__formatter = StringsFormatter(engine)

    dict = {
        "playerName": str(random.randint(1, 484))
    }

    @staticmethod
    def getString(string, *args):
        if string not in Strings.__strings:
            raise Exception("Unknown string " + string)

        result = Strings.__strings[string].format(*args)

        return result


    @staticmethod
    def unload():
        Strings.__strings = {}
        Strings.__formatter = None
        Strings.__engine = None