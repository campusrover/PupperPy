from numpy import random


class TestIMU:
    def __init__(self):
        self.data = {}
        keys = ['x_acc', 'y_acc', 'z_acc', 'roll', 'pitch', 'yaw', 'sys_calibration',
                'gyro_calibration', 'accel_calibration', 'mag_calibration']
        for key in keys:
            self.data[key] = random.uniform(-30, 30)

    def read(self):
        for key in self.data.keys():
            self.data[key] = random.uniform(-30, 30)
        return self.data


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


class TestCVSub:
    def __init__(self):
        self.data = [{}]
        keys = ['bbox_x', 'bbox_y', 'bbox_h',
                'bbox_w', 'bbox_label', 'bbox_confidence']
        for key in keys:
            if key == 'bbox_h' or key == 'bbox_w':
                self.data[0][key] = random.uniform(200, 300)
            else:
                self.data[0][key] = random.uniform(0, 300)

    def get(self):
        for key in self.data.keys():
            if key == 'bbox_h' or key == 'bbox_w':
                self.data[0][key] = random.uniform(200, 300)
            else:
                self.data[0][key] = random.uniform(0, 300)
        return self.data


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
