from datetime import datetime, timedelta
import os
#import plotly
import shutil

from containers_manager import ContainersManager, Container
from ships_manager import ShipsManager, Ship
from shipments_manager import ShipmentsManager, Shipment, PlacedContainer, CornerPosition
from optimizer import OptimizerSelector


class ReportGenerator:
    def __init__(self, dirname="log", filename="log.txt", if_log_to_file=True, if_print=True):
        self.if_log_to_file = if_log_to_file
        self.if_print = if_print
        self.dirname = dirname
        self.filename = os.path.join(dirname, filename)
        self.logfile = None

        self.start_time = None
        self.stop_time = None
        self.optimization_start_time = None
        self.optimization_stop_time = None
        self.indentation = 0

        self.shipments_list = []

    def __enter__(self):
        if os.path.exists(self.dirname):
            shutil.rmtree(self.dirname)
        os.mkdir(self.dirname)
        self.logfile = open(self.filename, "a+")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logfile.close()

    def new_section(self):
        self.log("")
        self.log("****************************************************************************************************")
        self.log("")

    def indent(self, indentation):
        self.indentation = indentation

    def increase_indent(self):
        self.indentation += 1

    def decrease_indent(self):
        if self.indentation > 0:
            self.indentation -= 1

    def log(self, text, additional_indent=0, new_section=False):
        if new_section:
            text += "\n"
        for _ in range(additional_indent + self.indentation):
            text = "\t" + text
        if self.if_log_to_file:
            self.logfile.write(text + "\n")
        if self.if_print:
            print(text)

    @staticmethod
    def time2str(x):
        return x.strftime("%Y.%m.%d %H:%M:%S")

    def start(self, ships_manager, containers_manager, optimizer):
        self.start_time = datetime.now()
        self.log(f"Started at {self.time2str(self.start_time)}")
        self.new_section()
        self.log("Ships settings:")
        self.increase_indent()
        self.log(f"Maximum number of available ships = {ships_manager.max_available}")
        self.log(f"Acceptable length range = ({ships_manager.min_length}, {ships_manager.max_length})")
        self.log(f"Acceptable width range = ({ships_manager.min_width}, {ships_manager.max_width})")
        self.log(f"Acceptable height range = ({ships_manager.min_height}, {ships_manager.max_height})")
        self.decrease_indent()
        self.log("Containers settings:")
        self.increase_indent()
        self.log(f"Acceptable length range = ({containers_manager.min_length}, {containers_manager.max_length})")
        self.log(f"Acceptable width range = ({containers_manager.min_width}, {containers_manager.max_width})")
        self.log(f"Acceptable height range = ({containers_manager.min_height}, {containers_manager.max_height})")
        self.decrease_indent()
        self.log(optimizer.info())

    def stop(self):
        self.stop_time = datetime.now()
        delta_time = self.stop_time - self.start_time
        self.new_section()
        self.log(f"Whole time = {str(delta_time)}")
        self.log(f"Finished at {self.time2str(self.stop_time)}")

    def add_ship(self, line, timestamp, ship):
        if line[-1] == "\n":
            line = line[0:-1]
        if ship is not None:
            self.log(f"Successfully added a ship {line} with timestamp {timestamp}.")
        else:
            self.log(f"A ship not added. The line {line} is incorrect. "
                     f"The id must be unique, "
                     f"the dimensions must be in the acceptable range.")

    def add_container(self, line, min_timestamp, container):
        if line[-1] == "\n":
            line = line[0:-1]
        if container is not None:
            self.log(f"Successfully added a container {line}.")
        else:
            self.log(f"A container not added. The line {line} is incorrect. "
                     f"The id must be unique, "
                     f"the dimensions must be in the acceptable range "
                     f"and the timestamp must be greater than or equal to {min_timestamp}")

    def data_summary(self, ships_manager, containers_manager):
        self.new_section()
        self.log("Data summary:")
        self.increase_indent()

        self.log(f"Ships ({len(ships_manager.ships)}):")
        self.increase_indent()
        for s in ships_manager.ships:
            self.log(f"{s.to_str_with_timestamp()}")
        self.decrease_indent()

        self.log(f"Containers ({len(containers_manager.waiting_containers)}):")
        self.increase_indent()
        for c in containers_manager.waiting_containers:
            self.log(f"{c}")
        self.decrease_indent()

        self.decrease_indent()

    def start_optimization(self):
        self.optimization_start_time = datetime.now()
        self.new_section()
        self.log(f"Started optimization at {self.time2str(self.optimization_start_time)}")
        self.log("")
        self.increase_indent()

    def stop_optimization(self):
        self.decrease_indent()
        self.optimization_stop_time = datetime.now()
        delta_time = self.optimization_stop_time - self.optimization_start_time
        self.log("")
        self.log(f"Optimization time = {str(delta_time)}")
        self.log(f"Finished optimization at {self.time2str(self.optimization_stop_time)}")

    @staticmethod
    def shipment2str(shipment):
        return f"Shipment (ship = s{shipment.ship.sid}, " \
               f"empty volume = {shipment.get_empty_volume()}, " \
               f"containers number = {len(shipment.get_all_containers())}): " \
               f"{shipment.get_all_containers()}"

    def send_containers(self, timestamp, available_ships, completed_shipments, uncompleted_shipment=None):
        self.log(f"Sending containers for timestamp {timestamp}")
        self.increase_indent()
        self.log(f"Available ships: {available_ships}")
        if len(completed_shipments) > 0:
            first_shipment = completed_shipments[0]
            if first_shipment.ship not in available_ships:
                completed_shipments = completed_shipments[1:]
                self.log("Previous shipment:")
                self.log(self.shipment2str(first_shipment), additional_indent=1)
            if len(completed_shipments) > 0:
                self.log("Completed shipments:")
                self.increase_indent()
                for shipment in completed_shipments:
                    self.shipments_list.append(shipment)
                    self.log(self.shipment2str(shipment))
                self.decrease_indent()
        if uncompleted_shipment is not None:
            self.log("Uncompleted shipment:")
            self.log(self.shipment2str(uncompleted_shipment), additional_indent=1)
        self.decrease_indent()
        self.log("")

    def generate_report(self):
        self.new_section()
        self.log("Report generating")
        sent_containers = sum([len(sh.get_all_containers()) for sh in self.shipments_list])
        self.log(f"Sent {sent_containers} containers.")


