import netifaces
from pick import pick
import time

def list_interfaces():
    iface, index = pick(netifaces.interfaces(), 'Please choose the wireless interface used for hotspot')
    return iface

if __name__ == "__main__":
    interfaces = list_interfaces()
    print(interfaces)