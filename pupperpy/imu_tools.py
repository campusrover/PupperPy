import datetime as dt
import time
import numpy as np
import pandas as pd
from adafruit_bno055 import BNO055_I2C
from busio import I2C

# Setup to use GPIO 0 and 1 as I2C interface,
# in config.txt:
#   dtparam=i2c_arm=on,i2c_arm_baudrate=10000
#   dtparam=i2c0=on,
#   dtparam=i2c1=off
SCL_GPIO = 1
SDA_GPIO = 0

class IMU(object):
    def __init__(self):
        self.initSensor()
        self.error_values = self.average_filter()

    def initSensor(self):
        self.i2c = I2C(SCL_GPIO, SDA_GPIO)
        self.sensor = BNO055_I2C(self.i2c)

    def read(self):
        acc = self.sensor.linear_acceleration
        euler = self.sensor.euler
        if all([x is None for x in euler]) and all([x is None for x in acc]):
            self.initSensor()
            acc = self.sensor.linear_acceleration
            euler = self.sensor.euler

        out = {'time': dt.datetime.now(), 'roll': euler[0],
               'pitch': euler[1], 'yaw': euler[2], 'x_acc': acc[0],
               'y_acc': acc[1], 'z_acc': acc[2]}
        return out

    def average_filter(self):
        sum_x_acc = 0
        sum_y_acc = 0
        sum_z_acc = 0
        sum_roll = 0
        sum_pitch = 0
        sum_yaw = 0

        for i in range(100):
            dat = self.read()
            sum_x_acc += dat['x_acc']
            sum_y_acc += dat['y_acc']
            sum_z_acc += dat['z_acc']
            sum_roll += dat['roll']
            sum_pitch += dat['pitch']
            sum_yaw += dat['yaw']

        sum_x_acc /= 100
        sum_y_acc /= 100
        sum_z_acc /= 100
        sum_roll /= 100
        sum_pitch /= 100
        sum_yaw /= 100
        out = {'time': dt.datetime.now(), 'roll': sum_roll,
               'pitch': sum_pitch, 'yaw': sum_yaw, 'x_acc': sum_x_acc,
               'y_acc': sum_y_acc, 'z_acc': sum_z_acc}
        return out

    def log_data(self, seconds, rate=60):
        data = []
        start_time = dt.datetime.now()
        active = True
        next_mark = 10
        while active:
            data.append(self.read())
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

def get_pos(time, acc, window=2):
    pos = []
    tout = []
    curr = 0
    t1 = time[0]
    i = 0
    while t1 <= time[-1]-window:
        idx = np.where((time >= t1) & (time < t1+window))[0]
        tout.append(np.mean(time[idx]))
        delta = np.sum(acc[idx])*window
        curr += delta
        pos.append(curr)
        t1 = t1 + window
        i += 1

    return np.array(tout), np.array(pos)
