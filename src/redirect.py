import netifaces
from pick import pick
import time
import subprocess,argparse,netifaces,configparser,iptc,os


def list_interfaces():
    iface, index = pick(netifaces.interfaces(), 'Please choose the wireless interface used for hotspot')
    return iface

def clean_iptables():
    os.system("sudo sysctl -w net.ipv4.ip_forward=1")
    os.system("sysctl -w net.ipv4.conf.all.send_redirects=1")
    existing_nat = iptc.easy.dump_chain('nat','PREROUTING')
    existing_filter = iptc.easy.dump_chain('filter','FORWARD')
    for rule in existing_nat:
        iptc.easy.delete_rule('nat','PREROUTING',rule)
    for rule in existing_filter:
        iptc.easy.delete_rule('filter','FORWARD',rule)

if __name__ == "__main__":
    interfaces = list_interfaces()
    clean_iptables
    print(interfaces)