import pygame


class Engine:

    TRANSITION_ACTION_PUSH = 0
    TRANSITION_ACTION_POP = 1

    GAME_VARIANT_1 = 0
    GAME_VARIANT_2 = 1

    def __init__(self, framerate, resolution, variant):
        # data init
        self.__sceneStack = []  # scene stack
        self.__sceneDrawOrder = []  # pre-computed list of scenes to draw in the right order
        self.__pendingScene = None  # the scene to push after a transition
        self.__transitionScene = None  # the current transition
        self.__transitionAction = None  # what should we do after the transition ? TRANSITION_ACTION_PUSH or TRANSITION_ACTION_POP
        self.__clock = pygame.time.Clock()  # the main loop clock
        self.__running = True  # is the game running ?
        self.__framerate = framerate  # the framerate in FPS
        self.__resolution = resolution  # the game window resolution
        self.__variant = variant  # the game variant : GAME_VARIANT_1 or GAME_VARIANT_2

        # pygame display
        pygame.display.init()
        from data.constants import Constants
        pygame.display.set_caption(Constants.WINDOW_TITLE[self.__variant])
        self.__window = pygame.display.set_mode(self.__resolution)

        # textures loading
        from engine.graphics.textures import Textures
        Textures.load()

    def invalidateDrawOrder(self):
        if len(self.__sceneStack) > 0:
            toDraw = []
            for scene in self.__sceneStack[::-1]:
                toDraw.append(scene)
                if not scene.shouldDrawUnderlyingScenes():
                    break

            self.__sceneDrawOrder = toDraw[::-1]
        else:
            self.__sceneDrawOrder = []

    def getVariant(self):
        return self.__variant

    def getResolution(self):
        return self.__resolution

    def getWindow(self):
        return self.__window

    def run(self):
        print("Running game...")

        # main loop
        while self.__running:

            try:
                # tick tock
                dt = self.__clock.tick(self.__framerate)

                # pygame events
                events = pygame.event.get()
                for event in events:
                    if event.type == pygame.QUIT:
                        self.exit()

                # fill
                self.__window.fill((0, 0, 0, 0))

                # scenes update and draw
                self.update(dt, events)
                self.draw()

                pygame.display.update()
            except KeyboardInterrupt:
                self.exit()

        # exit
        print("Quitting game...")
        pygame.display.quit()

        from engine.graphics.textures import Textures
        Textures.unload()

    def exit(self):
        self.__running = False

    def update(self, dt, events):
        if self.__transitionScene is None and len(self.__sceneStack) > 0:
            self.__sceneStack[-1].update(dt, events)
        elif self.__transitionScene is not None:
            self.__transitionScene.update(dt, events)

    def draw(self):
        for scene in self.__sceneDrawOrder:
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

            # invalidate draw order
            self.invalidateDrawOrder()

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

                # invalidate draw order
                self.invalidateDrawOrder()