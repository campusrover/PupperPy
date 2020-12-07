import random
import numpy as np
import time
from ControllerState import ControllerState
#from CommandInterface import Control
from datetime import datetime as dt
from PusherInterface import PusherClient
from Behavior import control_loop_tree

from Testing.TestSensorData import TestCMDSub, TestCVSub, TestIMU, TestObjectSensors

# actual robot imports
#from UDPComms import Publisher
#from UDPComms import Subscriber
#from imu_tools import IMU
#from object_detection import ObjectSensors

CONFINED_TESTING_MODE = True
WEB_MODE = False

MESSAGE_RATE = .5
TURNING_VELOCITY = .5
FORWARD_VELOCITY = 1
BOX_SIZE_LIMIT = 200
MAXIMUM_WAIT_TIME = 60
CAMERA_SIZE = 300

CV_PORT = 105  # computer vision
CMD_PORT = 8810

if not CONFINED_TESTING_MODE:
    pupper_pub = Publisher(8830)
    pupper_sub = Subscriber(8840, timeout=0.01)
data = None

# pos = None
# timer = 0

max_x_velocity = 0.4
max_y_velocity = 0.3
max_yaw_rate = 2.0

#control = Control()


class RobotData():
    """
    Class containing sensor data that can update with new information.
    """

    def __init__(self, rate=0.1, imu=None):

        if CONFINED_TESTING_MODE:
            self.obj_sensors = TestObjectSensors()
            if imu is None:
                self.imu = TestIMU()
            else:
                self.imu = imu
            self.cv_sub = TestCVSub()
            self.cmd_sub = TestCMDSub()
        else:
            self.obj_sensors = ObjectSensors()
            if imu is None:
                self.imu = TestIMU()
            else:
                self.imu = imu
            # self.cv_sub = Subscriber(CV_PORT)
            # self.cmd_sub = Subscriber(CMD_PORT)
            self.cv_sub = TestCVSub()
            self.cmd_sub = TestCMDSub()
        self.data = None

    def update(self):
        imu = self.imu.read()
        obj = self.obj_sensors.read()

        default_cv_dict = dict.fromkeys(['bbox_x', 'bbox_y', 'bbox_h', 'bbox_w',
                                         'bbox_label', 'bbox_confidence'], np.nan)
        try:
            # Ben's computer vision service is publishing a list of dictionaries per object
            cv = self.cv_sub.get()
            if cv == []:  # if no objects detected
                cv = default_cv_dict
            else:
                cv = cv[0]  # supposedly the first object
        except:
            cv = default_cv_dict

        try:
            cmd = self.cmd_sub.get()
        except:
            cmd = {'ly': 0, 'lx': 0, 'rx': 0}

        # some guessing before we get clean data i think
        x_vel = cmd['ly'] * max_x_velocity
        y_vel = cmd['lx'] * -max_y_velocity
        yaw_rate = cmd['rx'] * -max_yaw_rate
        time = dt.now().timestamp()

        # construct the dictionary
        self.data = {'message_rate': MESSAGE_RATE,
                     'time': time,
                     'x_acc': imu['x_acc'],
                     'y_acc': imu['y_acc'],
                     'z_acc': imu['z_acc'],
                     'x_pos': imu['x_pos'],
                     'y_pos': imu['y_pos'],
                     'roll': imu['roll'],
                     'pitch': imu['pitch'],
                     'yaw': imu['yaw'],
                     'left_sensor': obj['left'],
                     'right_sensor': obj['right'],
                     'center_sensor': obj['center'],
                     'bbox_x': cv['bbox_x'],
                     'bbox_y': cv['bbox_y'],
                     'bbox_h': cv['bbox_h'],
                     'bbox_w': cv['bbox_w'],
                     'bbox_label': cv['bbox_label'],
                     'bbox_confidence': cv['bbox_confidence'],
                     'x_vel': x_vel,
                     'y_vel': y_vel,
                     'yaw_rate': yaw_rate,
                     'sys_calibration': imu['sys_calibration'],
                     'gyro_calibration': imu['gyro_calibration'],
                     'accel_calibration': imu['accel_calibration'],
                     'mag_calibration': imu['mag_calibration']}
