import traceback
from threading import Timer
from pupperpy.imu_tools import IMU
from pupperpy.object_detection import ObjectSensors
from UDPComms import Subscriber
import numpy as np
from datetime import datetime as dt
import pandas as pd

CV_PORT = 105
CMD_PORT = 8810
# From StandfordQuadrupped.pupper.Config
max_x_velocity = 0.4
max_y_velocity = 0.3
max_yaw_rate = 2.0

class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

class DataLogger(object):
    def __init__(self, rate=0.1, imu=None):
        self.obj_sensors = ObjectSensors()
        if imu is None:
            self.imu = IMU()
        else:
            self.imu = imu

        self.cv_sub = Subscriber(CV_PORT, timeout=0.5)
        self.cmd_sub = Subscriber(CMD_PORT)
        self.data = None
        self.data_columns  = ['timestamp', 'x_acc', 'y_acc', 'z_acc', 'roll',
                              'pitch', 'yaw', 'left_obj', 'right_obj',
                              'center_obj', 'bbox_x', 'bbox_y', 'bbox_h',
                              'bbox_w', 'bbox_label', 'bbox_confidence',
                              'robo_x_vel', 'robo_y_vel',
                              'robo_yaw_rate', 'imu_calibration',
                              'gyro_calibration', 'accel_calibration',
                              'mag_calibration']
        self.timer = RepeatTimer(rate, self.log)
        self.all_img = []

    def log(self):
        imu = self.imu.read()
        obj = self.obj_sensors.read()


        try:
            # Ben's computer vision service is publishing a list of
            # dictionaries, empty list is nothing
            cv = self.cv_sub.get()
           # print(cv)
            if cv == []:
                cv = dict.fromkeys(['bbox_x', 'bbox_y', 'bbox_h', 'bbox_w',
                                    'bbox_label', 'bbox_confidence'], np.nan)
            else:
                tmp = {'time': dt.now().timestamp(), 'img': cv.copy()}
                self.all_img.append(tmp)
                cv = cv[0]
        except BaseException as e:
            #print(traceback.format_exc())
            cv = dict.fromkeys(['bbox_x', 'bbox_y', 'bbox_h', 'bbox_w',
                                'bbox_label', 'bbox_confidence'], np.nan)

        try:
            cmd = self.cmd_sub.get()
        except:
            print('Not getting control data')
            cmd = {'ly': 0, 'lx': 0, 'rx': 0}

        x_vel = cmd['ly'] * max_x_velocity
        y_vel = cmd['lx'] * -max_y_velocity
        yaw_rate = cmd['rx'] * -max_yaw_rate
        time = dt.now().timestamp()

        row = [time, imu['x_acc'], imu['y_acc'], imu['z_acc'],
                imu['roll'], imu['pitch'], imu['yaw'],
                obj['left'], obj['right'], obj['center'],
                cv['bbox_x'], cv['bbox_y'], cv['bbox_h'],
                cv['bbox_w'], cv['bbox_label'], cv['bbox_confidence'],
                x_vel, y_vel, yaw_rate, imu['sys_calibration'], imu['gyro_calibration'],
                imu['accel_calibration'], imu['mag_calibration']]
        self.add_data(row)

    def add_data(self, row):
        #print(row[0])
        if self.data is None:
            self.start_time = row[0]
            row[0] -= self.start_time
            self.data = np.array(row)
        else:
            row[0] -= self.start_time
            self.data = np.vstack([self.data, row])

    def save_data(self, fn):
        np.save(fn, self.data)
        df = self.get_pandas()
        df.to_csv(fn.replace('npy', 'csv'))

    def save_img_data(self, fn):
        out = []
        t0 = None
        for x in self.all_img:
            if t0 is None:
                t0 = x['time']

            t1 = x['time'] - t0
            for y in x['img']:
                tmp = y.copy()
                tmp['time'] = t1
                out.append(tmp.copy())

        df = pd.DataFrame(out)
        df.to_csv(fn)

    def run(self):
        print('Running logger...')
        self.timer.start()

    def stop(self):
        self.timer.cancel()
        print('Logger stopped')

    def load_data(self, fn):
        self.data = np.load(fn)

    def get_pandas(self):
        return pd.DataFrame(self.data, columns=self.data_columns)


