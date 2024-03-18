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

def get_forward_chain_rules():
    # Command to list the rules in the forward chain of the inet fw4 table
    command = ["nft", "list", "chain", "inet", "fw4", "forward"]
    
    # Execute the command and capture the output
    result = subprocess.run(command, capture_output=True, text=True)
    
    # Check if the command was executed successfully
    if result.returncode == 0:
        # Split the output into lines
        lines = result.stdout.split('\n')
        
        # Filter out lines that don't start with a rule indicator, like a tab or specific keywords
        rules = [line.strip() for line in lines if line.strip().startswith("iifname") or line.strip().startswith("jump")]
        
        return rules
    else:
        print("Error executing nft command:", result.stderr)
        return []

# Fetch the rules
    

if __name__ == "__main__":
    #interfaces = list_interfaces()
    """ list_nftables_rules() """
    forward_chain_rules = get_forward_chain_rules()

    # Print each rule
    for rule in forward_chain_rules:
        print(rule)
    #print(interfaces)