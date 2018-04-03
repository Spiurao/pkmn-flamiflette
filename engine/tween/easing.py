# from https://github.com/libretro/RetroArch/blob/2f55c5724fd6a299317b34c7518a8bfe26f2b05f/menu/menu_animation.c
import math
class Easing:

    @staticmethod
    def easingLinear(t, b, c, d):
        return c * t / d + b

    @staticmethod
    def easingInOutQuad(t, b, c, d):
        t = t / d * 2
        if t < 1:
            return c / 2 * pow(t, 2) + b
        return -c / 2 * ((t - 1) * (t - 3) - 1) + b

    @staticmethod
    def easingInQuad(t, b, c, d):
        return c * pow(t / d, 2) + b

    @staticmethod
    def easingOutQuad(t, b, c, d):
        t = t / d
        return -c * t * (t - 2) + b

    @staticmethod
    def easingOutInQuad(t, b, c, d):
        if t < d / 2:
            return Easing.easingOutQuad(t * 2, b, c / 2, d)
        return Easing.easingInQuad((t * 2) - d, b + c / 2, c / 2, d)

    @staticmethod
    def easingInCubic(t, b, c, d):
        return c * pow(t / d, 3) + b

    @staticmethod
    def easingOutCubic(t, b, c, d):
        return c * (pow(t / d - 1, 3) + 1) + b

    @staticmethod
    def easingInOutCubic(t, b, c, d):
        t = t / d * 2
        if t < 1:
            return c / 2 * t * t * t + b
        t = t - 2
        return c / 2 * (t * t * t + 2) + b

    @staticmethod
    def easingOutInCubic(t, b, c, d):
        if t < d / 2:
            return Easing.easingOutCubic(t * 2, b, c / 2, d)
        return Easing.easingInCubic((t * 2) - d, b + c / 2, c / 2, d)

    @staticmethod
    def easingInQuart(t, b, c, d):
        return c * pow(t / d, 4) + b

    @staticmethod
    def easingOutQuart(t, b, c, d):
        return -c * (pow(t / d - 1, 4) - 1) + b

    @staticmethod
    def easingInOutQuart(t, b, c, d):
        t = t / d * 2
        if t < 1:
            return c / 2 * pow(t, 4) + b
        return -c / 2 * (pow(t - 2, 4) - 2) + b

    @staticmethod
    def easingOutInQuart(t, b, c, d):
        if t < d / 2:
            return Easing.easingOutQuart(t * 2, b, c / 2, d)
        return Easing.easingInQuart((t * 2) - d, b + c / 2, c / 2, d)

    @staticmethod
    def easingInQuint(t, b, c, d):
        return c * pow(t / d, 5) + b

    @staticmethod
    def easingOutQuint(t, b, c, d):
        return c * (pow(t / d - 1, 5) + 1) + b

    @staticmethod
    def easingInOutQuint(t, b, c, d):
        t = t / d * 2
        if t < 1:
            return c / 2 * pow(t, 5) + b
        return c / 2 * (pow(t - 2, 5) + 2) + b

    @staticmethod
    def easingOutInQuint(t, b, c, d):
        if t < d / 2:
            return Easing.easingOutQuint(t * 2, b, c / 2, d)
        return Easing.easingInQuint((t * 2) - d, b + c / 2, c / 2, d)

    @staticmethod
    def easingInSine(t, b, c, d):
        return -c * math.cos(t / d * (math.pi / 2)) + c + b

    @staticmethod
    def easingOutSine(t, b, c, d):
        return c * math.sin(t / d * (math.pi / 2)) + b

    @staticmethod
    def easingInOutSine(t, b, c, d):
        return -c / 2 * (math.cos(math.pi * t / d) - 1) + b

    @staticmethod
    def easingOutInSine(t, b, c, d):
        if t < d / 2:
            return Easing.easingOutSine(t * 2, b, c / 2, d)
        return Easing.easingInSine((t * 2) - d, b + c / 2, c / 2, d)

    @staticmethod
    def easingInExpo(t, b, c, d):
        if t == 0:
            return b
        return c * math.pow(2, 10 * (t / d - 1)) + b - c * 0.001

    @staticmethod
    def easingOutExpo(t, b, c, d):
        if t == d:
            return b + c
        return c * 1.001 * (-math.pow(2, -10 * t / d) + 1) + b

    @staticmethod
    def easingInOutExpo(t, b, c, d):
        if t == 0:
            return b
        if t == d:
            return b + c
        t = t / d * 2
        if t < 1:
            return c / 2 * math.pow(2, 10 * (t - 1)) + b - c * 0.0005
        return c / 2 * 1.0005 * (-math.pow(2, -10 * (t - 1)) + 2) + b

    @staticmethod
    def easingOutInExpo(t, b, c, d):
        if t < d / 2:
            return Easing.easingOutExpo(t * 2, b, c / 2, d)
        return Easing.easingInExpo((t * 2) - d, b + c / 2, c / 2, d)

    @staticmethod
    def easingInCirc(t, b, c, d):
        return -c * (math.sqrt(1 - math.pow(t / d, 2)) - 1) + b

    @staticmethod
    def easingOutCirc(t, b, c, d):
        return c * math.sqrt(1 - math.pow(t / d - 1, 2)) + b

    @staticmethod
    def easingInOutCirc(t, b, c, d):
        t = t / d * 2
        if t < 1:
            return -c / 2 * (math.sqrt(1 - t * t) - 1) + b
        t = t - 2
        return c / 2 * (math.sqrt(1 - t * t) + 1) + b

    @staticmethod
    def easingOutInCirc(t, b, c, d):
        if t < d / 2:
            return Easing.easingOutCirc(t * 2, b, c / 2, d)
        return Easing.easingInCirc((t * 2) - d, b + c / 2, c / 2, d)

    @staticmethod
    def easingOutBounce(t, b, c, d):
        t = t / d
        if t < 1 / 2.75:
            return c * (7.5625 * t * t) + b
        if t < 2 / 2.75:

            t = t - (1.5 / 2.75)
            return c * (7.5625 * t * t + 0.75) + b

        elif t < 2.5 / 2.75:

            t = t - (2.25 / 2.75)
            return c * (7.5625 * t * t + 0.9375) + b

        t = t - (2.625 / 2.75)
        return c * (7.5625 * t * t + 0.984375) + b

    @staticmethod
    def easingInBounce(t, b, c, d):
        return c - Easing.easingOutBounce(d - t, 0, c, d) + b

    @staticmethod
    def easingInOutBounce(t, b, c, d):
        if t < d / 2:
            return Easing.easingInBounce(t * 2, 0, c, d) * 0.5 + b
        return Easing.easingOutBounce(t * 2 - d, 0, c, d) * 0.5 + c * .5 + b

    @staticmethod
    def easingOutInBounce(t, b, c, d):
        if t < d / 2:
            return Easing.easingOutBounce(t * 2, b, c / 2, d)
        return Easing.easingInBounce((t * 2) - d, b + c / 2, c / 2, d)
