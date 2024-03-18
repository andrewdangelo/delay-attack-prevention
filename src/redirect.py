import netifaces
from pick import pick
import subprocess


def list_interfaces():
    iface, index = pick(netifaces.interfaces(), 'Please choose the wireless interface used for hotspot')
    return iface

""" def clean_nftables():
    subprocess.run([ "nft", "flush", "table", "ip", "nat"])
    subprocess.run([ "nft", "delete", "table", "ip", "nat"])
    subprocess.run([ "nft", "flush", "table", "ip", "filter"])
    subprocess.run([ "nft", "delete", "table", "ip", "filter"])
    print("Ran nftables....") """

def list_nftables_rules():
    result = subprocess.run(["nft", "list", "ruleset"], capture_output=True, text=True)
    if result.returncode == 0:
        print(result.stdout)
    else:
        print("Error listing nftables rules:", result.stderr)

list_nftables_rules()
    

if __name__ == "__main__":
    #interfaces = list_interfaces()
    list_nftables_rules()
    #print(interfaces)