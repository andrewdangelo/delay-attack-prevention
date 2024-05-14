import json

def process_data():
    # Function to read and parse JSON files
    def parse_json(file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data

    # Function to match patterns in the message data
    def match_patterns(msg_data, patterns):
        matches = []
        for pattern in patterns:
            pattern_length = len(pattern)
            for i in range(len(msg_data) - pattern_length + 1):
                if msg_data[i:i + pattern_length] == pattern:
                    matches.append((pattern, i))
        return matches

    # Function to group information by patterns
    def group_info_by_patterns(device_info, patterns_dict):
        result = {}
        
        for device, data in device_info.items():
            msg_data = data['msg_data']
            timestamp_data = data['timestamp_data']
            patterns = patterns_dict.get(device, [])
            
            if not patterns:
                continue
            
            matched_patterns = match_patterns(msg_data, patterns)
            
            grouped_data = []
            for idx, (pattern, start_idx) in enumerate(matched_patterns):
                end_idx = start_idx + len(pattern)
                last_timestamp = timestamp_data[end_idx - 1]
                pattern_label = f"KA{idx + 1}_{device}"
                grouped_data.append([pattern_label, last_timestamp])
            
            result[device] = grouped_data
        
        return result
    
    def combine_grouped_data(grouped_data):
        combined_data = []
        
        for device, data in grouped_data.items():
            for pattern_label, timestamp in data:
                combined_data.append([pattern_label, timestamp])
        
        # Sort combined data by timestamp
        combined_data.sort(key=lambda x: x[1])
        
        return combined_data
    
    def calculate_average_temporal_distance(data):
        # Extract timestamps
        timestamps = [item[1] for item in data]
        
        # Compute temporal distances
        temporal_distances = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
        
        # Calculate the average temporal distance
        if len(temporal_distances) == 0:
            return 0
        average_distance = sum(temporal_distances) / len(temporal_distances)
        
        return average_distance

    # Define the file paths to your JSON files
    device_info_path = 'KAs.json'
    patterns_dict_path = 'keep_alive_patterns.json'

    # Parse the device info and patterns dictionary from the JSON files
    device_info = parse_json(device_info_path)
    patterns_dict = parse_json(patterns_dict_path)

    # Group the information by patterns
    grouped_data = group_info_by_patterns(device_info, patterns_dict)
    combined_data = combine_grouped_data(grouped_data)
    average_temporal_distance = calculate_average_temporal_distance(combined_data)

    # Write the grouped data to a file called grouped.json
    output_file_path = 'grouped.json'
    with open(output_file_path, 'w') as output_file:
        json.dump(grouped_data, output_file, indent=4)

    combined_output_file_path = 'combined_grouped.json'
    with open(combined_output_file_path, 'w') as output_file:
        output_file.write(f"Average Temporal Distance: {average_temporal_distance}\n\n")
        json.dump(combined_data, output_file, indent=4)

    print(f"Grouped data has been written to {output_file_path}")

# Call the function to process the data
process_data()
