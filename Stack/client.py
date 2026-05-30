import socket
import json

class Layer:

    def __init__(self):
        # Initial Layer variables
        self.PDU = None
        
        
    def encapsulate(self, data, header):
        packet = []
        
        if header is not None:
            packet.append("{} Header".format(header))
            
        packet.append(data)
        
        if header == 'Frame':
            packet.append("{} Footer".format(header))
        
        return packet


class Client:

    def __init__(self, host, port):
        # Initial Client variables
        self.HOST = host
        self.PORT = port
        self.MAX_TRANSFER_SIZE = 1024
        
        # Variables for later use
        self.COMMAND = None
        self.CONNECTION = None
        self.MESSAGE = None
    
    
    def setup(self):
        # Create a connection to the server program on defined address and port
        self.CONNECTION = socket.create_connection((self.HOST, self.PORT))
    
    
    def await_command(self):
        self.COMMAND = input("client@{}~> ".format(self.HOST))
    
    
    def await_response(self):
        try:
            # Receive and print data a few bytes at a time, as long as the client is sending something
            received = self.CONNECTION.recv(self.MAX_TRANSFER_SIZE)
            
            # Try to decode received message
            self.MESSAGE = json.loads(received.decode())
        except (json.JSONDecodeError, AttributeError):
            print("Data not in a valid JSON format or connection error.\n")
            self.CONNECTION.close()
    
    
    def ping(self):
        self.send_msg(self.COMMAND)
        self.await_response()
        print("{}\n".format(self.MESSAGE))
    
    
    def handshake(self):
        self.send_msg('SYN')
        print("'SYN' sent.")
        
        self.await_response()
        received1 = self.MESSAGE
        
        self.await_response()
        received2 = self.MESSAGE
        
        if received1 == 'SYN' and received2 == 'ACK':
            print("{} received.".format(received1))
            print("{} received.".format(received2))
            
            self.send_msg('ACK')
            print("'ACK' sent.\n")
        else:
            print("Error during Three Way Handshake.")
    
    
    def stack(self):
        message = input("Write your message: ")
        
        application = Layer()
        application.PDU = application.encapsulate(message, None)
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
        
        net_interface = Layer()
        net_interface.PDU = net_interface.encapsulate(packet, 'Frame')
        frame = net_interface.PDU
        print("Network Interface Layer - Created Frame (Frame Footer implied):")
        print("{}\n".format(frame))
        
        self.send_msg(frame)
        print("Frame sent.\n")
    
    
    def send_msg(self, data):
        self.CONNECTION.sendall(json.dumps(data).encode())
    
    
    def close_socket(self):
        try:
            print("Closing socket...")
            self.CONNECTION.close()
            self.CONNECTION = None
        except (OSError, socket.error):
            print("Already closed.\n")
    
    
    def help(self):
        print("\nOPTIONS")
        print("     help                See the manual.")
        print("     ping                Receive the server IP.")
        print("     handshake           Simulate a TCP handshake.")
        print("     stack               Simulate the TCP/IP encapsulation process.")
        print("     [ text ]            Send message to server.")
        print("     exit, [ empty ]     Quit the program.")
        print("")


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
                    client.send_msg(client.COMMAND)
            except (socket.error, BrokenPipeError, ConnectionResetError):
                print("Error connecting to server. Attempting to reconnect...\n")
                max_retries = 5
                
                client.close_socket()
                
                for i in range(max_retries):
                    client.setup()
                    if client.CONNECTION is not None:
                        break
                
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

