import os
from typing import Tuple, List

import pygame

from engine.graphics.fontmanager import FontManager
from engine.scene.scene import Scene
from engine.sound.sfx import SFX
from engine.strings import Strings


class Engine:

    TRANSITION_ACTION_PUSH = 0
    TRANSITION_ACTION_POP = 1

    GAME_VARIANT_1 = 0
    GAME_VARIANT_2 = 1

    SHOW_FPS_COUNTER = True

    def __init__(self, configuration : Tuple, variant : int):
        # data init
        from data.constants import Constants
        if configuration not in Constants.CONFIGURATIONS:
            raise Exception("Unknown configuration " + configuration)

        configuration = Constants.CONFIGURATIONS[configuration]

        self.__sceneStack = []  # scene stack
        self.__sceneDrawOrder = []  # pre-computed list of scenes to draw in the right order
        self.__pendingScene = None  # the scene to push after a transition
        self.__transitionScene = None  # the current transition
        self.__transitionAction = None  # what should we do after the transition ? TRANSITION_ACTION_PUSH or TRANSITION_ACTION_POP
        self.__clock = pygame.time.Clock()  # the main loop clock
        self.__running = True  # is the game running ?
        self.__framerate = configuration[0]  # the framerate in FPS
        self.__resolution = configuration[1]  # the game window resolution
        self.__variant = variant  # the game variant : GAME_VARIANT_1 or GAME_VARIANT_2

        # pygame display
        pygame.mixer.pre_init(44100, -16, 1, 512)
        pygame.init()
        pygame.display.init()
        pygame.display.set_caption(Constants.WINDOW_TITLE[self.__variant])
        self.__window = pygame.display.set_mode(self.__resolution, configuration[2])

        # textures loading
        from engine.graphics.textures import Textures
        Textures.load()

        # sfx loading
        SFX.load()

        # strings loading
        Strings.load(self)

        # fonts
        FontManager.load()

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

    def getVariant(self) -> int:
        return self.__variant

    def getResolution(self) -> Tuple:
        return self.__resolution

    def getWindow(self) -> pygame.Surface:
        return self.__window

    def getClockDate(self) -> int:
        return pygame.time.get_ticks()

    def playBGM(self, musicName):
        try:
            # TODO If already playing the same BGM, do nothing, else make a fade out and play
            from data.constants import Constants
            bgmPath = os.path.join(Constants.BGM_PATH, musicName + ".mp3")
            pygame.mixer.music.load(bgmPath)
            pygame.mixer.music.set_volume(Constants.BGM_VOLUME * Constants.MASTER_VOLUME)
            pygame.mixer.music.play()
        except pygame.error as e:
            print("Unable to play BGM (" + str(e) + ")")

    def run(self):
        print("Running game...")

        # main loop
        while self.__running:

            try:
                # tick tock
                dt = self.__clock.tick_busy_loop(self.__framerate)

                # pygame events
                events = pygame.event.get()
                for event in events:
                    if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
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

        for scene in self.__sceneStack[::-1]:
            scene.unload()

        pygame.display.quit()

        from engine.graphics.textures import Textures
        Textures.unload()

        SFX.unload()
        Strings.unload()
        FontManager.unload()

    def exit(self):
        self.__running = False

    def update(self, dt : int, events : List[pygame.event.Event]):
        if self.__transitionScene is None and len(self.__sceneStack) > 0:
            self.__sceneStack[-1].update(dt, events)
        elif self.__transitionScene is not None:
            self.__transitionScene.update(dt, events)

    def draw(self):
        for scene in self.__sceneDrawOrder:
            scene.draw()

        if self.__transitionScene is not None:
            self.__transitionScene.draw()

        # FPS Counter
        if Engine.SHOW_FPS_COUNTER:
            fpsCount = str(self.__clock.get_fps())[:4] + " FPS"
            fpsCounter = FontManager.getFont("Emerald32Bold").render(fpsCount, 0, (255, 255, 255))
            self.__window.blit(fpsCounter, (10, 10))

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

    def pushScene(self, scene : Scene, transition : Scene):
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

    def popScene(self, transition : Scene):
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