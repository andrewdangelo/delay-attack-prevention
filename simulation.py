from scapy.all import *
import time
import random
import argparse


# Mock IP addresses
client_ip = "192.168.1.2"
hub_ip = "192.168.1.1"
router_ip = "10.0.0.1"
cloud_server_ip = "10.0.0.2"

class Packet:
    def __init__(self, src, dst, seq=0, ack=0, flags='', payload=''):
        self.src = src
        self.dst = dst
        self.seq = seq
        self.ack = ack
        self.flags = flags
        self.payload = payload

    def summary(self):
        return f"Packet(src={self.src}, dst={self.dst}, seq={self.seq}, ack={self.ack}, flags={self.flags}, payload='{self.payload}')"

class TLSHandshakePacket(Packet):
    def __init__(self, src, dst, payload='', seq=0, ack=0, flags='', handshake_step=''):
        super().__init__(src, dst, seq, ack, flags, payload)
        self.handshake_step = handshake_step

class KeepAlivePacket(Packet):
    def __init__(self, src, dst, seq=0, ack=0):
        super().__init__(src, dst, seq, ack, 'A', 'KEEPALIVE')

class IoTDevice:
    def __init__(self, device_id, hub):
        self.device_id = device_id
        self.hub = hub

    def send_data(self, data):
        print(f"IoT Device {self.device_id}: Sending data -> '{data}'")
        data_packet = Packet(src=self.device_id, dst=hub_ip, payload=data)
        self.hub.forward(data_packet)

class Hub:
    def forward(self, packet):
        print(f"Hub: Forwarding {packet.summary()} from {packet.src} to all ports")
        if packet.src.startswith("IoT"):
            router.process_packet(packet)
        else:
            router.process_packet(packet)

class Router:
    def __init__(self):
        # Include hub_ip in routing to simulate forwarding to the cloud server
        self.routing_table = {cloud_server_ip: "Cloud Server", hub_ip: "Hub"}

    def process_packet(self, packet):
        # Adjusted to check if packet destination is the cloud server or requires forwarding through the hub
        if packet.dst in self.routing_table:
            print(f"Router: Routing {packet.summary()} to {self.routing_table[packet.dst]}")
            # Forward to cloud server directly if destination is cloud server
            if packet.dst == cloud_server_ip:
                cloud_server.receive_packet(packet)
            # Additional logic for forwarding from hub to cloud server could be added here
        else:
            print("Router: Destination unreachable")

class CloudServer:
    def receive_packet(self, packet):
        print(f"Cloud Server: Received {packet.summary()}")
        if isinstance(packet, TLSHandshakePacket):
            self.handle_tls_handshake(packet)
        elif packet.flags == 'S':
            self.handle_syn(packet)
        elif packet.src.startswith("IoT"):
            self.process_iot_data(packet)

    def handle_syn(self, packet):
        syn_ack_packet = Packet(src=cloud_server_ip, dst=packet.src, seq=1000, ack=packet.seq + 1, flags='SA')
        print(f"Cloud Server: Sending SYN-ACK {syn_ack_packet.summary()}")
        client.receive_packet(syn_ack_packet)

    def handle_tls_handshake(self, packet):
        if packet.handshake_step == "ClientHello":
            print(f"Cloud Server: Received ClientHello, sending ServerHello")
            server_hello = TLSHandshakePacket(src=cloud_server_ip, dst=packet.src, handshake_step="ServerHello")
            client.receive_packet(server_hello)
        elif packet.handshake_step == "ServerHello":
            print(f"Cloud Server: TLS Handshake completed")

    def process_iot_data(self, packet):
        print(f"Cloud Server: Processing IoT data from {packet.src}")
        processed_data_packet = Packet(src=cloud_server_ip, dst=client_ip, payload=f"Processed {packet.payload}")
        client.receive_packet(processed_data_packet)

class Client:
    def send_packet(self, packet):
        print(f"Client: Sending {packet.summary()}")
        hub.forward(packet)

    def receive_packet(self, packet):
        print(f"Client: Received {packet.summary()}")
        if isinstance(packet, TLSHandshakePacket) and packet.handshake_step == "ServerHello":
            print("Client: Received ServerHello, TLS Handshake completed")
        elif packet.flags == 'SA':
            self.handle_syn_ack(packet)
        elif packet.payload.startswith("Processed"):
            print(f"Client: Received processed data from Cloud Server: {packet.payload}")

    def handle_syn_ack(self, packet):
        ack_packet = Packet(src=client_ip, dst=packet.src, seq=packet.ack, ack=packet.seq + 1, flags='A')
        print(f"Client: Sending ACK {ack_packet.summary()}")
        hub.forward(ack_packet)

    def start_tls_handshake(self):
        print("Client: Starting TLS Handshake with ClientHello")
        client_hello = TLSHandshakePacket(src=client_ip, dst=cloud_server_ip, handshake_step="ClientHello")
        hub.forward(client_hello)

    def send_keep_alive(self):
        print("Client: Sending keep-alive packet")
        keep_alive_packet = KeepAlivePacket(src=client_ip, dst=cloud_server_ip)
        hub.forward(keep_alive_packet)

# Initialize network devices
hub = Hub()
router = Router()
cloud_server = CloudServer()
client = Client()

def run_simulation(delay_min, delay_max, client_ip, cloud_server_ip):

    # Use delay_min and delay_max in the simulation loop for random delays
    delay = random.uniform(delay_min, delay_max)

    # Initialize IoT Devices
    iot_devices = [IoTDevice("IoT-Device-1", hub), IoTDevice("IoT-Device-2", hub)]

    for _ in range(5):  # Run the loop 5 times for testing
        # Simulate IoT devices sending data with random delays
        for iot_device in iot_devices:
            # Generate random data for simplicity
            data = f"Data from {iot_device.device_id} at {time.strftime('%H:%M:%S')}"
            print("\n--- IoT Device Sending Data ---")
            iot_device.send_data(data)

            # Introduce a random delay to simulate network/device latency
            delay = random.uniform(0.5, 2.0)  # Random delay between 0.5 and 2 seconds
            print(f"Delaying next action by {delay:.2f} seconds...")
            time.sleep(delay)

        # Optionally, simulate client-server interactions with delays
        # This could include TLS handshakes, keep-alive packets, etc.
            
def parse_arguments():
    parser = argparse.ArgumentParser(description="Network Simulation")
    parser.add_argument('--delay_min', type=float, default=0.5, help='Minimum delay in seconds')
    parser.add_argument('--delay_max', type=float, default=2.0, help='Maximum delay in seconds')
    parser.add_argument('--client_ip', type=str, default="192.168.1.2", help='IP address for the client')
    parser.add_argument('--cloud_server_ip', type=str, default="10.0.0.2", help='IP address for the cloud server')
    # Add more arguments as needed

    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_arguments()
    run_simulation(args.delay_min, args.delay_max, args.client_ip, args.cloud_server_ip)