def test():
    with ReportGenerator() as rg:
        sm = ShipsManager(max_available=3)
        cm = ContainersManager()
        rg.start(sm, cm, OptimizerSelector.select(0))

        rg.new_section()

        s1 = Ship(sid=1, length=100, width=100, height=100, timestamp=10)
        s2 = Ship(sid=2, length=100, width=100, height=100, timestamp=10)
        s3 = Ship(sid=3, length=100, width=100, height=100, timestamp=10)

        sh1 = Shipment(ship=s1, containers_height=10)
        sh2 = Shipment(ship=s2, containers_height=10)
        sh3 = Shipment(ship=s1, containers_height=10)
        sh4 = Shipment(ship=s1, containers_height=10)

        sh1.check_and_add(PlacedContainer(container=Container(cid=1, length=1, width=3, height=10, timestamp=39),
                                          corner1=CornerPosition(height_level=0, length=0, width=0)))
        sh1.check_and_add(PlacedContainer(container=Container(cid=2, length=1, width=1, height=10, timestamp=39),
                                          corner1=CornerPosition(height_level=0, length=1, width=0)))
        sh2.check_and_add(PlacedContainer(container=Container(cid=3, length=2, width=2, height=10, timestamp=39),
                                          corner1=CornerPosition(height_level=0, length=0, width=0)))
        sh2.check_and_add(PlacedContainer(container=Container(cid=4, length=1, width=1, height=10, timestamp=39),
                                          corner1=CornerPosition(height_level=1, length=0, width=0)))
        sh3.check_and_add(PlacedContainer(container=Container(cid=5, length=15, width=7, height=10, timestamp=39),
                                          corner1=CornerPosition(height_level=0, length=0, width=0)))
        sh4.check_and_add(PlacedContainer(container=Container(cid=6, length=1, width=1, height=10, timestamp=39),
                                          corner1=CornerPosition(height_level=0, length=0, width=0)))

        rg.send_containers(timestamp=39,
                           available_ships=[s1, s2, s3],
                           completed_shipments=[sh1, sh2, sh3],
                           uncompleted_shipment=sh4)

        rg.stop()


if __name__ == "__main__":
    test()
