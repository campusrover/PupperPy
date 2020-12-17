"""
First finite state machine control loop that functions independently from CommandInterface. Can be also be run on randomized
data from test classes if robot cannot be run.
"""

import random
import numpy as np
import time
from ControllerState import ControllerState
from datetime import datetime as dt
from PusherInterface import PusherClient

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

robot_state = "RANDOM_SEARCH"
data = None

# pos = None
# timer = 0

max_x_velocity = 0.4
max_y_velocity = 0.3
max_yaw_rate = 2.0

"""
Class containing sensor data that can update with new information.
"""


class RobotData():

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


"""
Does random search (roomba) until target is found.
"""


def randomSearch():
    global data, robot_state
    new_command = ControllerState()

    if not data["bbox_confidence"]:  # target not found yet

        if data["center_sensor"] or data["left_sensor"]:
            new_command.right_analog_x = TURNING_VELOCITY  # just turn
            new_command.left_analog_y = FORWARD_VELOCITY * .3
        else:
            new_command.left_analog_y = FORWARD_VELOCITY  # go forward

    else:
        pass
    #    robot_state = "MOVE_TO_TARGET"

    return new_command


"""
Returns a new robot command based off camera and position data.
"""


def moveToTarget():
    global data, robot_state
    new_command = ControllerState()

    if data["bbox_confidence"]:

        """
        if cam_dat.target_bounding_box.area() > BOX_SIZE_LIMIT:  # if too close to object, stop
            robot_state = "SUCCESS"
            return new_command
        """
        # calculate how far bounding box is from center into offset
        target_median_x = data["bbox_x"] + data["bbox_w"] / 2
        offset = target_median_x - CAMERA_SIZE / 2

        # adjust yaw based on offset
        new_command.right_analog_x = offset * TURNING_VELOCITY / CAMERA_SIZE
        new_command.left_analog_y = FORWARD_VELOCITY

    else:  # no target found

        #robot_state = "RANDOM_SEARCH"

        pass

        """
        if data["center_sensor"]:
            robot_state = "AVOID_OBSTACLES"
        else:
            robot_state = "RANDOM_SEARCH"  # object probably moved
        """

    return new_command


"""
Returns new robot command to avoid and attempt to wall follow immediate obstacles.
"""


def avoidObstacles():
    global data, robot_state, timer
    new_command = ControllerState()

    if data["center_sensor"]:
        new_command.right_analog_x = TURNING_VELOCITY  # just turn
    elif data["left_sensor"]:
        # go forward (follow wall)
        new_command.left_analog_y = FORWARD_VELOCITY
    else:
        timer = 0
        robot_state = "MEMORY_NAVIGATION"

    return new_command


"""
Returns new robot command to navigate towards target last location.
"""


def memoryNavigation():
    global data, robot_state, timer
    new_command = ControllerState()

    if data["bbox_confidence"] > .5:
        robot_state = "MOVE_TO_TARGET"
    elif timer > MAXIMUM_WAIT_TIME:
        robot_state = "RANDOM_SEARCH"
    elif data["center_sensor"] > .5:
        robot_state = "AVOID_OBSTACLES"
    else:
        # TODO: turn toward target last known bearing()
        new_command.left_analog_y = FORWARD_VELOCITY

    return new_command


"""
Main loop.
"""
data_fetcher = RobotData()
data_fetcher.update()
pusher_client = PusherClient()  # WEB


# quick and dirty way to send start commands
robot_command = ControllerState()
robot_command.l1 = True

print(robot_state + " " + robot_command.__str__())
if not CONFINED_TESTING_MODE:
    pupper_pub.send(robot_command.get_state())

time.sleep(1)

robot_command = ControllerState()
robot_command.r1 = True

print(robot_state + " " + robot_command.__str__())
if not CONFINED_TESTING_MODE:
    pupper_pub.send(robot_command.get_state())

while True:

    time.sleep(.5)

    data_fetcher.update()
    data = data_fetcher.data  # update global data
    data["state"] = robot_state
    pusher_client.send(data)  # WEB

    robot_command = None

    if robot_state == "RANDOM_SEARCH":
        robot_command = randomSearch()
    elif robot_state == "MOVE_TO_TARGET":
        robot_command = moveToTarget()
    elif robot_state == "AVOID_OBSTACLES":
        robot_command = avoidObstacles()
    elif robot_state == "MEMORY_NAVIGATION":
        robot_command = memoryNavigation()
    else:
        pass
        # success
        # waitOutSuccess()

    print(robot_state + " " + robot_command.__str__())

    if not CONFINED_TESTING_MODE:
        pupper_pub.send(robot_command.get_state())
        try:
            # msg = pupper_sub.get()
            # print(msg)
            pass
        except timeout:
            pass
