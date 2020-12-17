"""
Test classes to alternatively run scripts without physical feedback from robot.
"""

from numpy import random

"""
Creates random IMU data.
"""


class TestIMU:
    def __init__(self):
        self.data = {}
        keys = ['x_acc', 'y_acc', 'z_acc', 'roll', 'pitch', 'yaw', 'sys_calibration',
                'gyro_calibration', 'accel_calibration', 'mag_calibration']
        for key in keys:
            self.data[key] = random.uniform(-30, 30)
        self.data['x_pos'] = 0
        self.data['y_pos'] = 0

    def read(self):
        for key in self.data.keys():
            if not (key == 'x_pos' or key == 'y_pos'):
                self.data[key] = random.uniform(-30, 30)
        self.data['x_pos'] += random.uniform(0, 5)
        self.data['y_pos'] += random.uniform(-5, 5)
        return self.data


"""
Creates random range-finding sensor data.
"""


class TestObjectSensors:
    def __init__(self):
        self.data = {}
        keys = ['left', 'right', 'center']
        for key in keys:
            self.data[key] = random.choice([True, False])

    def read(self):
        for key in self.data.keys():
            self.data[key] = random.choice([True, False])
        return self.data


"""
Creates random computer vision data.
"""


class TestCVSub:
    def __init__(self):
        self.data = [{}]
        keys = ['bbox_x', 'bbox_y', 'bbox_h',
                'bbox_w', 'bbox_label', 'bbox_confidence']
        for key in keys:
            if key == 'bbox_confidence':
                self.data[0][key] = random.uniform(0, 1)
            elif key == 'bbox_label':
                self.data[0][key] = 'ball'
            elif key == 'bbox_h' or key == 'bbox_w':
                self.data[0][key] = random.uniform(200, 300)
            else:
                self.data[0][key] = random.uniform(0, 300)

    def get(self):
        for key in self.data[0].keys():
            if key == 'bbox_confidence':
                self.data[0][key] = random.uniform(0, 1)
            elif key == 'bbox_label':
                self.data[0][key] = 'ball'
            elif key == 'bbox_h' or key == 'bbox_w':
                self.data[0][key] = random.uniform(200, 300)
            else:
                self.data[0][key] = random.uniform(0, 300)
        return self.data


"""
Creates random command feedback.
"""


class TestCMDSub:
    def __init__(self):
        self.data = {}
        keys = ['ly', 'lx', 'rx']
        for key in keys:
            self.data[key] = random.random()

    def get(self):
        for key in self.data.keys():
            self.data[key] = random.random()
        return self.data
