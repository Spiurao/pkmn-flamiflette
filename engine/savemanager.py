import msgpack
import os

class SaveManager:

    __currentSlot = None
    __currentVariant = None
    __saveData = None

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

    @staticmethod
    def getCurrentVariant():
        return SaveManager.__currentVariant

    """
    Saves the current save's data into the corresponding slot file
    Does nothing if no save is loaded
    Returns True if save succeeded, False otherwise
    """
    @staticmethod
    def save():
        try:
            data = msgpack.packb(SaveManager.__saveData, use_bin_type=True)
            with open(SaveManager.getSavePathForSlot(SaveManager.__currentSlot, SaveManager.__currentVariant), "r+b") as file:
                file.write(data)
                file.flush()

            return True
        except Exception as e:
            print(e)
            return False


    """
    Returns the file path for save file at given slot
    slotX-Y.bin where X is the variant, Y the slot
    """
    @staticmethod
    def getSavePathForSlot(slot, variant):
        try:
            slot = str(slot)
            variant = str(variant)
            return os.path.join(SaveManager.getSaveDirectory(), "slot" + variant + "-" + slot + ".sav")
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
    def createNewSave(slot, variant):
        SaveManager.unloadCurrentSave()

        try:
            slot = str(slot)
            variant = str(variant)

            SaveManager.deleteSave(slot, variant)

            os.makedirs(SaveManager.getSaveDirectory(), exist_ok=True)

            path = SaveManager.getSavePathForSlot(slot, variant)

            with open(path, "w+"): pass  # file creation

            SaveManager.__saveData = {}
            SaveManager.__currentSlot = slot
            SaveManager.__currentVariant = variant

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
    def deleteSave(slot, variant):
        SaveManager.unloadCurrentSave()

        try:
            slot = str(slot)
            variant = str(variant)

            saveToDeletePath = SaveManager.getSavePathForSlot(slot, variant)

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
    def saveExists(slot, variant):
        try:
            slot = str(slot)
            variant = str(variant)
            return os.path.exists(SaveManager.getSavePathForSlot(slot, variant))
        except Exception as e:
            print(e)
            return False

    """
    Unloads the current save and loads the save of the given slot
    Returns True if the save was loaded, False otherwise
    """
    @staticmethod
    def load(slot, variant):
        SaveManager.unloadCurrentSave()

        try:
            slot = str(slot)
            variant = str(variant)

            filePath = SaveManager.getSavePathForSlot(slot, variant)

            if not os.path.exists(filePath):
                return False

            with open(filePath, "r+b") as file:
                data = file.read()

            SaveManager.__currentSlot = slot
            SaveManager.__currentVariant = variant
            SaveManager.__saveData = msgpack.unpackb(data, raw=False)

            return True
        except Exception as e:
            print("Cannot load save slot " + slot + " for variant " + variant + " : ", e)
            SaveManager.unloadCurrentSave()
            return False

    """
    Unloads the current save data
    """
    @staticmethod
    def unloadCurrentSave():
        SaveManager.__currentSlot = None
        SaveManager.__saveData = None
        SaveManager.__currentVariant = None