from pupperpy.imu_tools import IMU
from pupperpy.kalman import KalmanFilter, simple_rotation, rotate_imu_acceleration
from pupperpy.daq_tools import RepeatTimer
from pupperpy.ControllerState import ControllerState
import numpy as np
import time

# From StandfordQuadrupped.pupper.Config
max_x_velocity = 0.4
max_y_velocity = 0.3
max_yaw_rate = 2.0


class PositionTracker(object):
    def __init__(self, control_state, rate=0.01):
        self.imu = IMU()
        self._last_imu_read = None
        self.timer = RepeatTimer(rate, self._step)
        self._last_time = None
        self._rate = rate
        self._last_cmd = None
        self.control = control_state
        self.running = False
        #self.cmd_sub = Subscriber(CMD_PORT)
        self._init_model()

    def _init_model(self):
        means = self.imu.means
        variances = self.imu.variances
        ax = variances['x_acc']
        ay = variances['y_acc']
        yaw_err = variances['yaw']
        est_err = np.array([[5, 5, .05, .05, .01, .01, .1, .1]])
        obs_err = np.array([[10, 10, 5, 5, ax, ay, yaw_err, yaw_err]])
        X0 = np.array([[0, 0, 0, 0, 0, 0, means['yaw'], 0]]).T
        self.model = KalmanFilter(est_err, obs_err, X0=X0)
        x, y, vx, vy, ax, ay, y, yr = self.model.X.T[0]
        # x & y are in cartesian coordinates
        # vx, vy, ax, and ay are all oriented so that the robot's heading is the x direction
        self.data = {'x':x, 'y':y, 'x_vel': vx, 'y_vel': vy,
                     'x_acc': ax, 'y_acc': ay, 'yaw': y,
                     'yaw_rate': yr}

    def _step(self):
        try:
            data = imu.read()
        except:
            data = self._last_imu_read

        self._last_imu_read = data
        means = self.imu.means
        # ax, ay = simple_rotation(data['yaw'], data['x_acc'] - means['x-acc'],
        #                          data['y_acc'] - means['y_acc'])
        # ax, ay, az = rotate_imu_acceleration(data['yaw'], data['pitch'], data['roll'],
        #                                      data['x_acc'] - means['x_acc'],
        #                                      data['y_acc'] - means['y_acc'],
        #                                      data['z_acc'] - means['z_acc'])
        if data is None:
            x_acc = 0
            y_acc = 0
            yaw = 0
        else:
            x_acc = data['x_acc']
            y_acc = data['y_acc']
            yaw = data['yaw']

        cmd = self.control.get_state()
        walking = self.control.walking
        # try:
        #     cmd = self.cmd_sub.get()
        # except TimeoutError:
        #     if self._last_cmd is not None:
        #         cmd = self._last_cmd
        #     else:
        #         cmd = ControllerState().get_state()

        self._last_cmd = cmd
        x_vel = cmd['ly'] * max_x_velocity
        y_vel = cmd['lx'] * -max_y_velocity
        yaw_rate = cmd['rx'] * -max_yaw_rate
        timestamp = time.time()
        dt = timestamp - self._last_time
        self._last_time = timestamp

        # This is so that any joystick commands are ignored while robot is not
        # in a walking state
        if not walking:
            x_vel, y_vel, yaw_rate = (0, 0, 0)

        self.model.step(dt, x_vel, y_vel, x_acc, y_acc, yaw, yaw_rate)
        x, y, vx, vy, ax, ay, y, yr = self.model.X.T[0]
        # x & y are in cartesian coordinates
        # vx, vy, ax, and ay are all oriented so that the robot's heading is the x direction
        self.data = {'x':x, 'y':y, 'x_vel': vx, 'y_vel': vy,
                     'x_acc': ax, 'y_acc': ay, 'yaw': y,
                     'yaw_rate': yr}

    def run(self):
        self._last_time = time.time()
        self.timer.start()
        self.running = True

    def stop(self):
        self.timer.cancel()
        self.running = False
