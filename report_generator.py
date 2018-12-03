from datetime import datetime, timedelta
import os
#import plotly
import shutil

from containers_manager import ContainersManager, Container
from ships_manager import ShipsManager, Ship
from shipments_manager import ShipmentsManager, Shipment, PlacedContainer, CornerPosition
from optimizer import OptimizerSelector


class ReportGenerator:
    """
    Class used for logging and generating report.
    """
    def __init__(self, dirname="log", filename="log.txt", if_log_to_file=True, if_print=True):
        """
        Constructor.
        :param dirname: a directory in which logs will be created
        :param filename: a basename of a file to which logs will be written
        :param if_log_to_file: (bool) if log to file
        :param if_print: (bool) if log using print
        """
        self.if_log_to_file = if_log_to_file                # (bool) if log to file
        self.if_print = if_print                            # (bool) if log using print
        self.dirname = dirname                              # a directory in which logs will be created
        self.filename = os.path.join(dirname, filename)     # a file to which logs will be written
        self.logfile = None                                 # an opened log file

        self.start_datetime = None                          # start datetime
        self.stop_datetime = None                           # stop datetime
        self.optimization_start_datetime = None             # optimization start datetime
        self.optimization_stop_datetime = None              # optimization stop datetime
        self.indentation = 0                                # indentation number

        self.shipments_list = []                            # list of sent shipments

    def __enter__(self):
        """
        Open a log file. Used automatically at the beginning of "with".
        :return: a report generator with opened log file
        """
        if os.path.exists(self.dirname):
            shutil.rmtree(self.dirname)
        os.mkdir(self.dirname)
        self.logfile = open(self.filename, "a+")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Close log file. Used automatically at the end of "with".
        :param exc_type:
        :param exc_val:
        :param exc_tb:
        :return:
        """
        self.logfile.close()

    def new_section(self):
        """
        Log new section.
        :return:
        """
        self.log("")
        self.log("****************************************************************************************************")
        self.log("")

    def indent(self, indentation):
        """
        Set indentation.
        :param indentation: an indentation to set
        :return:
        """
        self.indentation = indentation

    def increase_indent(self):
        """
        Increase indentation.
        :return:
        """
        self.indentation += 1

    def decrease_indent(self):
        """
        Decrease indentation.
        :return:
        """
        if self.indentation > 0:
            self.indentation -= 1

    def log(self, text, additional_indent=0, new_section=False):
        """
        Log a message.
        :param text: a message to log
        :param additional_indent: number of additional indentations
        :param new_section: (bool) if call new_section() at the beginning
        :return:
        """
        if new_section:
            self.new_section()
        for _ in range(additional_indent + self.indentation):
            text = "\t" + text
        if self.if_log_to_file:
            self.logfile.write(text + "\n")
        if self.if_print:
            print(text)

    @staticmethod
    def datetime2str(x):
        """
        Convert a datetime to a string.
        :param x: a datetime
        :return: a string
        """
        return x.strftime("%Y.%m.%d %H:%M:%S")

    def start(self, ships_manager, containers_manager, optimizer):
        """
        Log start of the program.
        :param ships_manager: ships manager
        :param containers_manager: containers manager
        :param optimizer: optimizer
        :return:
        """
        self.start_datetime = datetime.now()
        self.log(f"Started at {self.datetime2str(self.start_datetime)}")
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
        """
        Log stop of the program.
        :return:
        """
        self.stop_datetime = datetime.now()
        delta_time = self.stop_datetime - self.start_datetime
        self.new_section()
        self.log(f"Whole time = {str(delta_time)}")
        self.log(f"Finished at {self.datetime2str(self.stop_datetime)}")

    def add_ship(self, line, timestamp, ship):
        """
        Log adding a ship.
        :param line: a line generating a ship
        :param timestamp: a timestamp
        :param ship: a ship or None
        :return:
        """
        if line[-1] == "\n":
            line = line[0:-1]
        if ship is not None:
            self.log(f"Successfully added a ship {line} with timestamp {timestamp}.")
        else:
            self.log(f"A ship not added. The line {line} is incorrect. "
                     f"The id must be unique, "
                     f"the dimensions must be in the acceptable range.")

    def add_container(self, line, min_timestamp, container):
        """
        Log adding a container.
        :param line: a line generating a container
        :param min_timestamp: a timestamp
        :param container: a container or None
        :return:
        """
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
        """
        Log data summary.
        :param ships_manager: ships manager
        :param containers_manager: containers manager
        :return:
        """
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
        """
        Log start optimization.
        :return:
        """
        self.optimization_start_datetime = datetime.now()
        self.new_section()
        self.log(f"Started optimization at {self.datetime2str(self.optimization_start_datetime)}")
        self.log("")
        self.increase_indent()

    def stop_optimization(self):
        """
        Log stop optimization.
        :return:
        """
        self.decrease_indent()
        self.optimization_stop_datetime = datetime.now()
        delta_time = self.optimization_stop_datetime - self.optimization_start_datetime
        self.log("")
        self.log(f"Optimization time = {str(delta_time)}")
        self.log(f"Finished optimization at {self.datetime2str(self.optimization_stop_datetime)}")

    @staticmethod
    def shipment2str(shipment):
        """
        Convert a shipment to a string.
        :param shipment: a shipment
        :return: a string
        """
        return f"Shipment (ship = s{shipment.ship.sid}, " \
               f"empty volume = {shipment.get_empty_volume()}, " \
               f"containers number = {len(shipment.get_all_containers())}): " \
               f"{shipment.get_all_containers()}"

    def send_containers(self, timestamp, available_ships, completed_shipments, uncompleted_shipment=None):
        """
        Log sending containers.
        :param timestamp: a main shipment timestamp
        :param available_ships: a list of available ships
        :param completed_shipments: a list of completed shipments
        :param uncompleted_shipment: an uncompleted shipment
        :return:
        """
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
        """
        Generate report.
        :return:
        """
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
