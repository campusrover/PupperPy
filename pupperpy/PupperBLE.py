from UDPComms import Publisher, Subscriber, timeout
import time
import bluetooth

## Configurable ##
hostMACAddress = '60-F8-1D-AA-FE-19' ## MAC address to bluetooth adapter on pi
BLE_PORT = 3
BLE_MSG_SIZE = 1024
MESSAGE_RATE = 20
## End Config ##

PUPPER_COLOR = {"red":0, "blue":0, "green":255}

pupper_pub = Publisher(8830)
pupper_sub = Subscriber(8840, timeout=0.01)


def send_command(values):
    left_y = -values["left_analog_y"]
    right_y = -values["right_analog_y"]
    right_x = values["right_analog_x"]
    left_x = values["left_analog_x"]

    L2 = values["l2"]
    R2 = values["r2"]

    R1 = values["r1"]
    L1 = values["l1"]

    square = values["button_square"]
    x = values["button_cross"]
    circle = values["button_circle"]
    triangle = values["button_triangle"]

    dpadx = values["dpad_x"]
    dpady = values["dpad_y"]

    msg = {
        "ly": left_y,
        "lx": left_x,
        "rx": right_x,
        "ry": right_y,
        "L2": L2,
        "R2": R2,
        "R1": R1,
        "L1": L1,
        "dpady": dpady,
        "dpadx": dpadx,
        "x": x,
        "square": square,
        "circle": circle,
        "triangle": triangle,
        "message_rate": MESSAGE_RATE,
    }
    pupper_pub.send(msg)

    try:
        msg = pupper_sub.get()
        return msg
    except timeout:
        return None

if __name__ == "__main__":
    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    server_sock.bind((hostMACAddress, BLE_PORT))
    server_sock.listen(1)
    try:
        client, client_info = server_soc.accept()
        client.send({'ps4_color': PUPPER_COLOR})
        print("running")
        while True:
            data = client.recv(BLE_MSG_SIZE)
            out_msg = send_command(data)
            if out_msg is not None:
                client.send(out_msg)

            time.sleep(1 / MESSAGE_RATE)
    except:
        print("Closing socket")
        client.close()
        server_sock.close()
