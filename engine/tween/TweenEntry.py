class TweenEntry:
    def __init__(self, tag, subject, targetValue, duration, easing):
        self.__tag = tag
        self.__subject = subject
        self.__targetValue = targetValue
        self.__duration = duration
        self.__easing = easing

    def getTag(self):
        return self.__tag

    def getSubject(self):
        return self.__subject

    def getTargetValue(self):
        return self.__targetValue

    def getDuration(self):
        return self.__duration

    def getEasing(self):
        return self.__easing