import msgpack
import os
import sys

class SaveManager:

    __currentSlot = None
    __saveData = None

    __saveFile = None

    """
    Returns the current save's value for the given key or None if no save is loaded / the key is empty
    """
    @staticmethod
    def getCurrentSaveValue(key):
        if SaveManager.__saveData is None or key not in SaveManager.__saveData:
            return None

        return SaveManager.__saveData[key]

    """
    Sets the current save's value for the given key
    """
    @staticmethod
    def setCurrentSaveValue(key, value):
        if SaveManager.__saveData is None:
            return False

        try:
            SaveManager.__saveData[key] = value
            return True
        except Exception as e:
            print(e)
            return False

    """
    Returns the current save slot number or None if no save is loaded
    """
    @staticmethod
    def getCurrentSaveSlot():
        return SaveManager.__currentSlot

    """
    Saves the current save's data into the corresponding slot file
    Does nothing if no save is loaded
    Returns True if save succeeded, False otherwise
    """
    @staticmethod
    def save():
        if SaveManager.__saveFile is None:
            return False

        try:
            data = msgpack.packb(SaveManager.__saveData, use_bin_type=True)
            SaveManager.__saveFile.write(data)
            return True
        except Exception as e:
            print(e)
            return False


    """
    Returns the file path for save file at given slot
    """
    @staticmethod
    def getSavePathForSlot(slot):
        try:
            slot = str(slot)
            return os.path.join(SaveManager.getSaveDirectory(), "slot" + slot + ".sav")
        except Exception as e:
            print(e)
            return None

    """
    Returns the directory to use to store save files
    """
    @staticmethod
    def getSaveDirectory():
        return "save"

    """
    Unloads the current save, creates and loads a new save in the given slot, overriding any data present here
    Returns True if creating the save succeeded, False otherwise
    """
    @staticmethod
    def createNewSave(slot):
        SaveManager.unloadCurrentSave()

        try:
            slot = str(slot)

            SaveManager.deleteSave(slot)

            os.makedirs(SaveManager.getSaveDirectory(), exist_ok=True)

            path = SaveManager.getSavePathForSlot(slot)

            os.mknod(path)

            SaveManager.__saveFile = open(path, "r+b")
            SaveManager.__saveData = {}
            SaveManager.__currentSlot = slot

            SaveManager.save()

            return True
        except Exception as e:
            print(e)
            SaveManager.unloadCurrentSave()
            return False
    """
    Unload and deletes save data for the given slot
    Returns True if the deletion succeeded, False otherwise
    """
    @staticmethod
    def deleteSave(slot):
        SaveManager.unloadCurrentSave()

        try:
            slot = str(slot)

            saveToDeletePath = SaveManager.getSavePathForSlot(slot)

            if os.path.exists(saveToDeletePath):
                os.remove(saveToDeletePath)

            return True
        except Exception as e:
            print(e)
            return False

    """
    Returns True if a save is present in the given slot, False otherwise
    """
    @staticmethod
    def saveExists(slot):
        try:
            slot = str(slot)
            return os.path.exists(SaveManager.getSavePathForSlot(slot))
        except Exception as e:
            print(e)
            return False

    """
    Unloads the current save and loads the save of the given slot
    Returns True if the save was loaded, False otherwise
    """
    @staticmethod
    def loadSlot(slot):
        SaveManager.unloadCurrentSave()

        try:
            slot = str(slot)

            filePath = SaveManager.getSavePathForSlot(slot)

            if not os.path.exists(filePath):
                return False

            SaveManager.__saveFile = open(filePath, "r+b")
            SaveManager.__currentSlot = slot
            SaveManager.__saveData = msgpack.unpackb(SaveManager.__saveFile.read(), raw=False)
            return True
        except Exception as e:
            print("Cannot load save slot " + slot + " : ", e)
            SaveManager.unloadCurrentSave()
            return False

    """
    Unloads the current save data
    """
    @staticmethod
    def unloadCurrentSave():
        SaveManager.__currentSlot = None
        SaveManager.__saveData = None

        if SaveManager.__saveData is not None:
            SaveManager.__saveData.close()