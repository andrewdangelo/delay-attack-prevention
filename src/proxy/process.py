import socket, threading, logging, asyncio, argparse, time, os
import threading
from queue import Empty
from threading import Thread
from queue import Queue
import sys
from util import *
from TLSRecon import TLSType
import csv

class Session(threading.Thread):
    """
    Represents a session between a client and a server.

    Attributes:
    - d_addr: The address of the destination server.
    - d_sock: The socket connected to the destination server.
    - logger: The logger object for logging session events.
    - termination: A queue used to signal termination of the session.
    - server_q: A queue for sending data from the server to the client.
    - device_q: A queue for sending data from the client to the server.
    - s_addr: The address of the source client.
    - s_sock: The socket connected to the source client.
    """

    def __init__(self, d_addr, d_sock, logger):
        """
        Initializes a new Session object.

        Parameters:
        - d_addr: The address of the destination server.
        - d_sock: The socket connected to the destination server.
        - logger: The logger object for logging session events.
        """
        threading.Thread.__init__(self)
        self.d_sock = d_sock
        self.d_addr = d_addr
        self.termination = Queue()
        self.server_q = Queue()
        self.device_q = Queue()
        self.s_addr = original_addr(d_sock)
        self.logger = logger

    def run(self):
        """
        Starts the session by creating and starting the necessary threads.
        """
        self.s_sock = self.connect_server(self.s_addr)
        t_dr = Thread(target=self.device_read, name='device read')
        t_dw = Thread(target=self.device_write, name='device write')
        t_sr = Thread(target=self.server_read, name='server read')
        t_sw = Thread(target=self.server_write, name='server write')
        t_dr.start()
        t_sr.start()
        t_dw.start()
        t_sw.start()
        self.logger.info('new session with %s is established'%(str(self.s_addr)))
        if self.termination.get():
            self.s_sock.close()
            self.d_sock.close()
            self.logger.info('session with %s is getting terminated'%(str(self.s_addr)))
        t_dr.join()
        t_sr.join()
        t_dw.join()
        t_sw.join()
        self.logger.info('session with %s has been terminated'%(str(self.s_addr)))

    def in_range(self, time_range, lengths):
        """
        Checks if any of the lengths fall within the specified time range.

        Parameters:
        - time_range: A tuple representing the minimum and maximum time range.
        - lengths: A list of lengths to check.

        Returns:
        - True if any of the lengths fall within the time range, False otherwise.
        """
        for length in lengths:
            if (length >= time_range[0]) and (length <= time_range[1]):
                return True
        return False
    
    def analyze_hk(self, msg, dst):
        """
        Analyzes the message and performs actions based on the destination.

        Parameters:
        - msg: The message to analyze.
        - dst: The destination of the message.

        Actions:
        - Logs the number of bytes in the message.
        - Reads instructions from a file named 'flag.txt'.
        - Adds delay to the appropriate queue based on the instructions.
        - Clears the instructions from the file.
        """
        if dst == "server":
            address = self.s_addr
            other_address = self.d_addr
        else:
            address = self.d_addr
            other_address =  self.s_addr
        logger.info("%d bytes to %s from %s"%(len(msg),address, other_address))
        with open('./flag.txt','rt+') as flag:
                instruct = flag.read()
                length = len(msg)
                if len(instruct) > 0:
                    length_range = instruct.split(' ')[0]
                    delay = int(instruct.split(' ')[1])
                    minimal = int(length_range.split(',')[0])
                    maximal = int(length_range.split(',')[1]) 
                    if (length >= minimal) and (length <= maximal):
                        if dst == "server":
                            self.device_q.put(delay)
                        else:
                            self.server_q.put(delay)
                        flag.truncate(0)
                        flag.flush()
                        

    def analyze(self, msg, dst):
        """
        Analyzes the message and performs actions based on the destination.

        Parameters:
        - msg: The message to analyze.
        - dst: The destination of the message.

        Actions:
        - Logs the lengths of the records being sent to the address.
        - Writes the lengths of the records to a CSV file.
        - Reads instructions from a file named 'flag.txt'.
        - Adds delay to the appropriate queue based on the instructions.
        - Clears the instructions from the file.
        """
        if dst == "server":
            address = self.s_addr
        else:
            address = self.d_addr
        
        records_sig = TLSType(msg)
        type_list = [x[0] for x in records_sig]
        
        if ('application_data' in type_list):
            lengths = [x[1] for x in records_sig]
            
            logger.info("record of %s bytes to %s" % (str(lengths), address))

            self.write_to_csv(self.s_addr if dst == "server" else self.d_addr, self.d_addr if dst == "server" else self.s_addr, str(lengths))
            
            with open('./flag.txt', 'rt+') as flag:
                instruct = flag.read()
                if len(instruct) > 0:
                    ip_address, rest = instruct.split(';')
                    length_range, delay = rest.split(' ')[0:2]

                    minimal, maximal = map(int, length_range.split(','))
                    
                    if self.in_range((minimal, maximal), lengths):
                        if dst == "server" and ip_address:
                            self.device_q.put(int(delay))
                        else:
                            self.server_q.put(int(delay))
                            
                        flag.truncate(0)
                        flag.flush()

    def device_read(self):
        """
        Reads data from the device socket and performs analysis.
        """
        while True:
            try:
                msg_f_d = self.d_sock.recv(8192)
            except:
                self.termination.put(True)
                self.device_q.put('')
                break
            if len(msg_f_d) > 0:
                self.analyze_hk(msg_f_d,"server")
                self.device_q.put(msg_f_d)
            else:
                self.termination.put(True)
                self.device_q.put('')
                break

        
    def device_write(self):
        """
        Writes data from the device queue to the server socket.
        """
        while True:
            msg_t_d = self.server_q.get()
            if type(msg_t_d) == int:
                    self.logger.info("---------------delay starts for %s seconds---------------"%(str(msg_t_d)))
                    time.sleep(msg_t_d)
                    self.logger.info("---------------delay ends for %s seconds---------------"%(str(msg_t_d)))
                    continue
            if len(msg_t_d) > 0:
                try:
                    self.d_sock.send(msg_t_d)
                except:
                    self.termination.put(True)
                    break
            else:
                break

    def server_read(self):
        """
        Reads data from the server socket and performs analysis.
        """
        while True:
            try:
                msg_f_s = self.s_sock.recv(8192)
            except:
                self.termination.put(True)
                self.server_q.put('')
                break
            if len(msg_f_s):
                self.analyze_hk(msg_f_s,"device")
                self.server_q.put(msg_f_s)
            else:
                self.termination.put(True)
                self.server_q.put('')
                break
        
    def server_write(self):
        """
        Writes data from the server queue to the device socket.
        """
        while True:
            msg_t_s = self.device_q.get()
            if type(msg_t_s) == int:
                    self.logger.info("---------------delay starts for %s seconds---------------"%(str(msg_t_s)))
                    time.sleep(msg_t_s)
                    self.logger.info("---------------delay ends for %s seconds---------------"%(str(msg_t_s)))
                    continue
            if len(msg_t_s) > 0:
                try:
                    self.s_sock.send(msg_t_s)
                except:
                    self.termination.put(True)
                    break
            else:
                break

    def connect_server(self, s_addr):
        """
        Connects to the server using the given address.

        Parameters:
        - s_addr: The address of the server.

        Returns:
        - The socket connected to the server, or False if connection fails.
        """
        s_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s_sock.connect(s_addr)
            return s_sock
        except Exception as e:
            self.logger.error(e)
            return False
        
    def write_to_csv(self, src_ip, dst_ip, byte_size):
        """
        Writes traffic data to a CSV file.

        Parameters:
        - src_ip: The source IP address.
        - dst_ip: The destination IP address.
        - byte_size: The size of the data in bytes.
        """
        fieldnames = ['Date', 'Time', 'Src IP', 'Dst IP', 'Byte Size']
        file_exists = os.path.isfile('traffic_data.csv')
        with open('traffic_data.csv', 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            now = time.localtime()
            writer.writerow({
                'Date': time.strftime('%Y-%m-%d', now),
                'Time': time.strftime('%H:%M:%S', now),
                'DST IP': src_ip,
                'SRC IP': dst_ip,
                'Byte Size': byte_size
            })

    def resetConnection(self, ):
        """
        Resets the connection to the destination server.
        """
        self.logger.info(f"Initiating connection reset for {self.d_addr}")
        try:
            self.termination.put(True)  # Signal termination to the session threads
            self.logger.info(f"Connection to {self.d_addr} has been closed.")
            self.s_sock.close()  # Close the existing socket connection
            self.d_sock.close()
            self.logger.info(f"Connection to {self.d_addr} successfully re-established.")
        except Exception as e:
            self.logger.error(f"Failed to reset connection: {e}")

def cli_interface(session_threads):
    """
    Provides a command-line interface for managing session threads.

    Parameters:
    - session_threads: A list of session threads.

    Actions:
    - Resets a connection based on user input.

    Returns:
    - The IP address and duration specified in the command.
    """
    print("CLI interface is now active. Waiting for commands...")
    while True:
        cmd = input("Enter command (e.g., reset <ipaddress> -d <duration>): ")
        print(f"Command received: {cmd}")
        if cmd.startswith("reset "):
            cmd_parts = cmd.split(" ")
            ip = cmd_parts[1]
            duration = 30
            if "-d" in cmd_parts:
                duration_index = cmd_parts.index("-d")
                if duration_index + 1 < len(cmd_parts):
                    duration = int(cmd_parts[duration_index + 1])
            found = False
            print(f"Looking for session with IP: {ip}")
            for session in session_threads:
                print(f"Checking session with device IP: {session.d_addr}")
                if session.d_addr[0] == ip:
                    print(f"Initiating reset for session with IP {ip} and duration {duration} seconds")
                    threading.Thread(target=session.resetConnection, args=(duration,)).start()
                    found = True
                    # session.termination.put(True)
            
            if not found:
                print(f"No active session with IP {ip} found.")
            
            return ip, duration




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Transparent proxy for TLS sessions')
    parser.add_argument('-v', '--verbose', action='store_true', default=False)
    parser.add_argument('-p', '--port',type=int, default=10000, metavar='P',help= 'port to listen')
    args = parser.parse_args()

    session_threads = []
    # Starting the CLI in a separate thread
    cli_thread = threading.Thread(target=cli_interface, args=(session_threads,), daemon=True)
    cli_thread.start()

    logger = logging.getLogger('TLSLogger')
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

    # StreamHandler for console output
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # FileHandler for file output
    file_handler = logging.FileHandler('tls_analysis.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Set the log level
    logger.setLevel(logging.INFO)

    if args.verbose: 
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listen_sock:
        listen_sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        listen_sock.bind(('0.0.0.0',args.port))
        listen_sock.listen()

        logger.info("start listening at port %d"%(args.port))

        while True:
            try:
                # Wait for the CLI thread to finish and get the return values
                cli_thread.join()
                ip_address, duration = cli_thread.result()

                # Listens for an incoming socket connection on port 10000.
                d_sock, d_addr = listen_sock.accept()

                #Need conditional verification to check the s_addr.
                #Need to initiate an async timer instead of sleep.
                #Check timer and address 

                #Wrap the session statements in an else statement
                #Establishes a new socket connection with the d_sock and d_addr
                session_thread = Session(d_addr,d_sock,logger)
                print("Start new: " + d_addr[0])
                session_threads.append(session_thread)
                session_thread.start()
                
            except KeyboardInterrupt:
                for session in session_threads:
                    session.termination.put(True)
                listen_sock.close()
                del listen_sock
                sys.exit()

#1. When we 
