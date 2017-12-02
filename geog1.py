
class Direction:
    def __getitem__(self, item):
        if item in self.__dict__:
            return self.__dict__[item]

    def move_into(self):
        raise NotImplementedError


class Obstruction(Direction):
    def __init__(self, false_message):
        default_false_message = "There is an obstruction this way."
        self.false_message = false_message or default_false_message

    def move_into(self):
        return (False, self.false_message)


class Wall(Obstruction):
    def __init__(self):
        false_message = "That's a wall, you idiot."
        super().__init__(false_message)


class Room(Direction):
    """
    Class for holding relations between rooms and properties in them.
    """

    def __init__(self, ident, desc, n=None, e=None, s=None, w=None, items=[]):
        self.ident = ident
        self.desc = desc
        self.n = n
        self.e = e
        self.s = s
        self.w = w
        self.items = items

    def move_into(self):
        return (True, "You entered {}.".format(self.desc))


class Geography:
    GEOGRAPHY = {
        0: Room(0, "Lobby", n=1, e=Wall(), s=Wall(), w=Wall()),
        1: Room(1, "Dungeon", n=Wall(), e=2, s=0, w=Wall()),
        2: Room(2, "Second Dungeon", n=Wall(), e=Wall(), s=Wall(), w= Wall()),
    }

    @classmethod
    def get_direction(cls, location, direction):
        new_location = cls.GEOGRAPHY[location][direction]
        if isinstance(new_location, int):
            return cls.GEOGRAPHY[new_location]
        elif isinstance(new_location, Obstruction):
            return new_location

    @classmethod
    def resolve_direction(cls, current, turn):
        res = {
            "right": {"n": "e", "e": "s", "s": "w", "w": "n"},
            "left": {"n": "w", "w": "s", "s": "e", "e": "n"}
        }
        return res[turn][current]

    @classmethod
    def direction_name(cls, direction):
        compass = {"n": "North", "w": "West", "e": "East", "s": "South"}
        return compass[direction]


class testplayer:
    def __init__(self):
        self.location = 0
        self.orientation = "n"

    def compass(self):
        orient = Geography.direction_name(self.orientation)
        print("You are facing {}".format(orient))

    def turn(self, turn):
        self.orientation = Geography.resolve_direction(self.orientation, turn)
        print(self.compass())

    def move_forward(self):
        destination = Geography.get_direction(self.location, self.orientation)
        success, message = destination.move_into()
        if success:
            self.location = destination.ident
            print(message)
        else:
            print(message)
