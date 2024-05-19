import socket
import threading
import logging
import argparse
import time
import os
from queue import Queue
import sys
from util import *
from TLSRecon import TLSType
import csv
from colorama import Fore, Style
import json
from util import find_recent_pattern, start_timer, read_json_file
from datetime import datetime
import pytz
from dataManager import DataManager
from commands import CommandListener

class Session(threading.Thread):
    def __init__(self, s_sock, s_addr, d_sock, d_addr, logger, data_manager):
        super().__init__()
        self.s_sock = s_sock
        self.s_addr = s_addr
        self.d_sock = d_sock
        self.d_addr = d_addr
        self.logger = logger
        self.data_manager = data_manager
        self.termination = Queue()

    def run(self):
        self.logger.info('new session with %s is established' % (str(self.s_addr)))
        t_dr = threading.Thread(target=self.receive, args=(self.s_sock, self.d_sock))
        t_sr = threading.Thread(target=self.receive, args=(self.d_sock, self.s_sock))
        t_dw = threading.Thread(target=self.send, args=(self.s_sock, self.d_sock))
        t_sw = threading.Thread(target=self.send, args=(self.d_sock, self.s_sock))
        
        t_dr.start()
        t_sr.start()
        t_dw.start()
        t_sw.start()
        
        t_dr.join()
        t_sr.join()
        t_dw.join()
        t_sw.join()
        
        self.logger.info('session with %s has been terminated' % (str(self.s_addr)))

    def receive(self, src_sock, dst_sock):
        try:
            while not self.termination.get():
                data = src_sock.recv(4096)
                if data:
                    dst_sock.send(data)
                else:
                    break
        except Exception as e:
            self.logger.error("Receive error: %s" % str(e))
            self.termination.put(True)

    def send(self, src_sock, dst_sock):
        try:
            while not self.termination.get():
                data = src_sock.recv(4096)
                if data:
                    dst_sock.send(data)
                else:
                    break
        except Exception as e:
            self.logger.error("Send error: %s" % str(e))
            self.termination.put(True)

    def in_range(self, time_range, lengths):
        for length in lengths:
            if (length >= time_range[0]) and (length <= time_range[1]):
                return True
        return False

    def analyze_hk(self, msg, dst):
        if dst == "server":
            address = self.s_addr
            other_address = self.d_addr
        else:
            address = self.d_addr
            other_address = self.s_addr
        
        logger.info("%d bytes to %s from %s" % (len(msg), address, other_address))

        self.timestamps.append(time.time())
        self.msg_lengths.append(len(msg))

        self.data_manager.set_msg_data(self.d_addr[0], len(msg))
        self.data_manager.set_timestamp_data(self.d_addr[0], time.time())

        with open('./flag.txt', 'rt+') as flag:
            instruct = flag.read()
            if instruct:
                flag.seek(0)
                flag.truncate()
                delay = float(instruct)
                if dst == "server":
                    self.dst_server_delays.put(delay)
                else:
                    self.src_client_delays.put(delay)

def check_reset_info():
    while True:
        try:
            with open('reset_info.txt', 'rt+') as file:
                reset_info = file.readline().strip().split()
                # Process reset info here
            time.sleep(1)  # Add a small delay to prevent busy waiting
        except Exception as e:
            print("Error reading reset_info.txt: %s" % str(e))

def non_blocking_input(prompt, input_queue):
    print(prompt, end='', flush=True)
    input_queue.put(sys.stdin.readline().strip())

def main():
    parser = argparse.ArgumentParser(description='TLS Recon')
    parser.add_argument('--port', type=int, default=10000, help='Port to listen on')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    args = parser.parse_args()

    logger = logging.getLogger('tls_recon')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler = logging.FileHandler('tls_analysis.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    if args.verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    data_manager = DataManager()
    input_queue = Queue()
    command_listener = CommandListener(data_manager, logger, input_queue)
    command_listener.start()

    reset_info_thread = threading.Thread(target=check_reset_info, daemon=True)
    reset_info_thread.start()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listen_sock:
        listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listen_sock.bind(('0.0.0.0', args.port))
        listen_sock.listen()

        logger.info("start listening at port %d" % (args.port))

        while True:
            try:
                d_sock, d_addr = listen_sock.accept()
                session_thread = Session(listen_sock, ('0.0.0.0', args.port), d_sock, d_addr, logger, data_manager)
                session_thread.start()
                # Ensure the input prompt is not blocking
                threading.Thread(target=non_blocking_input, args=("Enter command: ", input_queue)).start()
            except KeyboardInterrupt:
                break

if __name__ == "__main__":
    main()
