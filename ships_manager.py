class Ship:
    def __init__(self, sid, length, width, height, timestamp=None):
        self.sid = sid
        self.length = length
        self.width = width
        self.height = height
        self.timestamp = timestamp

    def __str__(self):
        return f"s{self.sid},{self.width},{self.height},{self.length}"

    def __repr__(self):
        return f"Ship({self.__str__()})"

    def to_str_with_timestamp(self):
        return f"{self.__str__()};t={self.timestamp}"

    def to_string(self):
        return self.__str__()

    @staticmethod
    def from_string(text):
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
    def __init__(self, max_available=3, **args):
        self.max_available = max_available
        self.ships = []
        self.available = []

        self.min_length = args.get("min_length", 50)
        self.max_length = args.get("max_length", 100)
        self.min_width = args.get("min_width", 50)
        self.max_width = args.get("max_width", 100)
        self.min_height = args.get("min_height", 50)
        self.max_height = args.get("max_height", 100)

    def __str__(self):
        result = "\n\t".join([f"Ships ({len(self.ships)})"]
                             + [x.to_str_with_timestamp() for x in self.ships])
        if len(self.available) > 0:
            result += "\n" + "\n\t".join([f"Available ({len(self.available)})"]
                                         + [x.to_str_with_timestamp() for x in self.available])
        return result


    def add(self, x, timestamp):
        if type(timestamp) is not int:
            return None
        ship = Ship.from_string(x)
        if ship is not None:
            check_ok = self.min_length <= ship.length <= self.max_length and \
                       self.min_width <= ship.width <= self.max_width and \
                       self.min_height <= ship.height <= self.max_height
            if check_ok:
                ship.timestamp = timestamp
                self.ships.append(ship)
            else:
                ship = None
        return ship

    def get_available(self, max_timestamp):
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
    sm.add("s10,51,52,52", timestamp=2)
    sm.add("s11,51,52,52", timestamp=2)
    sm.add("s12,51,52,52", timestamp=2)
    sm.add("s13,51,52,52", timestamp=3)
    sm.add("s14,51,52,52", timestamp=3)
    sm.add("s15,51,52,52", timestamp=4)
    print(sm)
    sm.get_available(max_timestamp=3)
    print(sm)



if __name__ == "__main__":
    test2()
