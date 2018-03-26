class Engine:

    TRANSITION_ACTION_PUSH = 0
    TRANSITION_ACTION_POP = 1

    def __init__(self):
        # data init
        self.__sceneStack = []
        self.__pendingScene = None
        self.__transitionScene = None
        self.__transitionAction = None

        # main loop
            # TODO

    def update(self):
        if self.__transitionScene is None and self.__sceneStack.count() > 0:
            self.__sceneStack[-1].update()
        else:
            self.__transitionScene.update()

    def draw(self):
        if self.__sceneStack.count() > 0:
            for i in self.__sceneStack:
                self.__sceneStack[i].draw()

        if self.__transitionScene is not None:
            self.__transitionScene.draw()

    def onTransitionFinish(self):
        if self.__transitionAction == Engine.TRANSITION_ACTION_PUSH:
            # push pending scene and clear transition
            self.__transitionScene = None
            self.pushScene(self.__pendingScene, None)
            self.__pendingScene = None
        elif self.__transitionAction == Engine.TRANSITION_ACTION_POP:
            #pop current scene and clear transition
            self.__transitionScene = None
            self.popScene(None)

    def pushScene(self, scene, transition):
        # transition
        if transition is not None:
            self.__transitionAction = Engine.TRANSITION_ACTION_PUSH
            self.__transitionScene = transition
            self.__pendingScene = scene
            # we now wait for onTransitionFinish()
        else:
            # pause the current active scene
            if self.__sceneStack.count() > 0:
                self.__sceneStack[-1].onPause()

            # load and push the new one
            scene.load()
            self.__sceneStack.append(scene)

    def popScene(self, transition):
        if transition is not None:
            self.__transitionAction = Engine.TRANSITION_ACTION_POP
            self.__transitionScene = transition
            # we now wait for onTransitionFinish()
        else:
            # unload and pop the current scene
            if self.__sceneStack.count() > 0:
                self.__sceneStack[-1].unload()
                self.__sceneStack.pop()

                # if the stack contains at least one scene
                # after popping, we resume it
                if self.__sceneStack.count() > 0:
                    self.__sceneStack[-1].onResume()