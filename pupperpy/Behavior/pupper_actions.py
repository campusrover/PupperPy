import py_trees
import time


class MoveUntilObstaclesNode(py_trees.behaviour.Behaviour):

    def __init__(self, tsh):
        super(MoveUntilObstaclesNode, self).__init__(
            "Move Until Obstacles")
        self.tsh = tsh

    def setup(self):
        return

    def initialise(self):
        return

    def update(self):
        obj = self.tsh.control.obj_sensors.read()
        if any(obj.values()):
            self.feedback_message = "End of journey!"
            return py_trees.common.Status.SUCCESS
        else:
            self.feedback_message = "Still moving..."
            self.tsh.active_node = self
            self.tsh.control.move_forward()
            return py_trees.common.Status.RUNNING

    def terminate(self, new_status):
        return


class AvoidObstaclesNode(py_trees.behaviour.Behaviour):
    """
    Primitive behavior that moves robot forward for a set amount of time.
    """

    def __init__(self, tsh):
        super(AvoidObstaclesNode, self).__init__(
            "Avoid Obstacles")
        self.tsh = tsh

    def setup(self):
        return

    def initialise(self):
        return

    def update(self):
        obj = self.tsh.control.obj_sensors.read()
        if any(obj.values()):
            self.feedback_message = "Dodging obstacle..."
            self.tsh.active_node = self
            if obj['left'] and obj['center']:
                self.tsh.control.move_stop()
                self.tsh.control.turn_right()
            elif (obj['right'] and obj['center']) or obj['center']:
                self.tsh.control.move_stop()
                self.tsh.control.turn_left()
            elif obj['left']:
                self.tsh.control.move_forward()
                self.tsh.control.turn_right()
            elif obj['right']:
                self.tsh.control.move_forward()
                self.tsh.control.turn_left()
            elif not any(obj.values()):
                self.tsh.control.turn_stop()
            return py_trees.common.Status.RUNNING
        else:
            self.feedback_message = "Obstacle avoided!"
            return py_trees.common.Status.SUCCESS

    def terminate(self, new_status):
        return
