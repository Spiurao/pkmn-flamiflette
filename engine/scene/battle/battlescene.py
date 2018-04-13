from engine.scene.scene import Scene

class BattleScene(Scene):
	def __init__(self, engine, background):
		self.engine = engine
		self.background = background