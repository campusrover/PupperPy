import pandas as pd
import numpy as np
from numpy import cos, sin
#from pupperpy.imu_tools import IMU


class KalmanFilter(object):
    def __init__(self, est_err, obs_err, X0=None):
        self.X = np.array([[0,0,0,0,0,0,0,0]]).T # x, y, vx, vy, ax, ay, yaw, yaw_rate
        if X0 is not None:
            self.X = X0
        # self.est_err = np.array([[1, 1, 1, 1, 1, 1]]) # estimate this somehow
        # self.obs_err = np.array([[0, 0, 1, 1, 1, 1]]) # snag these from sensor
        self.est_err = est_err
        self.obs_err = obs_err
        self.Q = self.est_err * self.est_err.T
        self.R = self.obs_err * self.obs_err.T
        self.P = np.identity(self.X.shape[0]) * 0.1
        #self.P = self.R

    def step(self, dt, vx, vy, ax, ay, new_yaw, yaw_rate):
        n = self.X.shape[0]
        yaw = np.deg2rad(self.X[-2, 0])
        A = np.array([[1, 0, dt*cos(yaw), dt*sin(yaw),
                       0.5*(dt**2)*cos(yaw), 0.5*(dt**2)*sin(yaw), 0, 0],
                      [0, 1, dt*sin(yaw), dt*cos(yaw),
                       0.5*(dt**2)*sin(yaw), 0.5*(dt**2)*cos(yaw), 0, 0],
                      [0, 0, 1, 0, dt, 0, 0, 0],
                      [0, 0, 0, 1, 0, dt, 0, 0],
                      [0, 0, 0, 0, 1, 0, 0, 0],
                      [0, 0, 0, 0, 0, 1, 0, 0],
                      [0, 0, 0, 0, 0, 0, 1, dt],
                      [0, 0, 0, 0, 0, 0, 0, 1]])
        X_prime = A.dot(self.X)
        #P_prime = A.dot(self.P).dot(A.T) + self.Q
        P_prime = np.diag(np.diag(A.dot(self.P).dot(A.T) + self.Q))
        # ignoring nothing
        # H = np.identity(n)
        # Ignoring pos and velocity input
        # H = np.array([[0,0,0,0,0,0,0,0],
        #               [0,0,0,0,0,0,0,0],
        #               [0,0,0,0,0,0,0,0],
        #               [0,0,0,0,0,0,0,0],
        #               [0,0,0,0,1,0,0,0],
        #               [0,0,0,0,0,1,0,0],
        #               [0,0,0,0,0,0,1,0],
        #               [0,0,0,0,0,0,0,1]])
        # Ignoring only non-existant position measure
        H = np.array([[0,0,0,0,0,0,0,0],
                      [0,0,0,0,0,0,0,0],
                      [0,0,1,0,0,0,0,0],
                      [0,0,0,1,0,0,0,0],
                      [0,0,0,0,1,0,0,0],
                      [0,0,0,0,0,1,0,0],
                      [0,0,0,0,0,0,1,0],
                      [0,0,0,0,0,0,0,1]])

        Y = np.array([[0, 0, vx, vy, ax, ay, new_yaw, yaw_rate]]).T
        for i in range(Y.shape[0]):
            if Y[i, 0] is None:
                Y[i,0] = 0
                H[i,i] = 0

        S = H.dot(P_prime).dot(H.T) + self.R
        #K = P_prime.dot(H).dot(np.linalg.inv(S))
        K = P_prime.dot(H.T) / S

        #vx = self.X[2][0] + dt*ax
        #vy = self.X[3][0] + dt*ay
        #Y = np.array([[self.X[0][0]+vx*dt+0.5*ax*dt**2,
        #               self.X[1][0]+vy*dt+0.5*ay*dt**2,
        #               vx, vy, ax, ay]]).T

        Y = H.dot(Y)
        X = X_prime + K.dot(Y - H.dot(X_prime))
        P = (np.identity(len(K)) - K.dot(H)).dot(P_prime)
        self.X = X
        self.P = P


