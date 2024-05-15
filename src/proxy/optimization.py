import json
import numpy as np
from scipy.optimize import minimize
from functools import reduce
from math import gcd



class Optimizer:
    def __init__(self, periods, deltas):
        self.periods = periods
        self.deltas = deltas
    
    def lcm(self, a, b):
        return abs(a*b) // gcd(a, b)

    def lcmm(self, *args):
        return reduce(self.lcm, args)

    def delay_window(self, t):
        return np.min([(delta - t) % period for delta, period in zip(self.deltas, self.periods)])

    def objective_function(self, deltas):
        self.deltas = deltas  # Update the deltas
        integral = 0
        dt = 0.1  # integration step size, smaller steps mean higher accuracy
        T0 = self.lcmm(*self.periods)
        for t in np.arange(0, T0, dt):
            integral += self.delay_window(t)
        return integral / T0

    def optimize(self):
        # Ensure the lengths of deltas and periods match
        if len(self.deltas) != len(self.periods):
            raise ValueError("The length of deltas must match the length of periods.")

        # Compute the total period T0
        T0 = self.lcmm(*self.periods)

        # Optimization to find the optimal deltas
        result = minimize(self.objective_function, self.deltas, method='L-BFGS-B', bounds=[(0, T) for T in self.periods])

        return result.x, result.fun

    def save_results(self, file_path, optimized_deltas, optimized_value):
        # Read the existing JSON file
        with open(file_path, 'r') as file:
            data = json.load(file)

        # Append the optimized deltas and the objective function value
        data['optimized_deltas'] = optimized_deltas.tolist()
        data['optimized_value'] = optimized_value

        # Save the updated data back to the JSON file
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)


class DataProcessor:
    def __init__(self, device_info_path, patterns_dict_path):
        self.device_info_path = device_info_path
        self.patterns_dict_path = patterns_dict_path

    def parse_json(self, file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data

    def match_patterns(self, msg_data, patterns):
        matches = []
        for pattern in patterns:
            pattern_length = len(pattern)
            for i in range(len(msg_data) - pattern_length + 1):
                if msg_data[i:i + pattern_length] == pattern:
                    matches.append((pattern, i))
        return matches

    def group_info_by_patterns(self, device_info, patterns_dict):
        result = {}
        
        for device, data in device_info.items():
            msg_data = data['msg_data']
            timestamp_data = data['timestamp_data']
            patterns = patterns_dict.get(device, [])
            
            if not patterns:
                continue
            
            matched_patterns = self.match_patterns(msg_data, patterns)
            
            grouped_data = []
            for idx, (pattern, start_idx) in enumerate(matched_patterns):
                end_idx = start_idx + len(pattern)
                last_timestamp = timestamp_data[end_idx - 1]
                pattern_label = f"KA{idx + 1}_{device}"
                grouped_data.append([pattern_label, last_timestamp])
            
            result[device] = grouped_data
        
        return result
    
    def combine_grouped_data(self, grouped_data):
        combined_data = []
        
        for device, data in grouped_data.items():
            for pattern_label, timestamp in data:
                combined_data.append([pattern_label, timestamp])
        
        # Sort combined data by timestamp
        combined_data.sort(key=lambda x: x[1])
        
        return combined_data
    
    def calculate_average_temporal_distance(self, data):
        # Extract timestamps
        timestamps = [item[1] for item in data]
        
        # Compute temporal distances
        temporal_distances = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
        
        # Calculate the average temporal distance
        if len(temporal_distances) == 0:
            return 0
        average_distance = sum(temporal_distances) / len(temporal_distances)
        
        return average_distance
    
        # Function to calculate time differences (deltas) from a given KA label
    """ def calculate_deltas(self, combined_data, target_label):
        # Split target_label to separate KA label and IP address
        target_ka, target_ip = target_label.split('_')
        print("Target IP: ", target_ip)
        
        # Find the timestamp for the target KA label (T0)
        T0 = None
        start_processing = False
        deltas = []
        seen_ips = set()
        
        for label, timestamp in combined_data:
            ka, ip = label.split('_')
            if not start_processing and ka == target_ka and ip == target_ip:
                T0 = timestamp
                start_processing = True
                continue

            if start_processing:
                if ip == target_ip:
                    continue
                if ip not in seen_ips:
                    delta = timestamp - T0
                    deltas.append([label, delta])
                    seen_ips.add(ip)

        if T0 is None:
            print(f"KA label '{target_label}' not found in the combined data.")

        return deltas, T0 """

    def process_data(self):
        # Parse the device info and patterns dictionary from the JSON files
        device_info = self.parse_json(self.device_info_path)
        patterns_dict = self.parse_json(self.patterns_dict_path)

        # Group the information by patterns
        grouped_data = self.group_info_by_patterns(device_info, patterns_dict)
        combined_data = self.combine_grouped_data(grouped_data)
        """ average_temporal_distance = self.calculate_average_temporal_distance(combined_data)
        deltas, T0 = self.calculate_deltas(combined_data, self.target_label) """

        # Write the grouped data to a file called grouped.json
        output_file_path = 'grouped.json'
        with open(output_file_path, 'w') as output_file:
            json.dump(grouped_data, output_file, indent=4)

        combined_output_file_path = 'combined_grouped.json'
        with open(combined_output_file_path, 'w') as output_file:
            #output_file.write(f"Average Temporal Distance: {average_temporal_distance}\n\n")
            json.dump({"data": combined_data}, output_file, indent=4)

        """ optimization_params_output_file_path = 'optimization_params.json'
        with open(optimization_params_output_file_path, 'w') as output_file:
            json.dump({'T0': T0, 'deltas': deltas}, output_file, indent=4) """

        print(f"Grouped data has been written to {output_file_path}")
        

def calculate_deltas(combined_data, target_label):
        # Split target_label to separate KA label and IP address
        target_ka, target_ip = target_label.split('_')
        print("Target IP: ", target_ip)
        
        # Find the timestamp for the target KA label (T0)
        T0 = None
        start_processing = False
        deltas = []
        seen_ips = set()
        
        for label, timestamp in combined_data:
            ka, ip = label.split('_')
            if not start_processing and ka == target_ka and ip == target_ip:
                T0 = timestamp
                start_processing = True
                continue

            if start_processing:
                if ip == target_ip:
                    continue
                if ip not in seen_ips:
                    delta = timestamp - T0
                    deltas.append([label, delta])
                    seen_ips.add(ip)

        if T0 is None:
            print(f"KA label '{target_label}' not found in the combined data.")

        return deltas, T0