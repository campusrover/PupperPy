import py_trees
import time


class MoveForwardNode(py_trees.behaviour.Behaviour):
    """
    Primitive behavior that moves robot forward for a set amount of time.
    """

    def __init__(self, tsh, time_length=.5):
        super(MoveForwardNode, self).__init__(
            "Move Forward " + str(time_length) + " Seconds")
        self.time_length = time_length
        self.start = 0
        self.tsh = tsh

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
            self.tsh.active_node = self
            # print(self.name)
            # update command interface
            return py_trees.common.Status.RUNNING

    def terminate(self, new_status):
        return


class TurnNode(py_trees.behaviour.Behaviour):
    """
    Primitive behavior that turns robot clockwise a set number of degrees.
    """

    def __init__(self, tsh, degrees=90):
        super(TurnNode, self).__init__(
            "Turn " + str(degrees) + " Degrees")
        self.initial_reading = None
        self.degrees = degrees
        self.tsh = tsh

    def setup(self):
        return

    def initialise(self):
        self.initial_reading = self.tsh.data.degrees
        return

    def update(self):
        if self.tsh.data.degrees >= initial_reading + self.degrees:
            self.feedback_message = "Done turning!"
            return py_trees.common.Status.SUCCESS
        else:
            self.feedback_message = "Still turning..."
            self.tsh.active_node = self
            # print(self.name)
            # update command interface
            return py_trees.common.Status.RUNNING

    def terminate(self, new_status):
        return
