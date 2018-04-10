from typing import Any, Callable


class Timer:

    def __init__(self, tag : Any, duration : int, callback : Callable):
        self.__duration = duration
        self.__callback = callback
        self.__tag = tag

        self.__runningSince = 0

        self.alive = True

    def update(self, dt : int):
        self.__runningSince += dt

        if self.__runningSince >= self.__duration:
            self.alive = False
            self.__callback(self.__tag)
