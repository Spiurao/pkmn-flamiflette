class Tween:
    def __init__(self, alive, duration, runningSince, initialValue, targetValue, subject, tag, easing, cb):
        self.alive = alive
        self.duration = duration
        self.runningSince = runningSince
        self.initialValue = initialValue
        self.targetValue = targetValue
        self.subject = subject
        self.tag = tag
        self.easing = easing
        self.cb = cb

    @staticmethod
    def create(tag, subject, targetValue, duration, easing, cb):
        return Tween(True, duration, 0, None if subject is None else subject.value, targetValue, subject, tag, easing, cb)

    def update(self, dt):
        if not self.alive:
            return

        self.runningSince += dt

        if self.subject is not None:
            self.subject.value = (
                self.easing(
                    self.runningSince,
                    self.initialValue,
                    self.targetValue - self.initialValue,
                    self.duration
                )
            )

        if self.runningSince >= self.duration:
            if self.subject is not None:
                self.subject.value = (
                    self.targetValue
                )
            self.alive = False
            try:
                self.cb(self.tag)
            except TypeError:
                raise Exception("Tween callback must only have one argument (tag)")