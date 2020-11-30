from pupperpy.imu_tools import IMU
from pupperpy.kalman import KalmanFilter, simple_rotation, rotate_imu_acceleration
from pupperpy.daq_tools import RepeatTimer
from pupperpy.ControllerState import ControllerState
import time

# Port to listen to for copy of command info for pupper
CMD_PORT = 8810
# From StandfordQuadrupped.pupper.Config
max_x_velocity = 0.4
max_y_velocity = 0.3
max_yaw_rate = 2.0


class PositionTracker(object):
    def __init__(self, rate=0.01):
        self.imu = IMU()
        self._last_imu_read = None
        self.timer = RepeatTimer(rate, self._step)
        self._last_time = None
        self._rate = rate
        self._last_cmd = None
        self.cmd_sub = Subscriber(CMD_PORT)
        self._init_model()

    def _init_model(self):
        variances = self.imu.means
        variances = self.imu.variances
        ax = variances['x_acc']
        ay = variances['y_acc']
        yaw_err = variances['yaw']
        est_err = np.array([[5, 5, .05, .05, .01, .01, .1]])
        obs_err = np.array([[10, 10, 5, 5, ax, ay, yaw]])
        X0 = np.array([[0, 0, 0, 0, 0, 0, mean['yaw'], 0]]).T
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
        x_acc = data['x_acc']
        y_acc = data['y_acc']
        yaw = data['yaw']

        try:
            cmd = self.cmd_sub.get()
        except TimeoutError:
            if self._last_cmd is not None:
                cmd = self._last_cmd
            else:
                cmd = ControllerState().get_state()

        self._last_cmd = cmd
        x_vel = cmd['ly'] * max_x_velocity
        y_vel = cmd['lx'] * -max_y_velocity
        yaw_rate = cmd['rx'] * -max_yaw_rate
        time = time.time()
        dt = time - self._last_time
        self._last_time = time

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

    def stop(self):
        self.timer.cancel()


def decode_kalman_position(df):
    cols = ['yaw', 'pitch', 'roll', 'x_acc', 'y_acc', 'z_acc']
    df = df.copy().dropna(subset=cols)
    means = df[:30][cols].mean().to_numpy()
    stds = df[:30][cols].std().to_numpy()
    time = 0
    out = []
    # large change in decoding with choice of error
    est_err = np.array([[5,5,.05,.05,.01,.01]])/4
    #def rotate(row):
    #    ax, ay, az = rotate_imu_acceleration(*row[cols])
    #    return pd.Series({'ax':ax, 'ay':ay, 'az':az})

    #df[['ax', 'ay', 'az']] = df.apply(rotate, axis=1)
    def rotate(row):
        ax, ay = simple_rotation(row['yaw'], row['x_acc'], row['y_acc'])
        return pd.Series({'ax':ax,'ay':ay})

    df[['ax', 'ay']] = df.apply(rotate, axis=1)
    err = df[:30][['ax', 'ay']].std().to_list()
    means = df[:30][['ax', 'ay']].mean().to_numpy()
    means = [0,0]
    # negligble difference when subtracting mean offset

    obs_err = np.array([[1, 1, 5, 5, *err]])/4

    # Get rolling average of acceleration
    # Rolling average doesn't really help at all
    df[['max', 'may']] = df[['ax', 'ay']].rolling(30).mean()
    df = df.dropna(subset=['max', 'may'])

    model = KalmanFilter(est_err, obs_err)
    for i,row in df.iterrows():
        dt = row['timestamp'] - time
        time = row['timestamp']
        model.step(dt, row['robo_x_vel'], row['robo_y_vel'], row['ax']-means[0], row['ay']-means[1])
        X = model.X.flatten()
        tmp = {k:v for k,v in zip(['x', 'y', 'vx', 'vy', 'ax', 'ay'], X)}
        tmp['time'] = time
        out.append(tmp)

    return pd.DataFrame(out), model
