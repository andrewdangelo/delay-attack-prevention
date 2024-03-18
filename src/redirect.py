import netifaces
from pick import pick
import subprocess


def list_interfaces():
    iface, index = pick(netifaces.interfaces(), 'Please choose the wireless interface used for hotspot')
    return iface

def clean_nftables():
    subprocess.run([ "nft", "flush", "table", "ip", "nat"])
    subprocess.run([ "nft", "delete", "table", "ip", "nat"])
    subprocess.run([ "nft", "flush", "table", "ip", "filter"])
    subprocess.run([ "nft", "delete", "table", "ip", "filter"])
    print("Ran nftables....")
    

if __name__ == "__main__":
    #interfaces = list_interfaces()
    clean_nftables()
    #print(interfaces)