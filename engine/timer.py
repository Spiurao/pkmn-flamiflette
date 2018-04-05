class Timer:

    def __init__(self, tag, duration, callback):
        self.__duration = duration
        self.__callback = callback
        self.__tag = tag

        self.__runningSince = 0

        self.alive = True

    def update(self, dt):
        self.__runningSince += dt

        if self.__runningSince >= self.__duration:
            try:
                self.__callback(self.__tag)
            except TypeError:
                raise Exception("Timer callback must have only one argument (tag)")
            self.alive = False
