
import json
import numpy as np

class MessageIntervalOptimizer:
    def __init__(self, data, learning_rate=0.01, num_iterations=1000, initial_delay_range=0.1):
        self.data = data
        self.learning_rate = learning_rate
        self.num_iterations = num_iterations
        self.initial_delay_range = initial_delay_range
        self.delays = {}
        self._parse_data()

    def _parse_data(self):
        self.data_dict = {}
        for entry in self.data:
            label, timestamp = entry
            ip = label.split('_')[1]
            if ip not in self.data_dict:
                self.data_dict[ip] = []
            self.data_dict[ip].append(timestamp)

        self.timestamps = [timestamp for sublist in self.data_dict.values() for timestamp in sublist]
        self.ips = [ip for ip, sublist in self.data_dict.items() for _ in sublist]
        self.unique_ips = list(self.data_dict.keys())
        self.delays = {ip: np.random.uniform(-self.initial_delay_range, self.initial_delay_range) for ip in self.unique_ips}

    def _apply_delays(self, timestamps, ips, delays):
        return [timestamp + delays[ip] for timestamp, ip in zip(timestamps, ips)]

    def _calculate_intervals(self, timestamps):
        sorted_timestamps = sorted(timestamps)
        intervals = [sorted_timestamps[i] - sorted_timestamps[i - 1] for i in range(1, len(sorted_timestamps))]
        return intervals

    def optimize(self):
        # Calculate the original intervals and average interval before any optimization
        original_intervals = self._calculate_intervals(self.timestamps)
        original_avg_interval = np.mean(original_intervals)
        original_max_interval = np.max(original_intervals)

        for iteration in range(self.num_iterations):
            adjusted_timestamps = self._apply_delays(self.timestamps, self.ips, self.delays)
            current_intervals = self._calculate_intervals(adjusted_timestamps)
            current_max_interval = np.max(current_intervals)

            gradients = {}
            for ip in self.unique_ips:
                original_delay = self.delays[ip]
                delta = self.learning_rate

                # Perturb the delay
                self.delays[ip] += delta
                adjusted_timestamps = self._apply_delays(self.timestamps, self.ips, self.delays)
                new_intervals = self._calculate_intervals(adjusted_timestamps)
                new_max_interval = np.max(new_intervals)

                # Calculate the gradient
                gradients[ip] = (new_max_interval - current_max_interval) / delta
                self.delays[ip] = original_delay

            # Update the delays based on gradients
            for ip in self.unique_ips:
                self.delays[ip] -= self.learning_rate * gradients[ip]

            # Reduce learning rate over time
            self.learning_rate *= 0.99

            if iteration % 100 == 0:
                current_max_interval = np.max(self._calculate_intervals(self._apply_delays(self.timestamps, self.ips, self.delays)))
                print(f"Iteration {iteration}, Max Interval: {current_max_interval}")

        optimized_timestamps = self._apply_delays(self.timestamps, self.ips, self.delays)
        optimized_intervals = self._calculate_intervals(optimized_timestamps)
        optimized_avg_interval = np.mean(optimized_intervals)
        optimized_max_interval = np.max(optimized_intervals)

        return self.delays, original_avg_interval, original_max_interval, optimized_avg_interval, optimized_max_interval

    def save_results(self, file_path):
        delays, original_avg_interval, original_max_interval, optimized_avg_interval, optimized_max_interval = self.optimize()
        results = {
            "original_average_interval": original_avg_interval,
            "original_max_interval": original_max_interval,
            "optimized_average_interval": optimized_avg_interval,
            "optimized_max_interval": optimized_max_interval,
            "optimized_delays": delays
        }
        with open(file_path, 'w') as f:
            json.dump(results, f, indent=4)