def rotate_imu_acceleration(yaw, pitch, roll, x_acc, y_acc, z_acc):
    X = np.array([x_acc, y_acc, z_acc])
    a = np.deg2rad(yaw)
    b = np.deg2rad(pitch)
    c = np.deg2rad(roll)
    R = np.array([[np.cos(a)*np.cos(b),
                   np.cos(a)*np.sin(b)*np.sin(c) - np.sin(a)*np.cos(c),
                   np.cos(a)*np.sin(b)*np.cos(c) - np.sin(a)*np.sin(c)],
                  [np.sin(a)*np.cos(b),
                   np.sin(a)*np.sin(b)*np.sin(c) + np.cos(a)*np.cos(c),
                   np.sin(a)*np.sin(b)*np.cos(c) - np.cos(a)*np.sin(c)],
                  [-np.sin(b), np.cos(b)*np.sin(c), np.cos(b)*np.sin(c)]])
    Xr = np.dot(R,X)
    return Xr

def simple_rotation(yaw, x_acc, y_acc):
    a = np.deg2rad(yaw)
    ax = np.cos(a)*x_acc + np.sin(a)*y_acc
    ay = np.sin(a)*x_acc + np.cos(a)*y_acc
    return ax, ay


def decode_kalman_position(df):
    cols = ['yaw', 'pitch', 'roll', 'x_acc', 'y_acc', 'z_acc']
    df = df.copy().dropna(subset=cols)
    means = df[:30][cols].mean().to_numpy()
    stds = df[:30][cols].std().to_numpy()
    time = 0
    out = []
    # large change in decoding with choice of error
    est_err = np.array([[5,5,.05,.05,.01,.01, .01, .1, .1]])
    #def rotate(row):
    #    ax, ay, az = rotate_imu_acceleration(*row[cols])
    #    return pd.Series({'ax':ax, 'ay':ay, 'az':az})

    #df[['ax', 'ay', 'az']] = df.apply(rotate, axis=1)
    def rotate(row):
        ax, ay = simple_rotation(row['yaw'], row['x_acc'], row['y_acc'])
        return pd.Series({'ax':ax,'ay':ay})

    df[['ax', 'ay']] = df.apply(rotate, axis=1)
    err = df[:30][['x_acc', 'y_acc', 'yaw']].std().to_list()
    means = df[:30][['x_acc', 'y_acc', 'yaw']].mean().to_numpy()
    means = [0,0, means[-1]]
    # negligble difference when subtracting mean offset

    obs_err = np.array([[1, 1, 5, 5, *err, .1]])

    # Get rolling average of acceleration
    # Rolling average doesn't really help at all
    #df[['max', 'may']] = df[['ax', 'ay']].rolling(30).mean()
    #df = df.dropna(subset=['max', 'may'])

    X0 = np.array([[0,0,0,0,0,0, means[-1], 0]]).T
    model = KalmanFilter(est_err, obs_err, X0=X0)
    for i,row in df.iterrows():
        dt = row['timestamp'] - time
        time = row['timestamp']
        model.step(dt, row['robo_x_vel'], row['robo_y_vel'], row['x_acc']-means[0], row['y_acc']-means[1],  row['yaw'], row['robo_yaw_rate'])
        X = model.X.flatten()
        tmp = {k:v for k,v in zip(['x', 'y', 'vx', 'vy', 'ax', 'ay', 'yaw'], X)}
        tmp['time'] = time
        out.append(tmp)

    return pd.DataFrame(out), model


def decode_simple_position(df):
    cols = ['yaw', 'pitch', 'roll', 'x_acc', 'y_acc', 'z_acc']
    df = df.copy().dropna(subset=cols)
    means = df[:30][cols].mean().to_numpy()
    time = 0
    model = SimpleModel()
    out = []
    for i, row in df.iterrows():
        dat = row[cols] - means
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
        ax, ay, az = rotate_imu_acceleration(yaw, pitch, roll, x_accel, y_accel, z_accel)
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

