class DataManager:
    """
    A class that manages data for different devices.

    Attributes:
        device_data (dict): A dictionary that stores data for each device.

    Methods:
        set_msg_data(device, data): Sets the message data for a device.
        get_msg_data(device): Retrieves the message data for a device.
        set_timestamp_data(device, data): Sets the timestamp data for a device.
        get_timestamp_data(device): Retrieves the timestamp data for a device.
        set_address_data(device, data): Sets the address data for a device.
        get_address_data(device): Retrieves the address data for a device.
        print_data(): Prints the data for all devices.
    """

    def __init__(self):
        self.device_data = {}

    def set_msg_data(self, device, data):
        """
        Sets the message data for a device.

        Args:
            device (str): The device identifier.
            data (list): The message data to be set.

        Returns:
            None
        """
        if device not in self.device_data:
            self.device_data[device] = {}
        if 'msg_data' not in self.device_data[device]:
            self.device_data[device]['msg_data'] = []
        self.device_data[device]['msg_data'].append(data)

    def get_msg_data(self, device):
        """
        Retrieves the message data for a device.

        Args:
            device (str): The device identifier.

        Returns:
            list or None: The message data for the device, or None if the device is not found.
        """
        if device in self.device_data:
            return self.device_data[device].get('msg_data')
        return None

    def set_timestamp_data(self, device, data):
        """
        Sets the timestamp data for a device.

        Args:
            device (str): The device identifier.
            data (list): The timestamp data to be set.

        Returns:
            None
        """
        if device not in self.device_data:
            self.device_data[device] = {}
        if 'timestamp_data' not in self.device_data[device]:
            self.device_data[device]['timestamp_data'] = []
        self.device_data[device]['timestamp_data'].append(data)

    def get_timestamp_data(self, device):
        """
        Retrieves the timestamp data for a device.

        Args:
            device (str): The device identifier.

        Returns:
            list or None: The timestamp data for the device, or None if the device is not found.
        """
        if device in self.device_data:
            return self.device_data[device].get('timestamp_data')
        return None

    def set_address_data(self, device, data):
        """
        Sets the address data for a device.

        Args:
            device (str): The device identifier.
            data (list): The address data to be set.

        Returns:
            None
        """
        if device not in self.device_data:
            self.device_data[device] = {}
        if 'address_data' not in self.device_data[device]:
            self.device_data[device]['address_data'] = []
        self.device_data[device]['address_data'].append(data)

    def get_address_data(self, device):
        """
        Retrieves the address data for a device.

        Args:
            device (str): The device identifier.

        Returns:
            list or None: The address data for the device, or None if the device is not found.
        """
        if device in self.device_data:
            return self.device_data[device].get('address_data')
        return None

    def print_data(self):
        """
        Prints the data for all devices.

        Returns:
            None
        """
        for device, data in self.device_data.items():
            print(f"Device: {device}")
            print(f"Message Data: {data.get('msg_data')}")
            print(f"Timestamp Data: {data.get('timestamp_data')}")
            print(f"Address Data: {data.get('address_data')}")
            print()
