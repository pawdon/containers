from datetime import datetime, timedelta
import os
#import plotly
import shutil

from containers_manager import ContainersManager
from ships_manager import ShipsManager
from shipments_manager import ShipmentsManager
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

    def indent(self, indentation):
        self.indentation = indentation

    def increase_indent(self):
        self.indentation += 1

    def decrease_indent(self):
        if self.indentation > 0:
            self.indentation -= 1

    def log(self, text, indent=0, new_section=False):
        if new_section:
            text += "\n"
        for _ in range(indent + self.indentation):
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

    def start_optimization(self, ships_manager, containers_manager):
        pass

    def stop_optimization(self):
        pass

    def send_containers(self, available_ships, sent_containers, not_sent_containers, shipment):
        pass

    def generate_report(self):
        pass


def test():
    with ReportGenerator() as rg:
        sm = ShipsManager(max_available=3)
        cm = ContainersManager()
        rg.start(sm, cm, OptimizerSelector.select(0))
        rg.stop()


if __name__ == "__main__":
    test()
