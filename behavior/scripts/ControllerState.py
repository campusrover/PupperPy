import numpy as np


class ControllerState(object):
    LEFT_ANALOG_X_STEP = 0.05
    LEFT_ANALOG_Y_STEP = 0.05
    RIGHT_ANALOG_X_STEP = 0.05
    RIGHT_ANALOG_Y_STEP = 0.05
    DPAD_X_STEP = 1
    DPAD_Y_STEP = 1

    LEFT_ANALOG_X_MAX = 0.20
    LEFT_ANALOG_Y_MAX = 0.6
    RIGHT_ANALOG_X_MAX = 0.5
    RIGHT_ANALOG_Y_MAX = 0.6
    DPAD_X_MAX = 1
    DPAD_Y_MAX = 1

    def __init__(self):
        self.left_analog_x = 0
        self.left_analog_y = 0
        self.right_analog_x = 0
        self.right_analog_y = 0
        self.dpad_x = 0
        self.dpad_y = 0
        self.l1 = False
        self.l2 = False
        self.r1 = False
        self.r2 = False
        self.square = False
        self.circle = False
        self.cross = False
        self.triangle = False

    @property
    def left_analog_x(self):
        return self._left_analog_x

    @left_analog_x.setter
    def left_analog_x(self, value):
        if np.abs(value) > self.LEFT_ANALOG_X_MAX:
            self._left_analog_x = np.sign(value)*self.LEFT_ANALOG_X_MAX
        else:
            self._left_analog_x = value

    @property
    def left_analog_y(self):
        return self._left_analog_y

    @left_analog_y.setter
    def left_analog_y(self, value):
        if np.abs(value) > self.LEFT_ANALOG_Y_MAX:
            self._left_analog_y = np.sign(value)*self.LEFT_ANALOG_Y_MAX
        else:
            self._left_analog_y = value

    @property
    def right_analog_x(self):
        return self._right_analog_x

    @right_analog_x.setter
    def right_analog_x(self, value):
        if np.abs(value) > self.RIGHT_ANALOG_X_MAX:
            self._right_analog_x = np.sign(value)*self.RIGHT_ANALOG_X_MAX
        else:
            self._right_analog_x = value

    @property
    def right_analog_y(self):
        return self._right_analog_y

    @right_analog_y.setter
    def right_analog_y(self, value):
        if np.abs(value) > self.RIGHT_ANALOG_Y_MAX:
            self._right_analog_y = np.sign(value)*self.RIGHT_ANALOG_Y_MAX
        else:
            self._right_analog_y = value

    @property
    def dpad_x(self):
        return self._dpad_x

    @dpad_x.setter
    def dpad_x(self, value):
        if np.abs(value) > self.DPAD_X_MAX:
            self._dpad_x = np.sign(value)*self.DPAD_X_MAX
        else:
            self._dpad_x = value

    @property
    def dpad_y(self):
        return self._dpad_y

    @dpad_y.setter
    def dpad_y(self, value):
        if np.abs(value) > self.DPAD_Y_MAX:
            self._dpad_y = np.sign(value)*self.DPAD_Y_MAX
        else:
            self._dpad_y = value

    def increment(self, attr):
        try:
            x = getattr(self, attr)
            step = getattr(self, (attr + '_step').upper())
            x += step
            setattr(self, attr, round(x, 4))
        except:
            print('Attribute %s not found.' % attr)

    def decrement(self, attr):
        try:
            x = getattr(self, attr)
            step = getattr(self, (attr + '_step').upper())
            x -= step
            setattr(self, attr, round(x, 4))
        except:
            print('Attribute %s not found.' % attr)

    def get_state(self):
        out = {}
        out['left_analog_x'] = self.left_analog_x
        out['left_analog_y'] = self.left_analog_y
        out['right_analog_x'] = self.right_analog_x
        out['right_analog_y'] = self.right_analog_y
        out['dpad_x'] = self.dpad_x
        out['dpad_y'] = self.dpad_y
        out['l1'] = self.l1
        out['l2'] = self.l2
        out['r1'] = self.r1
        out['r2'] = self.r2
        out['button_square'] = self.square
        out['button_circle'] = self.circle
        out['button_triangle'] = self.triangle
        out['button_cross'] = self.cross
        return out

    def __str__(self):
        return repr(self.get_state())
