import os
import datetime as dt
import time
import numpy as np
import pandas as pd
from adafruit_bno055 import BNO055_I2C
from pupperpy.busio import I2C
import pigpio

# Setup to use GPIO 0 and 1 as I2C interface,
# in config.txt:
#   dtparam=i2c_arm=on,i2c_arm_baudrate=10000
#   dtparam=i2c0=on,
#   dtparam=i2c1=off
I2C_BUS = 3
SCL_GPIO = 1
SDA_GPIO = 0
RST_GPIO = 16

# I think the BNO055 just needs time to properly startup after power on
# For calibration, the sensor automatically calibrates, but it seems cer

def reset_imu():
    try_count = 0
    pi = pigpio.pi()
    h = pi.i2c_open(0, int(0x28))
    connected = False
    while not connected:
        try:
            pi.i2c_read_byte(h)
            connected = True
            break
        except:
            pass

        try_count += 1
        if try_count > 20:
            raise Exception('IMU reset failed')

        pi.write(RST_GPIO, 0)
        time.sleep(5)
        pi.write(RST_GPIO, 1)

    pi.i2c_close(h)

def wait_for_imu():
    start = dt.datetime.now()
    connected = False
    while not connected:
        try:
            pi.i2c_read_byte(h)
            connected = True
            break
        except:
            pass

        time.sleep(10)

    end = dt.datetime.now()
    return start, end


def init_imu():
    os.system('sudo i2cdetect -y 10')
    os.system('sudo i2cdetect -y 11')
    os.system('sudo i2cdetect -y 0')

class IMU(object):
    def __init__(self):
        #reset_imu()
        #init_imu()
        self.initSensor()
        self.means, self.variances = self.average_filter()

    def initSensor(self):
        start = dt.datetime.now()
        connected = False
        ex = True
        while (dt.datetime.now() - start).seconds < 10 and not connected:
            try:
                self.i2c = I2C(I2C_BUS, SCL_GPIO, SDA_GPIO)
                self.sensor = BNO055_I2C(self.i2c)
                connected = True
                ex = False
            except BaseException as e:
                ex = e

        if not connected:
            raise ex

    def read(self):
        calibration_status = self.sensor.calibration_status
        # calibration status is a tuple with status for (system, gyro, accel, mag)
        # If calibration is 0 its not calibrated, 3 is fully calibrated
        # It needs to sit still to calibrate gyro, it needs to move to
        # calibrate the magnetometer and it needs to sit on each plane, but
        # even when not fully calibrated it work alright. Also it automatically
        # calibrates as it moves around. 
        acc = self.sensor.linear_acceleration
        euler = self.sensor.euler
        if all([x is None for x in euler]) and all([x is None for x in acc]):
            self.initSensor()
            acc = self.sensor.linear_acceleration
            euler = self.sensor.euler

        out = {'time': dt.datetime.now(), 'roll': euler[0],
               'pitch': euler[1], 'yaw': euler[2], 'x_acc': acc[0],
               'y_acc': acc[1], 'z_acc': acc[2], 'sys_calibration': calibration_status[0],
               'gyro_calibration': calibration_status[1], 'accel_calibration': calibration_status[2],
               'mag_calibration': calibration_status[3]}
        return out

    def average_filter(self):
        sums = dict.fromkeys(['x_acc', 'y_acc', 'z_acc', 'roll', 'pitch', 'yaw'], 0)
        for k in sums.keys():
            sums[k] = []

        for i in range(100):
            dat = self.read()
            for k,v in dat.items():
                if k in sums.keys() and v is not None:
                    sums[k].append(v)

            time.sleep(0.0001)

        mean = {}
        variance = {}
        for k,v in sums.items():
            mean[k] = np.mean(v)
            variance[k] = np.var(v)

        mean['time'] = dt.datetime.now()
        variance['time'] = mean['time']
        return mean, variance

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
