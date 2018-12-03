import numpy as np

from containers_manager import Container
from ships_manager import Ship


class CornerPosition:
    """
    Class used for storing information about position of a corner of a container.
    """
    def __init__(self, length, width, height_level):
        """
        Constructor
        :param length: corner position in the length axis
        :param width: corner position in the width axis
        :param height_level: corner position in the height axis
        """
        self.length = length                # corner position in the length axis
        self.width = width                  # corner position in the width axis
        self.height_level = height_level    # corner position in the height axis

    def to_ordered_string(self, order=None):
        """
        Create a string from the corner position with named values in a given order.
        :param order: list of strings of named values, eg. ["length", "width", "height"]
        :return: A string describing the corner position.
        """
        if order is None:
            order = ["length", "width", "height"]
        d = {"length": self.length,
             "width": self.width,
             "height": self.height_level}
        return f"{order[0]}={d[order[0]]},{order[1]}={d[order[1]]},{order[2]}={d[order[2]]}"

    def __str__(self):
        """
        Create a string from the corner position. Used when call print(corner position).
        :return: A string describing the corner position.
        """
        return self.to_ordered_string()


class PlacedContainer:
    """
    Class used for storing information about a container and its position.
    """
    def __init__(self, container, corner1):
        """
        Constructor.
        :param container: a container
        :param corner1: a corner position with lower length, width and height_level
        """
        self.container = container                                                  # a container
        self.corner1 = corner1                                                      # the first corner position
        self.corner2 = CornerPosition(length=corner1.length + container.length,     # the second corner position
                                      width=corner1.width + container.width,
                                      height_level=corner1.height_level)

    def __str__(self):
        """
        Create a string from the placed container. Used when call print(placed container).
        :return: A string describing the placed container.
        """
        order = ["height", "length", "width"]
        return f"Container ({self.container.to_ordered_string(order)}) at ({self.corner1.to_ordered_string(order)})"

    def __repr__(self):
        """
        Create a string from the placed container. Used when call print(list of placed container).
        :return: A string describing the placed container.
        """
        return self.__str__()

    def get_shifted_copy(self, diff_length=0, diff_width=0, diff_height_level=0):
        """
        Get shifted copy of the placed container.
        :param diff_length: difference between a current position in the length axis and a new one
        :param diff_width: difference between a current position in the width axis and a new one
        :param diff_height_level: difference between a current position in the height axis and a new one
        :return: a shifted copy of a placed container
        """
        return PlacedContainer(container=self.container,
                               corner1=CornerPosition(length=self.corner1.length + diff_length,
                                                      width=self.corner1.width + diff_width,
                                                      height_level=self.corner1.height_level + diff_height_level))


