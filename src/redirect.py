import netifaces
from pick import pick
import subprocess
import json


def get_devices(file_path):
    # Open and read the JSON file
    with open(file_path, 'r') as file:
        devices = json.load(file)

    # Initialize an empty list to hold the device dictionaries
    device_list = []

    # Iterate over each device in the list
    for device in devices:
        # Create a dictionary for the current device
        device_dict = {
            'name': device['name'],
            'interface': device['interface'],
            'ip_address': device['ip address'], # Make sure this matches the key in your JSON
            'port': device['port']
        }
        # Append the dictionary to the list of devices
        device_list.append(device_dict)
    
    # Return the list of device dictionaries
    return device_list

def list_nftables_rules():
    result = subprocess.run(["nft", "list", "ruleset"], capture_output=True, text=True)
    if result.returncode == 0:
        print(result.stdout)
    else:
        print("Error listing nftables rules:", result.stderr)

def get_chain_rules(rule):
    # Command to list the rules in the designated rule chain of the inet fw4 table
    command = ["nft", "list", "chain", "inet", "fw4", rule]
    
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

def setup_tables(devices):
    with open('added_rules.txt', 'w') as file:
        for device in devices:
            print(device)
            """ addr = device['ip_address']
            port = device['port']
            
            # Construct nftables redirect and drop rules
            rules = [
                (f"prerouting", f"ip protocol tcp ip saddr {addr} tcp dport 0-65535 redirect to :{port}"),
                (f"prerouting", f"ip protocol tcp ip daddr {addr} tcp dport 0-65535 redirect to :{port}"),
                (f"forward", f"ip protocol tcp ip saddr {addr} tcp dport 0-65535 drop"),
                (f"forward", f"ip protocol tcp ip daddr {addr} tcp dport 0-65535 drop")
            ]

            # Insert rules into the 'prerouting' and 'forward' chains of the 'inet fw4' table and save to file
            for chain, rule in rules:
                command = f"nft add rule inet fw4 {chain} {rule}"
                try:
                    subprocess.run(command, check=True, shell=True)
                    print(f"Successfully inserted rule: {command}")
                    # Save the chain and rule to the file
                    file.write(f"{chain}|{rule}\n")
                except subprocess.CalledProcessError as e:
                    print(f"Failed to insert rule: {command}\nError: {e}") """

def cleanup_tables():
    with open('added_rules.txt', 'r') as file:
        lines = file.readlines()
    
    # Execute the delete command for each rule
    for line in lines:
        chain, rule = line.strip().split('|')
        delete_command = f"nft delete rule inet fw4 {chain} {rule}"
        try:
            subprocess.run(delete_command, check=True, shell=True)
            print(f"Successfully deleted rule: {delete_command}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to delete rule: {delete_command}\nError: {e}")
    
    # Clear the file after deleting the rules
    open('added_rules.txt', 'w').close()


if __name__ == "__main__":
    rules = get_chain_rules("PREROUTING")
    print(rules)
    print('---------------------------------------------')
    print('Getting devices and inserting rules....')
    
    devices = get_devices('devices.json')
    setup_tables(devices)
    print('---------------------------------------------')

    print('***UPDATED RULES***')
    inserted_rules = get_chain_rules("PREROUTING")
    print(inserted_rules)
