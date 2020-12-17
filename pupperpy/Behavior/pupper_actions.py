import py_trees
import time
import numpy as np


class MeanderNode(py_trees.behaviour.Behaviour):
    """
    Primitive behavior that moves robot forward until it sees Control's target.
    """

    def __init__(self, tsh):
        super(MeanderNode, self).__init__(
            "Meander")
        self.tsh = tsh

    def setup(self):
        return

    def initialise(self):
        return

    def update(self):
        obj = self.tsh.control.last_obj
        cv = self.tsh.control.last_cv
        print(any([x['bbox_label'] == self.tsh.control.target for x in cv]))
        if any([x['bbox_label'] == self.tsh.control.target for x in cv]):
            self.feedback_message = "End of journey!"
            return py_trees.common.Status.SUCCESS
        elif any(obj.values()):
            self.feedback_message = "Obstacle detected!"
            return py_trees.common.Status.FAILURE
        else:
            self.feedback_message = "Still moving..."
            self.tsh.set_active_node(self)
            self.tsh.control.turn_stop()
            self.tsh.control.move_forward()
            return py_trees.common.Status.RUNNING

    def terminate(self, new_status):
        return


class AvoidObstaclesNode(py_trees.behaviour.Behaviour):
    """
    Primitive behavior that moves robot forward for a set amount of time - see Roshan's CommandInterface loop.
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
            self.tsh.set_active_node(self)
            if obj['left'] and obj['center']:
                self.tsh.control.move_stop()
                self.tsh.control.turn_right()
            elif (obj['right'] and obj['center']) or obj['center']:
                self.tsh.control.move_stop()
                self.tsh.control.turn_left()
            elif obj['left']:
                self.tsh.control.move_forward(.3)
                self.tsh.control.turn_right()
            elif obj['right']:
                self.tsh.control.move_forward(.3)
                self.tsh.control.turn_left()
            elif not any(obj.values()):
                self.tsh.control.turn_stop()
            return py_trees.common.Status.RUNNING
        else:
            self.feedback_message = "Obstacle avoided!"
            return py_trees.common.Status.SUCCESS

    def terminate(self, new_status):
        return


class GoToTargetNode(py_trees.behaviour.Behaviour):
    """
    Primitive behavior that moves and centers the robot towards its target - see Roshan's CommandInterface loop.
    """

    def __init__(self, tsh):
        super(GoToTargetNode, self).__init__(
            "Go To Target")
        self.tsh = tsh

    def setup(self):
        return

    def initialise(self):
        return

    def update(self):

        obj = self.tsh.control.last_obj

        if False:
            self.feedback_message = "Ball is here!"
            return py_trees.common.Status.SUCCESS

        else:
            self.feedback_message = "Moving towards ball!"
            tmp = [x for x in self.tsh.control.last_cv if x['bbox_label']
                   == self.tsh.control.target]

            if len(tmp) == 0:
                self.feedback_message = "No such obstacle!"
                return py_trees.common.Status.FAILURE

            conf = np.array([x['bbox_confidence'] for x in tmp])
            idx = np.argmax(conf)
            best = tmp[idx]
            center_x = best['bbox_x'] + best['bbox_w']/2
            if center_x < self.tsh.control.SCREEN_MID_X:
                self.tsh.control.turn_left()
            elif center_x > self.tsh.control.SCREEN_MID_X:
                self.tsh.control.turn_right()

            self.tsh.control.move_forward()
            self.tsh.control.current_target = best
            return py_trees.common.Status.RUNNING

    def terminate(self, new_status):
        return


class TurnAroundNode(py_trees.behaviour.Behaviour):
    """
    Primitive behavior that spins the robot around in a circle.
    """

    def __init__(self, tsh):
        super(TurnAroundNode, self).__init__(
            "Turn Around")
        self.tsh = tsh

    def update(self):
        #not implemented
        return


class WaitNode(py_trees.behaviour.Behaviour):
    """
    Primitive behavior that busy waits tick cycles until the ball is no longer seen.
    """

    def __init__(self, tsh):
        super(MeanderNode, self).__init__(
            "Wait")
        self.tsh = tsh

    def update(self):
        #not implemented
        return