class Shipment:
    """
    Class used for managing a single shipment.
    """
    def __init__(self, ship, containers_height):
        """
        Constructor.
        :param ship: a ship (basis of a shipment)
        :param containers_height: constant height of containers
        """
        self.ship = ship                            # a ship (basis of a shipment)
        self.containers_height = containers_height  # constant height of containers

        self.levels_nr = self.ship.height // self.containers_height         # number of levels in the height axis
        self.placed_containers_levels = [[] for _ in range(self.levels_nr)] # list of placed containers divided into height levels
        self.all_containers = []                                            # list of all containers

        self.occupancy_map = np.zeros(shape=(self.levels_nr,
                                             self.ship.length,
                                             self.ship.width),
                                      dtype=np.int8)                        # map of occupancy; 0 if unoccupied, 1 if occupied

    def to_string(self, get_list=True, get_map=True):
        """
        Create and return a string describing the shipment.
        :param get_list: (bool) if include information about containers in the shipment
        :param get_map: (bool) if include information about an occupancy map in the shipment
        :return: a string describing the shipment
        """
        result = f"Shipment (empty volume = {self.get_empty_volume()}):"
        if get_list:
            result += "\nContainers:"
            for i, level in enumerate(reversed(self.placed_containers_levels)):
                result += f"\n\tLevel {self.levels_nr - i - 1}: {len(level)} containers: {str(level)}"
        if get_map:
            result += "\nOccupancy map:"
            for level in reversed(self.occupancy_map):
                result += f"\n{str(level)}"
        return result

    def __str__(self):
        """
        Create and return a string describing the shipment. Used when call print(shipment).
        :return: a string describing the shipment
        """
        return self.to_string()

    def __repr__(self):
        """
        Create and return a string describing the shipment. Used when call print(list of shipment).
        :return: a string describing the shipment
        """
        return self.to_string(get_map=False)

    def get_used_levels_nr(self):
        """
        Get a number of used (non empty) levels.
        :return: a number of used (non empty) levels.
        """
        max_used_level = 0
        for level in self.placed_containers_levels:
            if len(level) == 0:
                break
            else:
                max_used_level += 1
        return max_used_level

    def get_empty_volume(self, only_used_levels=False):
        """
        Get empty volume in the shipment.
        :param only_used_levels: (bool) if True than include only information about used height levels
        :return: empty volume in the shipment
        """
        if only_used_levels:
            full_volume = self.containers_height * self.get_used_levels_nr() * self.ship.length * self.ship.width
        else:
            full_volume = self.ship.height * self.ship.length * self.ship.width
        occupied_volume = np.sum(self.occupancy_map) * self.containers_height
        return full_volume - occupied_volume

    def get_all_containers(self):
        """
        Get a list of all containers in the shipment.
        :return: a list of all containers in the shipment
        """
        return self.all_containers

    def get_timestamps_set(self):
        """
        Get a set of timestamps of all containers in the shipment.
        :return: a set of timestamps of all containers in the shipment
        """
        timestamps = set()
        for container in self.get_all_containers():
            timestamps.add(container.timestamp)
        return timestamps

    def _check_redundancy(self, placed_container):
        """
        Private method.
        Check if a given container is in the shipment.
        :param placed_container: a placed container (a candidate to add to the shipment)
        :return: True if a given container is not in the shipment, else False
        """
        return placed_container.container not in self.all_containers

    def _check_if_inside_ship(self, placed_container):
        """
        Private method.
        Check if all corners of a given container are inside the ship.
        :param placed_container: a placed container (a candidate to add to the shipment)
        :return: True if all corners of a given container are inside the ship, else False
        """
        return 0 <= placed_container.corner1.height_level < self.levels_nr and \
               0 <= placed_container.corner1.length <= self.ship.length and \
               0 <= placed_container.corner1.width <= self.ship.width and \
               0 <= placed_container.corner2.length <= self.ship.length and \
               0 <= placed_container.corner2.width <= self.ship.width

    def _check_if_unoccupied(self, placed_container, checked_map=None):
        """
        Private method.
        Check if a space, a given container wants to take, is unoccupied.
        :param placed_container: a placed container (a candidate to add to the shipment)
        :param checked_map: (optional) an occupancy map used for checking
        :return: True if if a space, a given container wants to take, is unoccupied, else False
        """
        if checked_map is None:
            checked_map = self.occupancy_map
        occupied_area = np.sum(checked_map[placed_container.corner1.height_level,
                                           placed_container.corner1.length:placed_container.corner2.length,
                                           placed_container.corner1.width:placed_container.corner2.width])
        return occupied_area == 0

    def _check_if_stable(self, placed_container, checked_map=None):
        """
        Private method.
        Check if a given container would be stable.
        :param placed_container: a placed container (a candidate to add to the shipment)
        :param checked_map: (optional) an occupancy map used for checking
        :return: True if a given container would be stable, else False
        """
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
        """
        Private method.
        Add a given container to an occupancy map.
        :param placed_container: a placed container to add
        :param the_map: an occupancy map
        :return:
        """
        the_map[placed_container.corner1.height_level,
                placed_container.corner1.length:placed_container.corner2.length,
                placed_container.corner1.width:placed_container.corner2.width] = 1

    @staticmethod
    def _remove_from_map(placed_container, the_map):
        """
        Private method.
        Remove a given container from an occupancy map.
        :param placed_container: a placed container to remove
        :param the_map: an occupancy map
        :return:
        """
        the_map[placed_container.corner1.height_level,
                placed_container.corner1.length:placed_container.corner2.length,
                placed_container.corner1.width:placed_container.corner2.width] = 0

    def _add(self, placed_container):
        """
        Private method.
        Add a given container to the occupancy map and lists of containers.
        :param placed_container: a placed container to add
        :return:
        """
        self._add_to_map(placed_container, self.occupancy_map)
        self.placed_containers_levels[placed_container.corner1.height_level].append(placed_container)
        self.all_containers.append(placed_container.container)

    def _remove(self, placed_container):
        """
        Private method.
        Remove a given container from the occupancy map and lists of containers.
        :param placed_container: a placed container to remove
        :return:
        """
        self._remove_from_map(placed_container, self.occupancy_map)
        self.placed_containers_levels[placed_container.corner1.height_level].remove(placed_container)
        self.all_containers.remove(placed_container.container)

    def check_and_add(self, placed_container):
        """
        Check if a given container can be safely added to a shipment and if so, add it.
        A container can be added if:
            - all corners of a given container are inside the ship,
            - a space, a given container wants to take, is unoccupied (overlapping id forbidden),
            - a given container will be stable,
            - a given container is not in the shipment (redundancy is forbidden).
        :param placed_container: a placed container to add
        :return: True if successfully added, else False
        """
        if_can = False
        if self._check_if_inside_ship(placed_container):
            if_can = self._check_if_unoccupied(placed_container) and \
                     self._check_if_stable(placed_container) and \
                     self._check_redundancy(placed_container)
        if if_can:
            self._add(placed_container)
        return if_can

    def check_and_join(self, shipment):
        """
        Check if all containers from the given shipment can be added to this shipment and if so, add it.
        All containers are added or none of them.
        Height levels of a joined shipment will be put above height levels of this shipment.
        A shipment can be added if:
            - it is based on the same ship as this shipment,
            - sum of used height levels in both shipments is less than or equal to the maximum number of height levels for the ship
            - every container will be stable,
            - no container from the joined shipment is in this shipment (redundancy is forbidden).
        :param shipment: a joined shipment
        :return: True if successfully added, else False
        """
        if_can = False
        placed_containers_to_add = []
        if self.ship == shipment.ship:
            used_levels_nr = self.get_used_levels_nr()
            if used_levels_nr + shipment.get_used_levels_nr() <= self.levels_nr:
                if_can = True
                for level in shipment.placed_containers_levels:
                    if not if_can:
                        break
                    for placed_container in level:
                        new_placed_container = placed_container.get_shifted_copy(diff_height_level=used_levels_nr)
                        if_can_new = self._check_if_stable(placed_container) and \
                                     self._check_redundancy(placed_container)
                        if if_can_new:
                            placed_containers_to_add.append(new_placed_container)
                        else:
                            if_can = False
                            break
        if if_can:
            for placed_container in placed_containers_to_add:
                self._add(placed_container)
        return if_can

    def _get_supported_containers(self, placed_container):
        """
        Return list of containers supported by a given container (list of containers which would be unstable if a given
        container was removed).
        :param placed_container: a placed container
        :return: list of containers
        """
        if placed_container.corner1.height_level >= self.levels_nr - 1:
            return []
        else:
            above_containers = self.placed_containers_levels[placed_container.corner1.height_level + 1]
            if len(above_containers) == 0:
                return []
            map_to_be = np.copy(self.occupancy_map)
            self._remove_from_map(placed_container, map_to_be)
            return [x for x in above_containers if not self._check_if_stable(x, checked_map=map_to_be)]

    def check_and_remove(self, placed_container):
        """
        Check if removing a given container would cause instability of any other container and if no, remove it.
        :param placed_container: a placed container to remove
        :return: True if successfully removed, else False
        """
        if placed_container not in self.placed_containers_levels[placed_container.corner1.height_level]:
            if_can = False
        else:
            if_can = len(self._get_supported_containers(placed_container)) == 0
            if if_can:
                self._remove(placed_container)
        return if_can

    def remove_recursively(self, placed_container):
        """
        Remove a given container and all containers which will become unstable.
        :param placed_container: a placed container to remove
        :return: True
        """
        supported_containers = self._get_supported_containers(placed_container)
        for x in supported_containers:
            self.remove_recursively(x)
        self._remove(placed_container)
        return True


