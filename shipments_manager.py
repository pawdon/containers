import numpy as np

from containers_manager import Container
from ships_manager import Ship


class CornerPosition:
    def __init__(self, length, width, height_level):
        self.length = length
        self.width = width
        self.height_level = height_level

    def to_string(self, order=None):
        if order is None:
            order = ["length", "width", "height"]
        d = {"length": self.length,
             "width": self.width,
             "height": self.height_level}
        return f"{order[0]}={d[order[0]]},{order[1]}={d[order[1]]},{order[2]}={d[order[2]]}"

    def __str__(self):
        return self.to_string()


class PlacedContainer:
    def __init__(self, container, corner1):
        self.container = container
        self.corner1 = corner1
        self.corner2 = CornerPosition(length=corner1.length + container.length,
                                      width=corner1.width + container.width,
                                      height_level=corner1.height_level)

    def __str__(self):
        order = ["height", "length", "width"]
        return f"Container ({self.container.to_string(order)}) at ({self.corner1.to_string(order)})"

    def __repr__(self):
        return self.__str__()


class Shipment:
    def __init__(self, ship, containers_height):
        self.ship = ship
        self.containers_height = containers_height

        self.levels_nr = self.ship.height // self.containers_height
        self.placed_containers = [[] for _ in range(self.levels_nr)]
        self.all_containers = []
        self.occupancy_map = np.zeros(shape=(self.levels_nr, self.ship.length, self.ship.width), dtype=np.int8)

    def to_string(self, get_list=True, get_map=True):
        result = f"Shipment (empty volume = {self.get_empty_volume()}):"
        if get_list:
            result += "\nContainers:"
            for i, level in enumerate(reversed(self.placed_containers)):
                result += f"\n\tLevel {self.levels_nr - i - 1}: {len(level)} containers: {str(level)}"
        if get_map:
            result += "\nOccupancy map:"
            for level in reversed(self.occupancy_map):
                result += f"\n{str(level)}"
        return result

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string(get_map=False)

    def get_empty_volume(self):
        full_volume = self.ship.height * self.ship.length * self.ship.width
        occupied_volume = np.sum(self.occupancy_map) * self.containers_height
        return full_volume - occupied_volume

    def get_all_containers(self):
        return self.all_containers

    def get_timestamps_set(self):
        timestamps = set()
        for container in self.get_all_containers():
            timestamps.add(container.timestamp)
        return timestamps

    def _check_redundancy(self, placed_container):
        return placed_container.container not in self.all_containers

    def _check_if_inside_ship(self, placed_container):
        return 0 <= placed_container.corner1.height_level < self.levels_nr and \
               0 <= placed_container.corner1.length <= self.ship.length and \
               0 <= placed_container.corner1.width <= self.ship.width and \
               0 <= placed_container.corner2.length <= self.ship.length and \
               0 <= placed_container.corner2.width <= self.ship.width

    def _check_if_unoccupied(self, placed_container, checked_map=None):
        if checked_map is None:
            checked_map = self.occupancy_map
        occupied_area = np.sum(checked_map[placed_container.corner1.height_level,
                                           placed_container.corner1.length:placed_container.corner2.length,
                                           placed_container.corner1.width:placed_container.corner2.width])
        return occupied_area == 0

    def _check_if_stable(self, placed_container, checked_map=None):
        if placed_container.corner1.height_level == 0:
            return True
        else:
            if checked_map is None:
                checked_map = self.occupancy_map
            area_below = np.sum(checked_map[placed_container.corner1.height_level - 1,
                                            placed_container.corner1.length:placed_container.corner2.length,
                                            placed_container.corner1.width:placed_container.corner2.width])
            return area_below >= (placed_container.container.length * placed_container.container.width) / 2

    @staticmethod
    def _add_to_map(placed_container, the_map):
        the_map[placed_container.corner1.height_level,
                placed_container.corner1.length:placed_container.corner2.length,
                placed_container.corner1.width:placed_container.corner2.width] = 1

    @staticmethod
    def _remove_from_map(placed_container, the_map):
        the_map[placed_container.corner1.height_level,
                placed_container.corner1.length:placed_container.corner2.length,
                placed_container.corner1.width:placed_container.corner2.width] = 0

    def _add(self, placed_container):
        self._add_to_map(placed_container, self.occupancy_map)
        self.placed_containers[placed_container.corner1.height_level].append(placed_container)
        self.all_containers.append(placed_container.container)

    def _remove(self, placed_container):
        self._remove_from_map(placed_container, self.occupancy_map)
        self.placed_containers[placed_container.corner1.height_level].remove(placed_container)
        self.all_containers.remove(placed_container.container)

    def check_and_add(self, placed_container):
        if self._check_if_inside_ship(placed_container):
            if_can = self._check_if_unoccupied(placed_container) and \
                     self._check_if_stable(placed_container) and \
                     self._check_redundancy(placed_container)
        else:
            if_can = False
        if if_can:
            self._add(placed_container)
        return if_can

    def _get_supported_containers(self, placed_container):
        if placed_container.corner1.height_level >= self.levels_nr - 1:
            return []
        else:
            above_containers = self.placed_containers[placed_container.corner1.height_level + 1]
            if len(above_containers) == 0:
                return []
            map_to_be = np.copy(self.occupancy_map)
            self._remove_from_map(placed_container, map_to_be)
            return [x for x in above_containers if not self._check_if_stable(x, checked_map=map_to_be)]

    def check_and_remove(self, placed_container):
        if placed_container not in self.placed_containers[placed_container.corner1.height_level]:
            if_can = False
        else:
            if_can = len(self._get_supported_containers(placed_container)) == 0
            if if_can:
                self._remove(placed_container)
        return if_can

    def remove_recursively(self, placed_container):
        supported_containers = self._get_supported_containers(placed_container)
        for x in supported_containers:
            self.remove_recursively(x)
        self._remove(placed_container)
        return True


