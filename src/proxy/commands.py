
from ipaddress import IPv4Address
import socket, asyncio
from util import *
from TLSRecon import TLSType
import json
from optimization import DataProcessor, Optimizer, calculate_deltas
from optimizer import MessageIntervalOptimizer
import threading

class CommandListener(threading.Thread):
    def __init__(self, data_manager, logger):
        super().__init__()
        self.data_manager = data_manager
        self.logger = logger
        self._stop_event = threading.Event()

    def get_KA(self):
        self.logger.info("Executing get_KA command")
        get_KA(self.data_manager)

    def process_KA(self):
        self.logger.info("Executing process_KA command")
        processor = DataProcessor('KAs.json', 'keep_alive_patterns.json')
        processor.process_data()

    def prepare_optimize(self, command):
        self.logger.info("Executing optimize preparation command")
        
        file_path = 'combined_grouped.json'

        # Read the JSON file
        with open(file_path, 'r') as file:
            data = json.load(file)

        # Extract the list of lists
        combined_data = data["data"]
        # Process the combined data as needed
        target_value = command.split(" ")[1]
        # Call the optimize function with the target value
        deltas, T0 = calculate_deltas(combined_data, target_value)
        
        optimization_params_output_file_path = 'optimization_params.json'

        with open(optimization_params_output_file_path, 'w') as output_file:
            json.dump({'T0': T0, 'deltas': deltas}, output_file, indent=4)

    def optimize(self):
        self.logger.info("Executing optimization command")
        file_path = 'optimization_params.json'

        # Read the JSON file
        with open(file_path, 'r') as file:
            data = json.load(file)

        # Extract the integers from each list in the "deltas" field
        integers_from_deltas = [int(item[1]) for item in data["deltas"]]
        periods = [20, 30, 30]
        optimizer = Optimizer(periods, integers_from_deltas)
        optimized_deltas, optimized_value = optimizer.optimize()
        optimizer.save_results(file_path, optimized_deltas, optimized_value)

    def alt_optimize(self):
        self.logger.info("Executing alternative optimization command")
        file_path = 'combined_grouped.json'

        # Read the JSON file
        with open(file_path, 'r') as file:
            data = json.load(file)

        # Extract the integers from each list in the "deltas" field
        combined_data = data["data"]
        optimizer = MessageIntervalOptimizer(combined_data)
        optimizer.save_results("optimized_delays.json")

    def run(self):
        while not self._stop_event.is_set():
            command = input("Enter command: ").strip()
            if command == "GET_KA":
                self.get_KA()
            elif command == "PROCESS_KA":
                self.process_KA()
            elif command.startswith("PREPARE_OPTIMIZE"):
                self.prepare_optimize(command)
            elif command.startswith("OPTIMIZE"):
                self.optimize()
            elif command == "ALT_OPTIMIZE":
                self.alt_optimize()
            elif command == "KILL":
                self.stop()
            else:
                self.logger.warning("Invalid command")

    def stop(self):
        self._stop_event.set()