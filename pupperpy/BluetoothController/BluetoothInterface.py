import bluetooth
import json

## Configurable ##
hostMACAddress = 'B8:27:EB:5E:D6:8F' ## MAC address to bluetooth adapter on pi
BLE_PORT = 3
BLE_MSG_SIZE = 1024
TIMEOUT = 10
## End Config ##

class BluetoothClient(object):
    def __init__(self):
        self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.socket.settimeout(TIMEOUT)

    def connect(self):
        self.socket.connect((hostMACAddress, BLE_PORT))

    def send(self, msg):
        if not isinstance(msg, dict):
            self.close()
            raise ValueError('Message must be a dict')

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
        self.connect()
        return self

    def __exit__(self, type, value, tb):
        self.close()

def BluetoothServer(object):
    def __init__(self):
        self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.socket.bind((hostMACAddress, BLE_PORT))

    def connect(self):
        self.socket.listen(1)
        try:
            self.client, client_info = server_soc.accept()
            print('Successfully connected to client: %s' % client_info)
        except:
            self.close('Failed to connect to client')

    def send(self, msg):
        if not isinstance(msg, dict):
            self.close()
            raise ValueError('Message must be a dict')

        out = json.dumps(msg).encode('utf-8')
        self.client.send(msg)

    def recv(self):
        try:
            data = self.client.recv(BLE_MSG_SIZE)
            out = json.loads(data.decode('utf-8'))
            return out
        except:
            return None

    def close(self):
        self.client.close()
        self.socket.close()
        print('Bluetooth Socket Closed')

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, type, value, tb):
        self.close()
