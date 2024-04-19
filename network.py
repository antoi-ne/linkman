import socket
import selectors

# Network object
class Network():

    # create the Network object
    def __init__(self, addr=None):
        
        # create the socket
        self.socket = None
        self._create_socket(addr)

        # check if this is the master
        if addr is None:

            # start to listen for clients
            self.socket.setblocking(False)
            addr = ('0.0.0.0', 7777)
            print('listening on', addr)
            self.socket.bind(addr)
            self.socket.listen(32)
            self.selector = selectors.DefaultSelector()
            self.selector.register(self.socket, selectors.EVENT_READ)

        # check if this is the client
        else:

            # connect to the master
            while self._connect_wrapper(addr) == False:
                pass
            self.socket.setblocking(False)

    # create the socket
    def _create_socket(self, is_client=False):

        # close the socket if needed
        if self.socket is not None:
            self.socket.close()

        # open the socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # set the connect timeout for clients
        if is_client == True:
            self.socket.settimeout(1)

    # connect to the master server
    def _connect_wrapper(self, addr):

            # connect to the master server
            print('Connecting to', addr)
            try:
                self.socket.connect((addr, 7777))

            # check if we didn't got any response
            except TimeoutError:
                return False
            
            # check for other errors
            except OSError:
                self._create_socket(addr)
                return False
            
            # we are connected !
            return True
    
    # accept a client
    def _connect_client(self, sock):
        client_socket, client_address = sock.accept()
        print('Connection from', client_address)
        client_socket.setblocking(False)
        self.selector.register(client_socket, selectors.EVENT_READ, data=client_address)

    # disconnect a client
    def _disconnect_client(self, client_socket):
        self.selector.unregister(client_socket)
        client_socket.close()
    
    # send a message to a client
    def _send_client(self, client_socket, message):
        client_socket.sendall(message)
    
    # senf a message to all clients
    def send(self, message):

        # check for all clients (dis)connection
        while len((events := self.selector.select(timeout=0))):
            for selector_key, _ in events:
                if selector_key.fileobj == self.socket:
                    self._connect_client(selector_key.fileobj)
                else:
                    self._disconnect_client(selector_key.fileobj)

        # send the message to all clients
        for _, selector_key in self.selector.get_map().items():
            if selector_key.data is not None:
                client_socket = selector_key.fileobj
                self._send_client(client_socket, message)
    
    # receive a message
    def recv(self):

        # try to receive a message
        try:
            data = self.socket.recv(1024)

        # check if there is no message received
        except BlockingIOError:
            return None
        
        # check if there is a problem with the socket (not connected for example)
        except OSError:
            return None
        
        # return the received data
        return data