import socket
import json

class Layer:

    def __init__(self, data):
        # Initial Layer variables
        self.PDU = data
        
        
    def decapsulate(self, packet):
        last_item = -1
        
        if packet[last_item] == 'Frame Footer':
            packet.pop()
    
        return packet.pop()


class Server:

    def __init__(self, host, port):
        # Initial Server variables
        self.HOST = host
        self.PORT = port
        self.MAX_TRANSFER_SIZE = 1024
        
        # Variables for later use
        self.TCP = None
        self.CONNECTION = None
        self.MESSAGE = None
    
    
    def setup(self):
        # Set up a TCP/IP server
        self.TCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
        # Bind the socket to server on defined address and port
        hook = (self.HOST, self.PORT)
        self.TCP.bind(hook)

        # Listen on bound socket
        max_connections = 1
        self.TCP.listen(max_connections)
    
    
    def await_connection(self):
        print("Waiting for connection...")
        self.CONNECTION, client = self.TCP.accept()
        
        print("Connected to client IP: {}".format(client))
    
    
    def await_message(self):
        try:
            # Receive and print data a few bytes at a time, as long as the client is sending something
            received = self.CONNECTION.recv(self.MAX_TRANSFER_SIZE)
            
            # Try to decode received message
            self.MESSAGE = json.loads(received.decode())
        except (json.JSONDecodeError, AttributeError):
            print("Data not in a valid JSON format or connection error.\n")
            self.CONNECTION.close()
    
    
    def ping(self):
        print("{} request received.\n".format(self.MESSAGE))
        self.CONNECTION.sendall(json.dumps(self.HOST).encode())
    
    
    def handshake(self):
        print("{} request received.".format(self.MESSAGE))
        self.CONNECTION.sendall(json.dumps('SYN').encode())
        print("'SYN' sent.")
        
        self.CONNECTION.sendall(json.dumps('ACK').encode())
        print("'ACK' sent.")
    
    
    def stack(self):
        # Normally one would not write repetitive code, but this was done to demonstrate the process clearly:
        net_interface = Layer(self.MESSAGE)
        frame = net_interface.PDU
        print("Frame received:")
        print("{}\n".format(frame))
        
        network = Layer(net_interface.decapsulate(frame))
        packet = network.PDU
        print("Network Interface Layer - Processed Frame Header:")
        print("{}\n".format(packet))
        
        transport = Layer(network.decapsulate(packet))
        segment = transport.PDU
        print("Network Layer - Processed Packet Header:")
        print("{}\n".format(segment))
        
        application = Layer(transport.decapsulate(segment))
        data = application.PDU
        print("Transport Layer - Processed Segment Header:")
        print("{}\n".format(data))
        
        message = application.decapsulate(data)
        print("Application Layer - Processed Data:")
        print("{}\n".format(message))
        
        print("Message Received: {}\n".format(message))
    
    
    def close_socket(self):
        print("Closing connection...")
        try:
            self.CONNECTION.shutdown(socket.SHUT_RDWR)
        except (OSError, socket.error):
            print("Already closed.\n")
        finally:
            print("Closing socket...")
            self.CONNECTION.close()
            self.TCP.close()


def main():
    host = "localhost"
    port = 3333
    server = Server(host, port)
    server.setup()
    server.await_connection()
    
    try:
        while True:
            server.await_message()
            
            if not server.MESSAGE:
                break
            
            if server.MESSAGE == 'ping':
                server.ping()
                
            elif server.MESSAGE == 'SYN':
                server.handshake()
                
            elif isinstance(server.MESSAGE, list) == True:
                server.stack()
            
            else:
                print("Received: {}\n".format(server.MESSAGE))
    except (KeyboardInterrupt):
        print("\nConnection interrupted by user.\n")
    except (socket.error, BrokenPipeError, ConnectionResetError):
        print("Error or socket was closed by client earlier than expected.\n")
    except (Exception):
        print("Unexpected error during main runtime.\n")
    
    finally:
        server.close_socket()
        print("Quitting the program...")


if __name__ == "__main__":
    main()
    
