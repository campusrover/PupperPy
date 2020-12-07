import py_trees
import time


class MoveForwardNode(py_trees.behaviour.Behaviour):
    def __init__(self, time_length=.5):
        super(MoveForwardNode, self).__init__(
            "Move Forward " + str(time_length) + " Seconds")
        self.time_length = time_length
        self.start = 0

    def setup(self):
        return

    def initialise(self):
        self.start = time.time()

    def update(self):
        if (time.time() - self.start) >= self.time_length:
            self.feedback_message = "Done moving!"
            return py_trees.common.Status.SUCCESS
        else:
            self.feedback_message = "Still moving..."
            print(self.name)
            # update command interface
            return py_trees.common.Status.RUNNING

    def terminate(self, new_status):
        return


class TurnNode(py_trees.behaviour.Behaviour):
    def __init__(self, degrees=90, axis_data=None):
        super(MoveForwardNode, self).__init__(
            "Turn " + str(degrees) + " Degrees")
        #self.initial_reading = axis_data.degrees
        self.degrees = degrees
        self.axis_data = axis_data

    def setup(self):
        return

    def initialise(self):
        #self.initial_reading = self.axis_data.degrees
        return

    def update(self):
        if self.axis_data.degrees >= self.degrees:
            self.feedback_message = "Done turning!"
            return py_trees.common.Status.SUCCESS
        else:
            self.feedback_message = "Still turning..."
            print(self.name)
            # update command interface
            return py_trees.common.Status.RUNNING

    def terminate(self, new_status):
        return
