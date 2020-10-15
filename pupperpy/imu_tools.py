import datetime as dt
import time
import numpy as np
import pandas as pd
from adafruit_bno055 import BNO055_I2C
from busio import I2C

# Setup to use GPIO 0 and 1 as I2C interface, in config.txt: dtparam=i2c0=on,
# dtparam=i2c1=off, dtparam=i2c_arm=on, dtparam=i2c_arm_baudrate=10000
SCL_GPIO = 1
SDA_GPIO = 0

class IMU(object):
    def __init__(self):
        self.initSensor()

    def initSensor(self):
        self.i2c = I2C(SCL_GPIO, SDA_GPIO)
        self.sensor = BNO055_I2C(self.i2c)


    def log_data(self, seconds, rate=60):
        data = []
        start_time = dt.datetime.now()
        active = True
        next_mark = 10
        while active:
            acc = self.sensor.linear_acceleration
            euler = self.sensor.euler
            if all(x is None for x in euler) and all(x is None for x in acc):
                # If sensor drops out, refresh it and skip this iterations
                self.initSensor()
                continue

            tmp = {'time': dt.datetime.now(), 'roll': euler[0], 'pitch': euler[1], 'yaw': euler[2], 'x_acc': acc[0], 'y_acc': acc[1], 'z_acc': acc[2]}
            data.append(tmp)
            elapsed = (tmp['time'] - start_time).seconds
            if elapsed > next_mark:
                print('%i seconds elapsed' % elapsed)
                next_mark += 10

            if elapsed >= max_time:
                active = False

            time.sleep(1/rate)

        return pandas.DataFrame(data)


def save_data(df, fn):
    df.to_json(fn)

def read_data(fn):
    df = pd.read_json(fn)
    df['time'] = df.time.apply(lambda x: dt.datetime.fromtimestamp(x/1000))
    return df
