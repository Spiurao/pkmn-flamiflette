class Tile:

    TYPE_ABOVE_EVENTS = "aboveEvents"

    def __init__(self):
        self.surface = None  # the surface of this tile
        self.collision = (False, False, False, False)  # Can the player enter from Top, Right, Bottom, Left