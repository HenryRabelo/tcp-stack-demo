import socket
import pickle
import time

class Layer:

    def __init__(self):
        self.PDU = None
        
        
    def encapsulate(self, data, header):
        packet = []
        packet.append("{} Header".format(header))
        packet.append(data)
        
        if header == 'Frame':
            packet.append("{} Footer".format(header))
        
        return packet


class Client:

    def __init__(self, host, port):
        # Initial server variables
        self.HOST = host
        self.PORT = port
        self.MAX_TRANSFER_SIZE = 1024
        
        # Variables for later use
        self.COMMAND = None
        self.CONNECTION = None
        self.MESSAGE = None
    
    
    def setup(self):
        # Create a connection to the server application on port
        self.CONNECTION = socket.create_connection((self.HOST, self.PORT))
    
    
    def await_command(self):
        self.COMMAND = input("client@{}~> ".format(self.HOST))
    
    
    def help(self):
        print("\nOPTIONS")
        print("     help                See the manual.")
        print("     ping                Receive the server IP.")
        print("     handshake           Simulate a TCP handshake.")
        print("     stack               Simulate the TCP/IP encapsulation process.")
        print("     [ text ]            Send message to server.")
        print("     exit, [ empty ]     Quit the program.")
        print("")
        
        
    def ping(self):
        self.CONNECTION.sendall(self.COMMAND.encode())
        received = self.CONNECTION.recv(self.MAX_TRANSFER_SIZE).decode()
        print("{}\n".format(received))
        
        
    def handshake(self):
        self.CONNECTION.sendall('SYN'.encode())
        print("'SYN' sent.")
        
        received1 = self.CONNECTION.recv(self.MAX_TRANSFER_SIZE).decode()
        received2 = self.CONNECTION.recv(self.MAX_TRANSFER_SIZE).decode()
        
        if received1 == 'SYN' and received2 == 'ACK':
            print("{} received.".format(received1))
            print("{} received.".format(received2))
            
            self.CONNECTION.sendall('ACK'.encode())
            print("'ACK' sent.\n")
        else:
            print("Error during Three Way Handshake.")
        
        
    def stack(self):
        message = input("Write your message: ")
        
        application = Layer()
        application.PDU = [message]
        data = application.PDU
        print("\nApplication Layer - Created Data:")
        print("{}\n".format(data))
        
        transport = Layer()
        transport.PDU = transport.encapsulate(data, 'TCP')
        segment = transport.PDU
        print("Transport Layer - Created Segment:")
        print("{}\n".format(segment))
        
        print("Establishing connection through a Three-Way Handshake...")
        self.handshake()
        
        network = Layer()
        network.PDU = network.encapsulate(segment, 'IP')
        packet = network.PDU
        print("Network Layer - Created Packet:")
        print("{}\n".format(packet))
        
        netInterface = Layer()
        netInterface.PDU = netInterface.encapsulate(packet, 'Frame')
        frame = netInterface.PDU
        print("Network Interface Layer - Created Frame (Frame Footer implied):")
        print("{}\n".format(frame))
        
        self.CONNECTION.sendall(pickle.dumps(frame))
        print("Frame sent.\n")
        
        
    def send_msg(self):
        self.CONNECTION.sendall(self.COMMAND.encode())
    
    
    def close_socket(self):
        try:
            print("Closing socket...")
            self.CONNECTION.close()
            self.CONNECTION = None
        except (OSError, socket.error):
            print("Already closed.\n")


def main():
    host = "localhost"
    port = 3333
    client = Client(host, port)
    client.setup()
    
    print("Type 'help' to see the manual.\n")
    
    try:
        while True:
        
            try:
                client.await_command()
        
                if not client.COMMAND:
                    break
        
                if client.COMMAND == "help":
                    client.help()
        
                elif client.COMMAND == "ping":
                    client.ping()
        
                elif client.COMMAND == "handshake":
                    client.handshake()
                    
                elif client.COMMAND == "stack":
                    client.stack()
                
                elif client.COMMAND == "exit":
                    break
                
                else:
                    client.send_msg()
            except (socket.error, BrokenPipeError, ConnectionResetError):
                print("Error connecting to server. Attempting to reconnect...\n")
                max_retries = 5
                delay = 1
                
                client.close_socket()
                
                for i in range(max_retries):
                    client.setup()
                    if client.CONNECTION is not None:
                        break
                    else:
                        time.sleep(delay)
                
                if client.CONNECTION is None:
                    print("Reconnection timeout.\n")
                    break
                else:
                    print("Reconnection successful.\n")
                
    except (KeyboardInterrupt):
        print("\nProgram interrupted by user.\n")
    except (Exception):
        print("Unexpected error during main runtime.\n")
    
    finally:
        client.close_socket()
        print("Quitting the program...")


if __name__ == "__main__":
    main()

