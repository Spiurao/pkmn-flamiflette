class InternalTween:
    def __init__(self, alive, duration, runningSince, initialValue, targetValue, subject, tag, easing):
        self.alive = alive
        self.duration = duration
        self.runningSince = runningSince
        self.initialValue = initialValue
        self.targetValue = targetValue
        self.subject = subject
        self.tag = tag
        self.easing = easing
