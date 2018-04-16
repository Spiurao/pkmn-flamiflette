from scene.battle.battlescene import BattleScene

class WildBattleScene(BattleScene):
	"""docstring for WildBattleScene"""
	def __init__(self, engine, background, player, pokemon):
		super(engine, background, player).__init__()
		
		self.__pokemon = pokemon
