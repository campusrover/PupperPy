#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import py_trees
import random


class LookForBallNode(py_trees.behaviour.Behaviour):
    def __init__(self, name):
        super(LookForBallNode, self).__init__(name)
        self.ball_found = False

    def __init__(self):
        super(LookForBallNode, self).__init__("Look For Ball")
        self.ball_found = False

    def setup(self):
        return

    def initialise(self):
        return

    def update(self):
        self.updateBallFound()
        if self.ball_found:
            self.feedback_message = "Ball found!"
            return py_trees.common.Status.SUCCESS
        else:
            self.feedback_message = "Still looking..."
            return py_trees.common.Status.RUNNING

    def terminate(self, new_status):
        return


class MoveTowardsBallNode(py_trees.behaviour.Behaviour):
    def __init__(self, name):
        super(MoveTowardsBallNode, self).__init__(name)
        self.ball_found = False

    def __init__(self):
        super(MoveTowardsBallNode, self).__init__("Move Towards Ball")
        self.ball_found = False

    def setup(self):
        return

    def initialise(self):
        return

    def update(self):
        self.updateBallFound()
        if self.ball_found:
            self.feedback_message = "Ball fetched!"
            return py_trees.common.Status.SUCCESS
        else:
            self.feedback_message = "On my way..."
            return py_trees.common.Status.RUNNING

    def updateBallFound(self):
        # update ball found
        pass

    def terminate(self, new_status):
        return
