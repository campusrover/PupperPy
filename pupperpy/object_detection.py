import pigpio
import time
from UDPComms import Publisher

LEFT_SENSOR = 12
RIGHT_SENSOR = 5
CENTER_SENSOR = 6
PUB_PORT = 9100
MESSAGE_RATE = 20
OUTPUT_MAP = {pigpio.HIGH: False, pigpio.LOW: True}

class ObjectSensors(object):
    def __init__(self):
        self.pi = pigpio.pi()
        self.pi.set_mode(LEFT_SENSOR, pigpio.INPUT)
        self.pi.set_mode(RIGHT_SENSOR, pigpio.INPUT)
        self.pi.set_mode(CENTER_SENSOR, pigpio.INPUT)
        self.read()

    def read(self):
        pi = self.pi
        try:
            self.left = left = pi.read(LEFT_SENSOR)
            self.right = right = pi.read(RIGHT_SENSOR)
            self.center = center = pi.read(CENTER_SENSOR)
            out = {'left': OUTPUT_MAP[left],
                   'right': OUTPUT_MAP[right],
                   'center': OUTPUT_MAP[center]}
        except:
            pi.close()
            raise

        return out

    def close(self):
        self.pi.close()

if __name__ == "__main__":
    sensors = ObjectSensors()
    obj_pub = Publisher(PUB_PORT)

    while True:
        reading = sensors.read()
        obj_pub.send(reading)
        time.sleep(1 / MESSAGE_RATE)
