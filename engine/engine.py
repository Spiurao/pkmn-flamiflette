class Engine:

    def __init__(self):
        self.__sceneStack = None
        self.__pendingScene = None
        self.__transitionScene = None

    def update(self):
        if self.__transitionScene is None:
            self.__scene.update()
        else:
            self.__transitionScene.update()

    def draw(self):
        self.__scene.draw()

        if self.__transitionScene is not None:
            self.__transitionScene.draw()

    def onTransitionFinish(self):
        self.changeScene(self.__pendingScene)
        self.__pendingScene = None
        self.__transitionScene = None

    def transitionToScene(self, scene, transition):
        self.__pendingScene = scene
        self.__transitionScene = transition

    def changeScene(self, scene):
        if self.__scene is not None:
            self.__scene.unload()

        self.__scene = scene
        self.__scene.load()
