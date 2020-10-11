import bluetooth
import json

## Configurable ##
hostMACAddress = 'B8:27:EB:5E:D6:8F' ## MAC address to bluetooth adapter on pi
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
        if not isinstance(msg, dict):
            raise ValueError('Message must be type dict or bytes')

        # Convert message to bytes
        out = json.dumps(msg).encode('utf-8')

        self.socket.send(out)

    def recv(self):
        try:
            msg = self.socket.recv(BLE_MSG_SIZE)
            # Convert bytes to dict
            out = json.loads(msg.decode('utf-8'))
            return out
        except:
            return None  # in case of timeout

    def close(self):
        self.socket.close()

    def __enter__(self):
        self.socket.connect((hostMACAddress, BLE_PORT))
        return self

    def __exit__(self, type, value, tb):
        self.socket.close()
