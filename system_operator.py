from containers_manager import ContainersManager
from optimizer import OptimizerSelector
from ships_manager import ShipsManager
from report_generator import ReportGenerator
from timestamps_manager import TimestampsManager


class Operator:
    def __init__(self):
        self.report_generator = ReportGenerator()
        self.timestamp_manager = TimestampsManager()
        self.ships_manager = ShipsManager()
        self.containers_manager = ContainersManager()
        self.optimizer = OptimizerSelector.select(0)
        self.optimizer_algorithm_file = "optimizer_algorithm.txt"

    def select_optimizer_algorithm(self, optimizer_algorithm):
        if optimizer_algorithm in OptimizerSelector.correct_algorithms_ids():
            with open(self.optimizer_algorithm_file, "w") as f:
                f.write(str(optimizer_algorithm))
        else:
            with open(self.optimizer_algorithm_file, "r") as f:
                optimizer_algorithm = int(f.read())
        return optimizer_algorithm

    def enter_data_from_file(self, input_file):
        self.report_generator.new_section()
        self.report_generator.log(f"Started entering data from {input_file}.")
        self.report_generator.increase_indent()
        with open(input_file, "r") as f:
            for line in f:
                if line[0] == "s":
                    latest_timestamp = self.timestamp_manager.get_max()
                    ship = self.ships_manager.add(line, timestamp=latest_timestamp)
                    self.report_generator.add_ship(line, latest_timestamp, ship)
                elif line[0] == "c":
                    latest_timestamp = self.timestamp_manager.get_max()
                    container = self.containers_manager.add(line, min_timestamp=latest_timestamp)
                    if container is not None:
                        self.timestamp_manager.add(container.timestamp)
                    self.report_generator.add_container(line, latest_timestamp, container)
                else:
                    self.report_generator.log(f"Incorrect type of line: {line}")
        self.report_generator.decrease_indent()
        self.report_generator.log(f"Finished entering data.")

    def run(self, input_file="input.txt", log_dir="log", log_file="log.txt", optimizer_algorithm=None):
        with ReportGenerator(log_dir, log_file) as self.report_generator:
            self.timestamp_manager = TimestampsManager()
            self.ships_manager = ShipsManager()
            self.containers_manager = ContainersManager()
            self.optimizer = OptimizerSelector.select(self.select_optimizer_algorithm(optimizer_algorithm))
            self.report_generator.start(self.ships_manager, self.containers_manager, self.optimizer)

            self.enter_data_from_file(input_file)

            self.report_generator.new_section()
            self.report_generator.log("Data summary:")
            self.report_generator.log(str(self.ships_manager))
            self.report_generator.log(str(self.containers_manager))

            self.report_generator.stop()


if __name__ == "__main__":
    operator = Operator()
    operator.run()
