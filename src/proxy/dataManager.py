class DataManager:
    def __init__(self):
        self.device_data = {}

    def set_msg_data(self, device, data):
        if device not in self.device_data:
            self.device_data[device] = {}
        if 'msg_data' not in self.device_data[device]:
            self.device_data[device]['msg_data'] = []
        self.device_data[device]['msg_data'].append(data)

    def get_msg_data(self, device):
        if device in self.device_data:
            return self.device_data[device].get('msg_data')
        return None

    def set_timestamp_data(self, device, data):
        if device not in self.device_data:
            self.device_data[device] = {}
        if 'timestamp_data' not in self.device_data[device]:
            self.device_data[device]['timestamp_data'] = []
        self.device_data[device]['timestamp_data'].append(data)

    def get_timestamp_data(self, device):
        if device in self.device_data:
            return self.device_data[device].get('timestamp_data')
        return None

    def set_address_data(self, device, data):
        if device not in self.device_data:
            self.device_data[device] = {}
        if 'address_data' not in self.device_data[device]:
            self.device_data[device]['address_data'] = []
        self.device_data[device]['address_data'].append(data)

    def get_address_data(self, device):
        if device in self.device_data:
            return self.device_data[device].get('address_data')
        return None

    def print_data(self):
        for device, data in self.device_data.items():
            print(f"Device: {device}")
            print(f"Message Data: {data.get('msg_data')}")
            print(f"Timestamp Data: {data.get('timestamp_data')}")
            print(f"Address Data: {data.get('address_data')}")
            print()
