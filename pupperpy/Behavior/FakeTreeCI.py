import FakeCommandInterface
from numpy import random

# temp class


class TestObjectSensors():
    def __init__(self):
        self.left = None
        self.center = None
        self.right = None

    def read(self):
        self.left = random.choice([True, False])
        self.center = random.choice([True, False])
        self.right = random.choice([True, False])

# temp class


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
                self.data[0][key] = 'tennis_ball'
            elif key == 'bbox_h' or key == 'bbox_w':
                self.data[0][key] = random.uniform(200, 300)
            else:
                self.data[0][key] = random.uniform(0, 300)
        return self.data


class FakeTreeControl(FakeCommandInterface.FakeControl):
    """
    Control extension that updates on command with behavior tree ticks.
    """

    def __init__(self):
        super(FakeTreeControl, self).__init__()
        self.obj_sensors = TestObjectSensors()
        self.cv_sub = TestCVSub
        self.data = {}

    def update_data(self):
        # grab data
        obj = self.obj_sensors.read()
        #pos = self.pos.data
        try:
            cv = self.cv_sub.get()
        # except timeout:
        except:
            cv = []

        self.data["obj"] = obj
        self.data["cv"] = cv
