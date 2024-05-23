import socket
import selectors
import struct

__author__ = 'Matthis "Suske" Perreaux'

class _UDPManager:

    def __init__(self, addr, mode):
        self.addr = addr

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        if mode == "client":
            print("listening on", addr)
            self.socket.setblocking(False)
            self.socket.bind(('', addr[1]))
            mreq = struct.pack("4sl", socket.inet_aton(self.addr[0]), socket.INADDR_ANY)
            self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            # self.socket.listen(32)
        else:
            self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 4)

    def recv(self):

        try:
            data = self.socket.recv(1024)
        except BlockingIOError:
            return None
        else:
            return data

    def send(self, msg):
        self.socket.sendto(msg, self.addr)


class _TCPManager:

    def __init__(self, addr, mode):

        self.addr = addr
        self._init_socket()

        if mode == "master":
            print("listening on", addr)
            self.socket.bind(addr)
            self.socket.listen(32)
            self.selector = selectors.DefaultSelector()
            self.selector.register(self.socket, selectors.EVENT_READ)
        else:
            self.connected = False

    def _init_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setblocking(False)

    def _accept_wrapper(self, sock):
        client_socket, client_address = sock.accept()
        print("connection from", client_address)
        client_socket.setblocking(False)
        self.selector.register(client_socket, selectors.EVENT_READ, data=client_address)

    def _connect_wrapper(self):
        try:
            self.socket.connect(self.addr)
        except BlockingIOError:
            pass
        except OSError:
            pass

    def _close_wrapper(self, client_socket):
        self.selector.unregister(client_socket)
        client_socket.close()

    def _handle_client(self, client_socket, message):
        try:
            client_socket.sendall(message)
        except Exception as e:
            print("error occurred:", e)

    # TODO multi-threaded send?
    def send(self, msg):
        while len((events := self.selector.select(timeout=0))):
            for selector_key, _ in events:
                if selector_key.fileobj == self.socket:
                    self._accept_wrapper(selector_key.fileobj)
                else:
                    self._close_wrapper(selector_key.fileobj)

        for _, selector_key in self.selector.get_map().items():
            if selector_key.data is not None:
                client_socket = selector_key.fileobj
                self._handle_client(client_socket, msg)

    def recv(self):
        if not self.connected:
            self._connect_wrapper()
            self.connected = True

        try:
            data = self.socket.recv(1024)
        except BlockingIOError:
            return None
        except OSError:
            self.connected = False
            return None
        else:
            if not data:
                self.socket.close()
                self._init_socket()
                self.connected = False
                return None
            return data


class NetworkModeException(Exception):

    def __init__(self, method, mode):
        super().__init__("The %s method is only allowed in %s mode" % (method, mode))


def require_mode(mode):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            if self.mode != mode:
                raise NetworkModeException(func.__name__, mode)
            return func(self, *args, **kwargs)

        return wrapper

    return decorator


class Network:

    def __init__(self, proto, mode, addr=None, port=7777):

        if mode not in ("master", "client"):
            raise ValueError("mode should be one of master or client")

        if proto not in ("tcp", "udp"):
            raise ValueError("proto should be one of tcp or udp")

        if proto == "udp" and not addr:
            raise ValueError("addr should be supplied in udp mode")

        if proto == "tcp" and mode == "client" and not addr:
            raise ValueError("addr should be supplied in tcp client mode")

        self.mode = mode
        addr = (addr if addr is not None else "0.0.0.0", 7777)

        self._mgr = (
            _TCPManager(addr, mode) if proto == "tcp" else _UDPManager(addr, mode)
        )

    @require_mode("master")
    def send(self, msg):
        return self._mgr.send(msg)

    @require_mode("client")
    def recv(self):
        return self._mgr.recv()
