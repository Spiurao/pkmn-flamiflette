class Tile:

    TYPE_ABOVE_ACTORS = "aboveActors"

    def __init__(self):
        self.surface = None  # the surface of this tile
        self.collision = (False, False, False, False)  # Can the player enter from Top, Right, Bottom, Left