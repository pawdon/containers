import random
from shipments_manager import ShipmentsManager, Shipment, PlacedContainer, CornerPosition


class IOptimizer:
    def __init__(self):
        self.shipments_manager = None
        self.container_height = None
        self.ships = None
        self.containers = None
        self.timestamp = None
        self.previous_shipment = None

    @staticmethod
    def info():
        return "Abstract optimizer interface"

    def optimize(self, ships, containers, timestamp, container_height, previous_shipment):
        self.shipments_manager = ShipmentsManager(timestamp)
        return self.shipments_manager


class OptimizerSelector:
    @staticmethod
    def select(nr=1):
        if nr == 1:
            return Optimizer1()
        else:
            return IOptimizer()

    @staticmethod
    def correct_algorithms_ids():
        return [1]


class Optimizer1(IOptimizer):
    def __init__(self):
        super().__init__()

    @staticmethod
    def info():
        return "Stupid optimizer"

    def new_shipment(self):
        ship = random.choice(self.ships)
        shipment = Shipment(ship, containers_height=self.container_height)
        return shipment

    def place_container(self, container, shipment):
        for l in range(shipment.ship.length):
            for w in range(shipment.ship.width):
                if shipment.check_and_add(PlacedContainer(container,
                                                          corner1=CornerPosition(length=l, width=w, height_level=0))):
                    return True
        return False

    def optimize(self, ships, containers, timestamp, container_height, previous_shipment):
        """

        :param ships:
        :param containers:
        :param timestamp:
        :param container_height:
        :param previous_shipment:
        Sytuacja w której to jest użyte:
        W poprzedniej turze mieliśmy duży fajny statek. Nie zapakowaliśmy go do końca, więc nie wysłaliśmy ostatniej
        partii. Teraz nie mamy już tego statku. Okazało się, że nie jesteśmy w stanie wysłać naraz zalegających
        kontenerów nowymi statkami, ale musimy to jakoś zrobić. W związku z tym wysyłamy tamten duży statek tak,
        jak mogliśmy.
        :return:
        """
        self.container_height = container_height
        self.containers = containers
        self.ships = ships
        self.timestamp = timestamp
        self.previous_shipment = previous_shipment
        self.shipments_manager = ShipmentsManager(timestamp)

        use_previous_shipment = False

        shipment = self.new_shipment()
        for container in self.containers:
            if use_previous_shipment:
                if container in self.previous_shipment.get_all_containers():
                    continue
            if_success = self.place_container(container, shipment)
            if not if_success:
                if container.timestamp < self.timestamp:
                    """
                    To jest właśnie ta sytuacja
                    """
                    use_previous_shipment = True
                    self.shipments_manager.check_and_add(self.previous_shipment)
                else:
                    self.shipments_manager.check_and_add(shipment)
                    shipment = self.new_shipment()
                    self.place_container(container, shipment)
        self.shipments_manager.check_and_add(shipment)
        return self.shipments_manager

