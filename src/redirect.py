import netifaces,iptc,os
from pick import pick
import subprocess
import json


def get_devices(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        # Adjust here to match your JSON structure
        devices = data['devices']  # Adjusted to access the nested list

    device_list = []
    for device in devices:
        device_dict = {
            'name': device['name'],
            'ip_address': device['ip_address'],  # Ensure this matches your JSON keys
            'port': device['port']
        }
        device_list.append(device_dict)

    return device_list


""" def setup_tables(devices):
    os.system("sudo sysctl -w net.ipv4.ip_forward=1")
    os.system("sysctl -w net.ipv4.conf.all.send_redirects=0")

    # ERROR IN SYSTEM LOGIC: ONLY PRINTING FIRST DEVICE
    #Might need to get rid of the use of iptc because it goes to iptables-lagacy
    for device in devices:
        print(device)
        addr = device['ip_address']
        port = device['port']
        
        existing_nat = iptc.easy.dump_chain('nat','PREROUTING')
        existing_filter = iptc.easy.dump_chain('filter','FORWARD')

        if existing_nat and existing_filter:
            for rule in existing_nat:
                iptc.easy.delete_rule('nat','PREROUTING',rule)
            for rule in existing_filter:
                iptc.easy.delete_rule('filter','FORWARD',rule)

        redirect_rules = [
        {
            'src':addr,'protocol':'tcp','multiport':{'dports': '0:65535'}, 'target': {'REDIRECT': {'to-ports': str(port)}}
        },
        # {
        #     'src':addr1,'protocol':'tcp','multiport':{'dports': '0:65535'}, 'target': {'REDIRECT': {'to-ports': str(port)}}
        # },
        {
            'dst':addr,'protocol':'tcp','multiport':{'dports': '0:65535'}, 'target': {'REDIRECT': {'to-ports': str(port)}}
        }
        # ,{
        #     'dst':addr1,'protocol':'tcp','multiport':{'dports': '0:65535'}, 'target': {'REDIRECT': {'to-ports': str(port)}}
        # }
        ]
        
        drop_rules = [
            {'src': addr, 'protocol':'tcp','multiport':{'dports': '0:65535'},'target': 'DROP'},
            {'dst': addr, 'protocol':'tcp','multiport':{'dports': '0:65535'},'target': 'DROP'}
        ]

        for rule in drop_rules:
            iptc.easy.insert_rule('filter','FORWARD',rule)
        for rule in redirect_rules:
            iptc.easy.insert_rule('nat','PREROUTING',rule) """

def run_iptables_command(command, rule_file=None):
    try:
        result = subprocess.run(command, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(result.stdout)
        # Save the command to a file for later cleanup if specified
        if rule_file:
            with open(rule_file, 'a') as file:
                file.write(command + '\n')
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}\n{e}")

def setup_tables(devices, rule_file='added_rules.txt'):
    # Clear the file to start fresh
    open(rule_file, 'w').close()

    # Enable IP forwarding
    run_iptables_command("sudo sysctl -w net.ipv4.ip_forward=1")
    run_iptables_command("sudo sysctl -w net.ipv4.conf.all.send_redirects=0")

    for device in devices:
        print(device)
        addr = device['ip_address']
        port = device['port']

        # Redirect rules
        redirect_command = f"sudo iptables -t nat -A PREROUTING -p tcp -d {addr} -j REDIRECT --to-port {port}"
        run_iptables_command(redirect_command, rule_file)
        redirect_command = f"sudo iptables -t nat -A PREROUTING -p tcp -s {addr} -j REDIRECT --to-port {port}"
        run_iptables_command(redirect_command, rule_file)

        # Drop rules
        drop_command = f"sudo iptables -t filter -A FORWARD -p tcp -d {addr} -j DROP"
        run_iptables_command(drop_command, rule_file)
        drop_command = f"sudo iptables -t filter -A FORWARD -p tcp -s {addr} -j DROP"
        run_iptables_command(drop_command, rule_file)

def cleanup_rules(rule_file='added_rules.txt'):
    with open(rule_file, 'r') as file:
        rules = file.readlines()

    for rule in rules:
        # Replace '-A' (append) with '-D' (delete) to construct the delete command
        delete_command = rule.replace('-A', '-D').strip()
        run_iptables_command(delete_command)

    # Optionally, clear the file after cleanup
    open(rule_file, 'w').close()

# Old function to clean up nftables
def cleanup_nftables():
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

def get_chain_rules(table_name, chain_name):
    """
    Prints out the rules for a specified chain in the specified table using the iptc library.
    
    :param table_name: The name of the table (e.g., 'nat', 'filter')
    :param chain_name: The name of the chain (e.g., 'PREROUTING', 'FORWARD')
    """
    table = iptc.Table(table_name)
    chain = iptc.Chain(table, chain_name)
    print(f"Rules in {chain_name} chain of the {table_name} table:")
    for rule in chain.rules:
        print(f"Rule: {rule.src} -> {rule.dst} {rule.protocol} {rule.target.name}")
        for match in rule.matches:
            print(f" Match: {match.name}")



if __name__ == "__main__":
    print('---------------------------------------------')
    print('Getting devices and inserting rules....')
    
    devices = get_devices('devices.json')
    setup_tables(devices)
    print('---------------------------------------------')

    print('***UPDATED RULES***')
    get_chain_rules('nat', 'PREROUTING')
    get_chain_rules('filter', 'FORWARD')
