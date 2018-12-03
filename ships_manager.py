class Ship:
    """
    Class used for storing a single ship.
    """
    def __init__(self, sid, length, width, height, timestamp=None):
        """
        Constructor.
        :param sid: ship id (int)
        :param length: ship length (int)
        :param width: ship width (int)
        :param height: ship height (int)
        :param timestamp: ship timestamp (int) (optional)
        """
        self.sid = sid              # id of a ship
        self.length = length        # length of a ship
        self.width = width          # width of a ship
        self.height = height        # height of a ship
        self.timestamp = timestamp  # timestamp of a ship

    def __str__(self):
        """
        Create a string from the ship without timestamp. It is inversion of from_string(). Used when call print(ship).
        :return: A string describing the ship.
        """
        return f"s{self.sid},{self.width},{self.height},{self.length}"

    def __repr__(self):
        """
        Create a string from the ship without timestamp. Used when call print(list of ships).
        :return: A string describing the ship.
        """
        return f"Ship({self.__str__()})"

    def to_str_with_timestamp(self):
        """
        Create a string from the ship with timestamp.
        :return: A string describing the ship.
        """
        return f"{self.__str__()};t={self.timestamp}"

    def to_string(self):
        """
        The same as __str__()
        :return: A string describing the ship.
        """
        return self.__str__()

    @staticmethod
    def from_string(text):
        """
        Creates a ship from string and return it. Check only if the string can be split to correct number of ints.
        :param text: string in format s{id},{width},{height},{length}
        :return: a ship
        """
        if text[0] != "s":
            return None
        if text[-1] == "\n":
            text = text[0:-1]
        try:
            sid, width, height, length = [int(x) for x in text[1:].split(",")]
        except ValueError:
            return None
        return Ship(sid=sid, width=width, height=height, length=length)


class ShipsManager:
    """
    Class used for storing a list of ships,
    checking if a ship has correct values
    and managing information about available ships.
    """
    def __init__(self, max_available=3, **args):
        """
        Constructor.
        :param max_available: maximum number of ships available in the same time
        :param args: an optional dictionary used for changing default values
        """
        self.max_available = max_available  # maximum number of ships available in the same time
        self.ships = []                     # list of ships
        self.available = []                 # list of available ships

        # default values defining a correct ship
        self.min_length = args.get("min_length", 50)
        self.max_length = args.get("max_length", 100)
        self.min_width = args.get("min_width", 50)
        self.max_width = args.get("max_width", 100)
        self.min_height = args.get("min_height", 50)
        self.max_height = args.get("max_height", 100)

    def __str__(self):
        """
        Create a string from the ships manager. Used when call print(ships manager).
        :return: A string describing the ships manager.
        """
        result = "\n\t".join([f"Ships ({len(self.ships)})"]
                             + [x.to_str_with_timestamp() for x in self.ships])
        if len(self.available) > 0:
            result += "\n" + "\n\t".join([f"Available ({len(self.available)})"]
                                         + [x.to_str_with_timestamp() for x in self.available])
        return result

    def add(self, x, added_timestamp):
        """
        Create a ship from a given string. Check if it is correct and if so, add to list of ships.
        :param x: a string describing a ship
        :param added_timestamp: timestamp added to a ship
        :return: a ship (if successfully added) or None
        """
        if type(added_timestamp) is not int:
            return None
        ship = Ship.from_string(x)
        if ship is not None:
            check_ok = self.min_length <= ship.length <= self.max_length and \
                       self.min_width <= ship.width <= self.max_width and \
                       self.min_height <= ship.height <= self.max_height and \
                       ship.sid not in [x.sid for x in self.ships]
            if check_ok:
                ship.timestamp = added_timestamp
                self.ships.append(ship)
            else:
                ship = None
        return ship

    def get_available(self, max_timestamp):
        """
        Save and get list of available ships.
        :param max_timestamp: maximum timestamp a ship must have
        :return: a list of available ships
        """
        self.available = []
        for ship in reversed(self.ships):
            if ship.timestamp <= max_timestamp:
                self.available.append(ship)
                if len(self.available) >= self.max_available:
                    break
        return self.available



def test():
    s1 = Ship(sid=2, length=4, width=5, height=7, timestamp=39)
    text = s1.to_string()
    print(text)
    s2 = Ship.from_string(text)
    print(s2)
    print(Ship.from_string("s10,1,2,2"))
    print(Ship.from_string("c10,1,2,2"))


def test2():
    sm = ShipsManager(max_available=3)
    sm.add("s10,51,52,52", added_timestamp=2)
    sm.add("s11,51,52,52", added_timestamp=2)
    sm.add("s12,51,52,52", added_timestamp=2)
    sm.add("s13,51,52,52", added_timestamp=3)
    sm.add("s14,51,52,52", added_timestamp=3)
    sm.add("s15,51,52,52", added_timestamp=4)
    sm.add("s12,51,52,52", added_timestamp=4)
    print(sm)
    sm.get_available(max_timestamp=3)
    print(sm)



if __name__ == "__main__":
    test2()
