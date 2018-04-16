from engine.scene.scene import Scene

class BattleScene(Scene):
	def __init__(self, engine, background, player):
		super().__init__(engine)

		self.__background = background
		self.__player = player