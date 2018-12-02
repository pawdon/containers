import datetime
import random

from containers_manager import Container
from ships_manager import Ship


class DataGenerator:
    def __init__(self, containers_nr, ships_nr=3, timestamps_nr=10, only_correct_timestamps=True, **args):
        self.containers_nr = containers_nr
        self.ships_nr = ships_nr
        self.timestamps_nr = timestamps_nr
        self.only_correct_timestamps = only_correct_timestamps

        self.containers = []
        self.ships = []
        self.timestamps = []

        self.simultaneous_ships = args.get("simultaneous_ships", 3)
        self.ship_min_length = args.get("ship_min_length", 50)
        self.ship_max_length = args.get("ship_max_length", 100)
        self.ship_min_width = args.get("ship_min_width", 50)
        self.ship_max_width = args.get("ship_max_width", 100)
        self.ship_min_height = args.get("ship_min_height", 50)
        self.ship_max_height = args.get("ship_max_height", 100)

        self.container_min_length = args.get("container_min_length", 1)
        self.container_max_length = args.get("container_max_length", 40)
        self.container_min_width = args.get("container_min_width", 1)
        self.container_max_width = args.get("container_max_width", 40)
        self.container_min_height = args.get("container_min_height", 1)
        self.container_max_height = args.get("container_max_height", 40)

    def __str__(self):
        return "\n\t".join([f"Ships ({len(self.ships)}):"] + [str(x) for x in self.ships]) + "\n" + \
               "\n\t".join([f"Containers ({len(self.containers)}):"] + [str(x) for x in self.containers])

    def rand_timestamps(self):
        while len(self.timestamps) < self.timestamps_nr:
            rand = random.randint(0, 10*self.timestamps_nr)
            if rand not in self.timestamps:
                self.timestamps.append(rand)
        self.timestamps = sorted(self.timestamps)

    def rand_containers(self, const_h):
        for i in range(self.containers_nr):
            l = random.randint(self.container_min_length, self.container_max_length)
            w = random.randint(self.container_min_width, self.container_max_width)
            t = random.choice(self.timestamps)
            self.containers.append(Container(cid=i, length=l, width=w, height=const_h, timestamp=t))
        if self.only_correct_timestamps:
            self.containers = sorted(self.containers, key=lambda x: x.timestamp)

    def rand_ships(self):
        for i in range(self.ships_nr):
            l = random.randint(self.ship_min_length, self.ship_max_length)
            w = random.randint(self.ship_min_width, self.ship_max_width)
            h = random.randint(self.ship_min_height, self.ship_max_height)
            self.ships.append(Ship(sid=i, length=l, width=w, height=h))

    def rand_and_write(self, filename="input.txt"):
        self.rand_timestamps()
        self.rand_containers(const_h=random.randint(self.container_min_height, self.container_max_height))
        self.rand_ships()
        list_to_save = [str(x) for x in self.containers]
        list_to_save.insert(0, str(self.ships[0]))
        for i in range(1, self.ships_nr):
            j = random.randint(0, self.containers_nr)
            list_to_save.insert(j, str(self.ships[i]))
        str_to_save = "\n".join(list_to_save)
        with open(filename, "w") as f:
            f.write(str_to_save)


def test():
    dg = DataGenerator(containers_nr=100, ships_nr=5, timestamps_nr=4, only_correct_timestamps=True)
    dg.rand_and_write(filename="input_t4.txt")
    print(dg)


if __name__ == "__main__":
    test()