class ShipmentsManager:
    def __init__(self, timestamp):
        self.timestamp = timestamp
        self.shipments = []

    def __str__(self):
        result = f"ShipmentManager (timestamp = {self.timestamp}, empty volume = {self.get_summary_empty_volume()})"
        for sh in self.shipments:
            result += "\n" + sh.to_string(get_map=False)
        return result

    def get_summary_empty_volume(self):
        return sum([sh.get_empty_volume() for sh in self.shipments])

    def get_containers(self, skip_first_shipments=False, skip_last_shipments=False):
        shipments_list = self.shipments
        if skip_first_shipments:
            shipments_list = shipments_list[1:]
        if skip_last_shipments:
            shipments_list = shipments_list[0:-1]
        containers_list = []
        for sh in shipments_list:
            containers_list += sh.get_all_containers()
        return containers_list

    def _check_timestamp(self, shipment):
        if_ok = False
        timestamps_set = shipment.get_timestamps_set()
        if len(self.shipments) == 0:
            if max(timestamps_set) <= self.timestamp:
                if_ok = True
        else:
            if len(timestamps_set) == 1 and self.timestamp in timestamps_set:
                if_ok = True
        return if_ok

    def _check_redundancy(self, shipment):
        if_ok = True
        loaded_containers = self.get_containers()
        for container in shipment.get_all_containers():
            if container in loaded_containers:
                if_ok = False
                break
        return if_ok

    def check_and_add(self, shipment):
        if_can = False
        if type(shipment) is Shipment:
            if_can = self._check_timestamp(shipment) and self._check_redundancy(shipment)
        if if_can:
            self.shipments.append(shipment)
        return if_can

    def check_and_remove(self, shipment):
        if_can = False
        if shipment in self.shipments:
            if len(self.shipments) == 1:
                if_can = True
            elif shipment != self.shipments[0]:
                if_can = True
        if if_can:
            self.shipments.remove(shipment)
        return if_can


