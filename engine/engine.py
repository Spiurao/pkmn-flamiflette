import pygame

class Engine:

    TRANSITION_ACTION_PUSH = 0
    TRANSITION_ACTION_POP = 1

    GAME_VARIANT_1 = 0
    GAME_VARIANT_2 = 1

    def __init__(self, framerate, resolution, variant):
        # data init
        self.__sceneStack = []
        self.__pendingScene = None
        self.__transitionScene = None
        self.__transitionAction = None
        self.__clock = pygame.time.Clock()
        self.__running = True
        self.__framerate = framerate
        self.__resolution = resolution
        self.__variant = variant

    def getVariant(self):
        return self.__variant

    def getResolution(self):
        return self.__resolution

    def getWindow(self):
        return self.__window

    def run(self):
        # pygame display
        pygame.display.init()
        from data.constants import Constants
        pygame.display.set_caption(Constants.WINDOW_TITLE[self.__variant])
        self.__window = pygame.display.set_mode(self.__resolution)

        # main loop
        while self.__running:
            # tick tock
            dt = self.__clock.tick(self.__framerate)

            # pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit()

            # scenes update and draw
            self.__window.fill((0, 0, 0))

            self.update(dt)
            self.draw()

            pygame.display.flip()

        # exit
        pygame.display.quit()

    def exit(self):
        self.__running = False

    def update(self, dt):
        if self.__transitionScene is None and len(self.__sceneStack) > 0:
            self.__sceneStack[-1].update(dt)
        elif self.__transitionScene is not None:
            self.__transitionScene.update(dt)

    def draw(self):
        if len(self.__sceneStack) > 0:
            toDraw = []
            for scene in self.__sceneStack[::-1]:
                toDraw.append(scene)
                if not scene.shouldDrawUnderlyingScenes():
                    break

            for scene in toDraw:
                scene.draw()

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
            if len(self.__sceneStack) > 0:
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
            if len(self.__sceneStack) > 0:
                self.__sceneStack[-1].unload()
                self.__sceneStack.pop()

                # if the stack contains at least one scene
                # after popping, we resume it
                if len(self.__sceneStack) > 0:
                    self.__sceneStack[-1].onResume()