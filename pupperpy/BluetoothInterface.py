import bluetooth

## Configurable ##
hostMACAddress = '60-F8-1D-AA-FE-19' ## MAC address to bluetooth adapter on pi
BLE_PORT = 3
BLE_MSG_SIZE = 1024
TIMEOUT = 10
## End Config ##

class BluetoothInterface(object):
    def __init__(self):
        self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.socket.settimeout(TIMEOUT)

    def connect(self):
        self.socket.connect((hostMACAddress, BLE_PORT))

    def send(self, msg):
        self.socket.send(msg)

    def recv(self):
        try:
            return self.socket.recv(BLE_MSG_SIZE)
        except:
            return None  # in case of timeout

    def close(self):
        self.socket.close()

    def __enter__(self):
        self.socket.connect((hostMACAddress, BLE_PORT))
        return self

    def __exit__(self, type, value, tb):
        self.socket.close()