class ShipmentsManager:
    """
    Class used for storing and managing shipments.
    """
    def __init__(self, main_timestamp):
        """
        Constructor.
        :param main_timestamp: main timestamp for the shipments
        """
        self.main_timestamp = main_timestamp    # main timestamp for the shipments
        self.shipments = []                     # list of shipments

    def __str__(self):
        """
        Create a string describing the shipments manager. Used when call print(shipments manager).
        :return: a string describing the shipments manager
        """
        result = f"ShipmentManager (timestamp = {self.main_timestamp}, " \
                 f"empty volume = {self.get_summary_empty_volume()})"
        for sh in self.shipments:
            result += "\n" + sh.to_ordered_string(get_map=False)
        return result

    def get_summary_empty_volume(self, only_used_levels=False):
        """
        Get a summary empty volume in all shipments.
        :param only_used_levels: (bool) if True than include only information about used height levels
        :return: a summary empty volume in all shipments
        """
        return sum([sh.get_empty_volume(only_used_levels) for sh in self.shipments])

    def get_containers(self, skip_first_shipment=False, skip_last_shipment=False):
        """
        Get a list of containers in all shipments.
        :param skip_first_shipment: (bool) if True, skip first shipment
        :param skip_last_shipment:  (bool) if True, skip last shipment
        :return: a list of containers in all shipments
        """
        shipments_list = self.shipments
        if skip_first_shipment:
            shipments_list = shipments_list[1:]
        if skip_last_shipment:
            shipments_list = shipments_list[0:-1]
        containers_list = []
        for sh in shipments_list:
            containers_list += sh.get_all_containers()
        return containers_list

    def _check_shipment_timestamps(self, shipment):
        """
        Private method.
        Check timestamps of all containers in a given shipment. In first shipment there can be timestamps lower than
        or equal to the main timestamp. In all other shipments there can be only timestamps equal to the main timestamp.
        :param shipment: a shipment to verify
        :return: True if timestamps in a given shipment are correct, else False
        """
        if_ok = False
        timestamps_set = shipment.get_timestamps_set()
        if len(self.shipments) == 0:
            if max(timestamps_set) <= self.main_timestamp:
                if_ok = True
        else:
            if len(timestamps_set) == 1 and self.main_timestamp in timestamps_set:
                if_ok = True
        return if_ok

    def _check_redundancy(self, shipment):
        """
        Private method.
        Check if there is no containers redundancy in the already added shipments and a given shipment.
        :param shipment: a shipment to verify
        :return: True if there is no redundancy, else False
        """
        if_ok = True
        loaded_containers = self.get_containers()
        for container in shipment.get_all_containers():
            if container in loaded_containers:
                if_ok = False
                break
        return if_ok

    def check_and_add(self, shipment):
        """
        Check if a given shipment can be added to list and if so, add it.
        A shipment can be added if
            - its containers have correct timestamps,
            - no container from the given shipment is in the already added shipments (redundancy is forbidden).
        :param shipment: a shipment to add
        :return: True if successfully added, else False
        """
        if_can = False
        if type(shipment) is Shipment:
            if_can = self._check_shipment_timestamps(shipment) and self._check_redundancy(shipment)
        if if_can:
            self.shipments.append(shipment)
        return if_can

    def check_and_remove(self, shipment):
        """
        Check if a given shipment can be removed and if so, remove it.
        A shipment can not be removed only if it is the first shipment and there are other shipments.
        Read a description of _check_shipment_timestamps() to know why.
        :param shipment: a shipment to remove.
        :return: True if successfully removed, else False
        """
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

    shm = ShipmentsManager(main_timestamp=40)
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
