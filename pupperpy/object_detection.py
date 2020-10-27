import pigpio
import time
from UDPComms import Publisher

LEFT_SENSOR = 5
RIGHT_SENSOR = 6
CENTER_SENSOR = 12
PUB_PORT = 9100
MESSAGE_RATE = 20
OUTPUT_MAP = {pigpio.HIGH: False, pigpio.LOW: True}

if __name__ == "__main__":
    pi = pigpio.pi()
    pi.set_mode(LEFT_SENSOR, pigpio.INPUT)
    pi.set_mode(RIGHT_SENSOR, pigpio.INPUT)
    pi.set_mode(CENTER_SENSOR, pigpio.INPUT)

    obj_pub = Publisher(PUB_PORT)

    try:
        while True:
            left = pi.read(LEFT_SENSOR)
            right = pi.read(RIGHT_SENSOR)
            center = pi.read(CENTER_SENSOR)
            out = {'left': OUTPUT_MAP[left],
                   'right': OUTPUT_MAP[right],
                   'center': OUTPUT_MAP[center]}
            obj_pub.send(out)
            time.sleep(1 / MESSAGE_RATE)
    except:
        pi.close()
        raise






