import socket,struct,typing
from ipaddress import IPv4Address
import socket, asyncio
from util import *
from TLSRecon import TLSType
import json
from collections import Counter
import os




def original_addr(csock: socket.socket) -> typing.Tuple[str, int]:
    SO_ORIGINAL_DST = 80
    SOL_IPV6 = 41

    is_ipv4 = "." in csock.getsockname()[0]
    if is_ipv4:
        dst = csock.getsockopt(socket.SOL_IP, SO_ORIGINAL_DST, 16)
        port, raw_ip = struct.unpack_from("!2xH4s", dst)
        ip = socket.inet_ntop(socket.AF_INET, raw_ip)
    else:
        dst = csock.getsockopt(SOL_IPV6, SO_ORIGINAL_DST, 28)
        port, raw_ip = struct.unpack_from("!2xH4x16s", dst)
        ip = socket.inet_ntop(socket.AF_INET6, raw_ip)
    return ip, port

def isLocal(address):
    # gateway_ip, net_if = netifaces.gateways()['default'][netifaces.AF_INET]
    # addr_obj = netifaces.ifaddresses(net_if)[netifaces.AF_INET][0]
    if IPv4Address(address).is_private:
        return True
    else:
        return False

def longlive(addr,port):
    return True


def device_type(length):
    if (388 < length) and (393 > length):
        return 'third_reality'


async def timer(duration, establish_session, addr, sock, sessions, logger, data_manager):
    """
    A timer function that waits for a specified duration and then establishes a session.

    Args:
        duration (int): The duration in seconds to wait.
        establish_session (function): The function to call to establish a session.
        addr (str): The address to establish the session with.
        sock (socket): The socket to use for the session.
        sessions (list): The list of sessions.
        logger (Logger): The logger object to use for logging.

    Returns:
        None
    """
    for i in range(duration, 0, -1):
        logger.reset(f"Timer: {i} seconds remaining")
        await asyncio.sleep(1)
    establish_session(addr, sock, sessions, logger, data_manager)


def start_timer(duration, establish_session, addr, sock, sessions, logger, data_manager):
    """
    Starts a timer for the specified duration and runs the timer coroutine.

    Args:
        duration (float): The duration of the timer in seconds.
        establish_session (coroutine): The coroutine function to establish a session.
        addr (str): The address to establish the session with.
        sock (socket): The socket to use for the session.
        sessions (list): The list of active sessions.
        logger (Logger): The logger object for logging.

    Returns:
        None
    """
    asyncio.run(timer(duration, establish_session, addr, sock, sessions, logger, data_manager))



def find_recent_pattern(msgData, pattern):
    """
    Finds the most recent index in the given `msgData` where the `pattern` is fully matched.

    Args:
        msgData (list): The list of data to search for the pattern.
        pattern (list): The pattern to search for in the `msgData`.

    Returns:
        int: The most recent index where the pattern is fully matched. Returns -1 if no match is found.
    """

    most_recent_index = -1

    for variation in pattern:
        i, j = 0, 0
        while i < len(msgData):
            if msgData[i] == variation[j]:  # Check if current data matches the pattern variation
                j += 1
                if j == len(variation):  # If pattern variation fully matches
                    current_end_index = i
                    most_recent_index = max(most_recent_index, current_end_index)  # Update the most recent index
                    j = 0  # Reset j for further searching
            else:
                i -= j  # Reset i to start of the last match attempt plus one
                j = 0   # Reset j to start of variation
            i += 1

    return most_recent_index
    

def read_json_file(file_path):
    """
    Read and parse a JSON file.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        dict: The parsed JSON data.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        json.JSONDecodeError: If the file contains invalid JSON.

    """
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data



def find_repeating_pattern(data):
    """
    Finds the most common repeating pattern in the given data.

    Args:
        data (list): The input data to search for repeating patterns.

    Returns:
        tuple: A tuple containing the most common repeating pattern found and its certainty.

    Example:
        >>> data = [1, 2, 3, 1, 2, 3, 1, 2, 3, 4, 5, 6]
        >>> find_repeating_pattern(data)
        ([1, 2, 3], 0.3)
    """
    if not data:
        return None, 0

    # Minimum size of the repeating pattern we expect to find
    min_pattern_length = 2
    max_pattern_length = len(data) // 2

    # This dictionary will hold patterns and their frequencies
    pattern_counts = Counter()

    # Test various lengths of patterns
    for pattern_length in range(min_pattern_length, max_pattern_length + 1):
        # Slide over the data to extract patterns of the current length
        for start in range(len(data) - pattern_length + 1):
            # Extract the pattern and update the count in the dictionary
            pattern = tuple(data[start:start + pattern_length])
            pattern_counts[pattern] += 1

    # Find the pattern with the maximum frequency
    if not pattern_counts:
        return None, 0

    most_common_pattern, frequency = pattern_counts.most_common(1)[0]

    # Calculate the certainty as the number of times the pattern appears divided by the possible times it could
    total_occurrences = sum(pattern_counts.values())
    certainty = frequency / total_occurrences

    return list(most_common_pattern), certainty

def update_session_data(address, msg_lengths, timestamps):
    session_file = 'session_save.json'
    
    # Load existing data if file exists
    if os.path.exists(session_file):
        with open(session_file, 'r') as file:
            try:
                # Assuming the file contains a JSON object
                data = json.load(file)
            except json.JSONDecodeError:
                data = {}
    else:
        data = {}

    # Update or add new data
    if address[0] in data:
        # Append to existing lists if the key exists
        data[address[0]][0].extend(msg_lengths)
        data[address[0]][1].extend(timestamps)
    else:
        # Create a new entry if the key does not exist
        data[address[0]] = [msg_lengths, timestamps]

    # Write the updated data back to the file
    with open(session_file, 'w') as file:
        json.dump(data, file, indent=4)