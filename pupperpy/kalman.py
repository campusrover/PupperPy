import pandas as pd
import numpy as np
from numpy import cos, sin
#from pupperpy.imu_tools import IMU


class KalmanFilter(object):
    def __init__(self, dt):
        self.dt = dt
        self.X = np.array([[0,0,0,0,0,0]]).T # x, y, vx, vy, ax, ay
        self.est_err = np.array([[1, 1, 1, 1, 1, 1]]) # estimate this somehow
        self.obs_err = np.array([[0, 0, 1, 1, 1, 1]]) # snag these from sensor
        self.Q = self.est_err * self.est_err.T
        self.R = self.obs_err * self.obs_err.T
        self.A = np.array([[1, 0, dt, 0, 0.5*(dt**2), 0],
                           [0, 1, 0, dt, 0, 0.5*(dt**2)],
                           [0, 0, 1, 0, dt, 0],
                           [0, 0, 0, 1, 0, dt],
                           [0, 0, 0, 0, 1, 0],
                           [0, 0, 0, 0, 0, 1]])



def decode_simple_position(df):
    cols = ['yaw', 'pitch', 'roll', 'x_acc', 'y_acc', 'z_acc']
    df = df.copy().dropna(subset=cols)
    time = 0
    model = SimpleModel()
    out = []
    for i, row in df.iterrows():
        dat = row[cols]
        dt = row['timestamp'] - time
        time = row['timestamp']
        model.step(*dat, dt)
        out.append({'x': model.x, 'y': model.y, 'z': model.z, 'vx':
                    model.x_vel, 'vy': model.y_vel, 'vz': model.z_vel, 'dt':dt})

    tmp = pd.DataFrame(out)
    return df.merge(tmp, left_index=True, right_index=True)


class SimpleModel(object):
    def __init__(self):
        self.yaw = 0
        self.pitch = 0
        self.roll = 0
        self.x_accel = 0
        self.y_accel = 0
        self.z_accel = 0
        self.x = 0
        self.y = 0
        self.z = 0
        self.x_vel = 0
        self.y_vel = 0
        self.z_vel = 0

    def step(self, yaw, pitch, roll, x_accel, y_accel, z_accel, dt):
        a = np.deg2rad(self.yaw)
        b = np.deg2rad(self.pitch)
        c = np.deg2rad(self.roll)
        R = np.array([[np.cos(a)*np.cos(b),
                       np.cos(a)*np.sin(b)*np.sin(c) - np.sin(a)*np.cos(c),
                       np.cos(a)*np.sin(b)*np.cos(c) - np.sin(a)*np.sin(c)],
                      [np.sin(a)*np.cos(b),
                       np.sin(a)*np.sin(b)*np.sin(c) + np.cos(a)*np.cos(c),
                       np.sin(a)*np.sin(b)*np.cos(c) - np.cos(a)*np.sin(c)],
                      [-np.sin(b), np.cos(b)*np.sin(c), np.cos(b)*np.sin(c)]])
        # R = np.array([[cos(b)*cos(c),
        #                sin(a)*sin(b)*cos(c) - cos(a)*sin(c),
        #                cos(a)*sin(b)*cos(c) - sin(a)*sin(c)],
        #               [cos(b)*sin(c),
        #                sin(a)*sin(b)*sin(c) + cos(a)*cos(c),
        #                cos(a)*sin(b)*sin(c) - sin(a)*cos(c)],
        #               [-sin(b), sin(a)*cos(b), cos(a)*cos(b)]])

        dx = dt*self.x_vel + 0.5*(dt**2)*self.x_accel
        dy = dt*self.y_vel + 0.5*(dt**2)*self.y_accel
        dz = dt*self.z_vel + 0.5*(dt**2)*self.z_accel
        X = np.array([dx, dy, dz])
        dX = np.dot(R, X)
        self.x += dX[0]
        self.y += dX[1]
        self.z += dX[2]
        self.x_vel = self.x_vel + dt*self.x_accel
        self.y_vel = self.y_vel + dt*self.y_accel
        self.z_vel = self.z_vel + dt*self.z_accel
        self.yaw = yaw
        self.pitch = pitch
        self.roll = roll
        self.x_accel = x_accel
        self.y_accel = y_accel
        self.z_accel = z_accel

