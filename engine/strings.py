import json

from data.savedatafields import SaveDataFields
from engine.savemanager import SaveManager


class StringsFormatter:
    def __init__(self, engine):
        self.__engine = engine

    def __format__(self, format_spec):
        if format_spec == "playerName":
            return SaveManager.getCurrentSaveValue(SaveDataFields.PLAYER_NAME)
        else:
            raise Exception("Unknown format placeholder " + format_spec)


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

    @staticmethod
    def getString(string):
        if string not in Strings.__strings:
            raise Exception("Unknown string " + string)

        return Strings.__strings[string].format(Strings.__formatter)


    @staticmethod
    def unload():
        Strings.__strings = {}
        Strings.__formatter = None
        Strings.__engine = None