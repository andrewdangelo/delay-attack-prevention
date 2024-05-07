import socket,struct,typing
from ipaddress import IPv4Address
import socket, threading, logging, asyncio, argparse, time, os
import threading
from util import *
from TLSRecon import TLSType
from colorama import Fore, Style


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

class CustomLogger(logging.getLoggerClass()):
    def __init__(self, name, level=logging.NOTSET):
        super().__init__(name, level)

        logging.addLevelName(60, "RESET")

    def reset(self, message, *args, **kws):
        if self.isEnabledFor(60):
            self._log(60, Fore.RED + message + Style.RESET_ALL, args, **kws)


async def timer(duration, establish_session, addr, sock, sessions, logger):
    for i in range(duration, 0, -1):
        logger.reset(f"Timer: {i} seconds remaining")
        await asyncio.sleep(1)
    establish_session(addr, sock, sessions, logger)

def start_timer(duration, establish_session, addr, sock, sessions, logger):
    asyncio.run(timer(duration, establish_session, addr, sock, sessions, logger))


# This function finds the index of the most recent occurrence of a pattern in a given message data.
# It takes two parameters:
# - msgData: The message data in which the pattern is to be searched.
# - pattern: The pattern to be searched in the message data.
# It returns the index of the most recent occurrence of the pattern in the message data.
# If the pattern is not found, it returns -1.
def find_recent_pattern(msgData, pattern):
    idx_found = False
    i, j = 0, 0

    for variation in pattern:
        while i < len(msgData):
            if msgData[i] == variation[j]:  # Check if current character matches the pattern variation
                i += 1
                j += 1
            else:
                if j != 0:  # If pattern variation partially matches, reset j to 0
                    j = 0
                else:
                    i += 1  # If pattern variation doesn't match, move to the next character

            if j == len(variation):  # If pattern variation fully matches, set idx_found to True and reset j to 0
                idx_found = True
                j = 0

        if idx_found:
            return i-1  # Return the index of the most recent occurrence of the pattern variation
        else:
            i = 0  # Reset i to 0 for the next pattern variation

    return -1  # Return -1 if pattern is not found
    

def find_recent_pattern_without_variation(msgData, pattern):
    idx_found = False
    i, j = 0, 0

    while i < len(msgData):
        if msgData[i] == pattern[j]:  # Check if current character matches the pattern
            i += 1
            j += 1
        else:
            if j != 0:  # If pattern partially matches, reset j to 0
                j = 0
            else:
                i += 1  # If pattern doesn't match, move to the next character

        if j == len(pattern):  # If pattern fully matches, set idx_found to True and reset j to 0
            idx_found = True
            j = 0

    if idx_found:
        return i - len(pattern)  # Return the index of the most recent occurrence of the pattern
    else:
        return -1  # Return -1 if pattern is not found