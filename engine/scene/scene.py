class Scene:

    def __init__(self, engine):
        self.__engine = engine

    def load(self):
        pass

    def unload(self):
        pass

    def draw(self):
        pass

    def update(self):
        pass

    def transitionOut(self):
        return False

	def onPause(self):
		pass

	def onResume(self):
		pass