def test1():
    s1 = Ship(sid=1, length=5, width=5, height=20, timestamp=39)
    sh = Shipment(s1, containers_height=10)
    print(sh)
    c1 = Container(cid=1, length=2, width=2, height=10, timestamp=39)
    pc1 = PlacedContainer(container=c1, corner1=CornerPosition(height_level=1, length=0, width=0))
    print(sh.check_and_add(pc1))
    print(sh)
    pc1 = PlacedContainer(container=c1, corner1=CornerPosition(height_level=0, length=0, width=0))
    print(sh.check_and_add(pc1))
    c4 = Container(cid=4, length=2, width=2, height=10, timestamp=39)
    pc4 = PlacedContainer(container=c4, corner1=CornerPosition(height_level=0, length=3, width=0))
    print(sh.check_and_add(pc4))
    print(sh)
    print("******************************")
    c2 = Container(cid=2, length=5, width=1, height=10, timestamp=39)
    pc2 = PlacedContainer(container=c2, corner1=CornerPosition(height_level=1, length=0, width=0))
    c3 = Container(cid=3, length=1, width=1, height=10, timestamp=40)
    pc3 = PlacedContainer(container=c3, corner1=CornerPosition(height_level=1, length=0, width=1))
    print(sh.check_and_add(pc2))
    print(sh.check_and_add(pc3))
    print(sh)
    print(sh.check_and_remove(pc4))
    print(sh.remove_recursively(pc4))
    print(sh)
    print(sh.get_all_containers())
    print(sh.get_timestamps_set())


def test2():
    sh1 = Shipment(Ship(sid=1, length=5, width=5, height=20, timestamp=39), containers_height=10)
    sh2 = Shipment(Ship(sid=1, length=5, width=5, height=20, timestamp=39), containers_height=10)
    sh3 = Shipment(Ship(sid=1, length=5, width=5, height=20, timestamp=39), containers_height=10)
    sh4 = Shipment(Ship(sid=1, length=5, width=5, height=20, timestamp=39), containers_height=10)

    sh1.check_and_add(PlacedContainer(container=Container(cid=1, length=1, width=1, height=10, timestamp=39),
                                      corner1=CornerPosition(height_level=0, length=0, width=0)))
    c2 = Container(cid=2, length=1, width=1, height=10, timestamp=40)
    sh1.check_and_add(PlacedContainer(container=c2,
                                      corner1=CornerPosition(height_level=0, length=1, width=0)))

    sh2.check_and_add(PlacedContainer(container=Container(cid=3, length=1, width=1, height=10, timestamp=39),
                                      corner1=CornerPosition(height_level=0, length=0, width=0)))
    sh2.check_and_add(PlacedContainer(container=Container(cid=4, length=1, width=1, height=10, timestamp=40),
                                      corner1=CornerPosition(height_level=0, length=1, width=0)))

    sh3.check_and_add(PlacedContainer(container=Container(cid=5, length=1, width=1, height=10, timestamp=40),
                                      corner1=CornerPosition(height_level=0, length=0, width=0)))
    sh3.check_and_add(PlacedContainer(container=c2,
                                      corner1=CornerPosition(height_level=0, length=1, width=0)))

    sh4.check_and_add(PlacedContainer(container=Container(cid=7, length=1, width=1, height=10, timestamp=40),
                                      corner1=CornerPosition(height_level=0, length=0, width=0)))
    sh4.check_and_add(PlacedContainer(container=Container(cid=8, length=1, width=1, height=10, timestamp=40),
                                      corner1=CornerPosition(height_level=0, length=1, width=0)))

    shm = ShipmentsManager(timestamp=40)
    shm.check_and_add(sh1)
    shm.check_and_add(sh2)
    shm.check_and_add(sh3)
    shm.check_and_add(sh4)
    print(shm)
    shm.check_and_remove(sh2)
    shm.check_and_remove(sh1)
    shm.check_and_remove(sh4)
    print(shm)


if __name__ == "__main__":
    test2()
