from containers_manager import ContainersManager
from optimizer import OptimizerSelector
from ships_manager import ShipsManager
from report_generator import ReportGenerator
from timestamps_manager import TimestampsManager


class Operator:
    """
    Class used for managing the whole system.
    """
    def __init__(self, optimizer_algorithm_file="optimizer_algorithm.txt"):
        """
        Constructor.
        :param optimizer_algorithm_file: a path to file with optimizer algorithm number
        """
        self.optimizer_algorithm_file = optimizer_algorithm_file    # a path to file with optimizer algorithm number

        self.report_generator = None        # a report generator
        self.timestamps_manager = None      # a timestamps manager
        self.ships_manager = None           # a ships manager
        self.containers_manager = None      # a containers manager
        self.optimizer = None               # an optimizer

    def select_optimizer_algorithm(self, optimizer_algorithm=0):
        """
        Select an optimizer algorithm number. If a given number is incorrect, then read a previous one from a file.
        :param optimizer_algorithm: a proposed optimizer algorithm number
        :return: an optimizer algorithm number
        """
        if optimizer_algorithm in OptimizerSelector.correct_algorithms_ids():
            with open(self.optimizer_algorithm_file, "w") as f:
                f.write(str(optimizer_algorithm))
        else:
            with open(self.optimizer_algorithm_file, "r") as f:
                optimizer_algorithm = int(f.read())
        return optimizer_algorithm

    def enter_data_from_file(self, input_file):
        """
        Enter input data from a file. See a sequence diagram.
        :param input_file: a file (name) with input data
        :return:
        """
        self.report_generator.new_section()
        self.report_generator.log(f"Started entering data from {input_file}.")
        self.report_generator.increase_indent()
        with open(input_file, "r") as f:
            for line in f:
                if line[0] == "s":
                    latest_timestamp = self.timestamps_manager.get_max()
                    ship = self.ships_manager.add(line, added_timestamp=latest_timestamp)
                    self.report_generator.add_ship(line, latest_timestamp, ship)
                elif line[0] == "c":
                    latest_timestamp = self.timestamps_manager.get_max()
                    container = self.containers_manager.add(line, min_timestamp=latest_timestamp)
                    if container is not None:
                        self.timestamps_manager.add(container.timestamp)
                    self.report_generator.add_container(line, latest_timestamp, container)
                else:
                    self.report_generator.log(f"Incorrect type of line: {line}")
        self.report_generator.decrease_indent()
        self.report_generator.log(f"Finished entering data.")

    def optimize(self):
        """
        Optimize. See a sequence diagram.
        :return:
        """
        self.timestamps_manager.set_max(self.timestamps_manager.get_min())
        max_timestamp = self.timestamps_manager.get_max()
        self.report_generator.start_optimization()

        uncompleted_shipment = None
        while True:
            containers = self.containers_manager.get_containers(max_timestamp=max_timestamp)
            if len(containers) > 0:
                self.timestamps_manager.set_min(min([c.timestamp for c in containers]))
                ships = self.ships_manager.get_available(max_timestamp=self.timestamps_manager.get_min())
                shipment_manager = self.optimizer.optimize(ships, containers,
                                                           timestamp=max_timestamp,
                                                           container_height=self.containers_manager.const_h,
                                                           previous_shipment=uncompleted_shipment)

                completed_shipments = shipment_manager.shipments[0:-1]
                uncompleted_shipment = shipment_manager.shipments[-1]
                containers_to_send = shipment_manager.get_containers(skip_last_shipment=True)
                self.containers_manager.send(containers_to_send)
                self.report_generator.send_containers(timestamp=max_timestamp,
                                                      available_ships=ships,
                                                      completed_shipments=completed_shipments,
                                                      uncompleted_shipment=uncompleted_shipment)

                next_timestamp = self.timestamps_manager.increase_max()
                if next_timestamp > -1:
                    max_timestamp = next_timestamp
                else:
                    containers_to_send = uncompleted_shipment.get_all_containers()
                    self.containers_manager.send(containers_to_send)
                    self.report_generator.send_containers(timestamp=max_timestamp,
                                                          available_ships=ships,
                                                          completed_shipments=[uncompleted_shipment],
                                                          uncompleted_shipment=None)
                    break
            else:
                break

        self.report_generator.stop_optimization()

    def run(self, input_file="input.txt", log_dir="log", log_file="log.txt", optimizer_algorithm=None):
        """
        Main function.
        :param input_file: a file (name) with input data
        :param log_dir: a directory in which logs will be created
        :param log_file: a basename of a file to which logs will be written
        :param optimizer_algorithm: a proposed optimizer algorithm number
        :return:
        """
        with ReportGenerator(log_dir, log_file) as self.report_generator:
            self.timestamps_manager = TimestampsManager()
            self.ships_manager = ShipsManager()
            self.containers_manager = ContainersManager()

            self.optimizer = OptimizerSelector.select(self.select_optimizer_algorithm(optimizer_algorithm))
            self.report_generator.start(self.ships_manager, self.containers_manager, self.optimizer)

            self.enter_data_from_file(input_file)
            self.report_generator.data_summary(self.ships_manager, self.containers_manager)

            self.optimize()
            self.report_generator.generate_report()

            self.report_generator.stop()


if __name__ == "__main__":
    operator = Operator()
    operator.run(input_file="input_t4.txt")
