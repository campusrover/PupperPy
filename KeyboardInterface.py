from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys
import os
import configparser
import tkinter as tk
from tkinter import ttk
from pupperpy.Controller.Controller_QT import Ui_MainWindow
import time
from pupperpy.BluetoothInterface import BluetoothClient
from pupperpy.CommandInterface import ControllerState


__location__ = os.path.dirname(__file__)
RESOURCE_DIR = os.path.join(__location__, 'pupperpy', 'resources')
KEY_CONFIG = os.path.join(RESOURCE_DIR, 'keyboard_mapping.conf')
MESSAGE_RATE = 20
PUPPER_COLOR = {"red":255, "blue":0, "green":0}
RESET_KEY = Qt.Key_Space
EXIT_KEY = Qt.Key_Escape


def launch_pupper_controller():
    app = QApplication(sys.argv)
    cgi = ControlGUI()
    sys.exit(app.exec_())


def load_keymap(keymap=KEY_CONFIG):
    config = configparser.ConfigParser()
    config.read(keymap)
    out_map = {}
    for k1, v1 in config.items():
        for k2, v2 in v1.items():
            if v2 == '':
                continue

            key = QKeySequence(v2)[0]
            out_map[key] = (k1, k2)

    return out_map

class DummyBLE(object):
    def __init__(self):
        pass
    def send(self, msg):
        pass
    def recv(self):
        return None
    def close(self):
        pass

class ControlGUI(QMainWindow):
    '''This will start a keyboard listener and display the controller state. It
    will loop and poll the listener for controller state, then send the state
    on to the raspberry pi via Bluetooth, will also check for a response from
    the pi
    '''
    def __init__(self, *args, **kwargs):
        if 'keymap' in kwargs:
            keymap = kwargs.pop('keymap')
        else:
            keymap = KEY_CONFIG

        super(ControlGUI, self).__init__(*args, **kwargs)
        #window_center(self.root)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.state = ControllerState()
        self.pupper_color = PUPPER_COLOR
        self.active = False

        self.config = load_keymap(keymap)
        self.updateUI()

        #self.ble_interface = BluetoothClient()
        self.ble_interface = DummyBLE()
        self.timer = QTimer()
        self.timer.setInterval(1000 / MESSAGE_RATE)
        self.timer.timeout.connect(self.send_signal)
        self.timer.start()

        self.show()

    def keyPressEvent(self, event):
        key = event.key()
        mapped = self.config.get(key)
        if key == EXIT_KEY:
            self.close()

        if key == RESET_KEY:
            self.state = ControllerState()
        elif mapped is None:
            return
        else:
            group, key_val = mapped
            if key_val == 'reset':
                self.state = ControllerState()
            elif key_val == 'quit':
                self.close()
            elif group == 'toggle':
                setattr(self.state, key_val, True)
            else:
                if key_val == 'increment':
                    self.state.increment(group)
                elif key_val == 'decrement':
                    self.state.decrement(group)
                else:
                    raise ValueError('Unknown keyword %s' % key_val)

        self.updateUI()

    def keyReleaseEvent(self, event):
        key = event.key()
        mapped = self.config.get(key)
        if mapped is None:
            return

        group, key_val = mapped
        if group is None or key_val is None:
            return

        if group == 'toggle':
            setattr(self.state, key_val, False)
        elif 'dpad' in group:
            # reset dpad values when reset, dpad must be 1 or -1 while pressed
            # and 0 otherwise
            if key_val == 'increment':
                self.state.decrement(group)
            elif key_val == 'decrement':
                self.state.increment(group)

        self.updateUI()
        print(self.state)

    @property
    def pupper_color(self):
        return self._pupper_color

    @pupper_color.setter
    def pupper_color(self, value):
        if value is None:
            return

        if not all([x in value.keys() for x in ['red', 'blue', 'green']]):
            raise ValueError('Invalid Color Message')

        self._pupper_color = value


    def updateUI(self, state=None, pupper_msg=None):
        if state is not None:
            self.state = state
        else:
            state = self.state

        if pupper_msg is not None:
            self.pupper_color = pupper_msg['ps4_color']

        state_dict = state.get_state()

        lx = state.left_analog_x
        ly = state.left_analog_y
        rx = state.right_analog_x
        ry = state.right_analog_y
        dx = state.dpad_x
        dy = state.dpad_y
        l1 = state.l1
        r1 = state.r1
        hop = state.cross

        if l1 and not self.active:
            self.active = True
            self.ui.active_label.setText('Active')

        r,g,b = (self._pupper_color[x] for x in ['red', 'green', 'blue'])
        self.ui.active_label.setStyleSheet("background-color: rgb(%i, %i, %i)"
                                           % (r,g,b))

        set_toggle(self.ui.gait_button, r1)
        set_toggle(self.ui.hop_button, hop)

        if dx > 0:
            set_toggle(self.ui.dpad_right, True)
            set_toggle(self.ui.dpad_left, False)
        elif dx < 0:
            set_toggle(self.ui.dpad_right, False)
            set_toggle(self.ui.dpad_left, True)
        else:
            set_toggle(self.ui.dpad_right, False)
            set_toggle(self.ui.dpad_left, False)

        if dy > 0:
            set_toggle(self.ui.dpad_up, True)
            set_toggle(self.ui.dpad_down, False)
        elif dy < 0:
            set_toggle(self.ui.dpad_up, False)
            set_toggle(self.ui.dpad_down, True)
        else:
            set_toggle(self.ui.dpad_up, False)
            set_toggle(self.ui.dpad_down, False)

        self.ui.left_x_slider.setValue(int(100 * lx / state.LEFT_ANALOG_X_MAX))
        self.ui.left_y_slider.setValue(int(100 * ly / state.LEFT_ANALOG_Y_MAX))

        self.ui.right_x_slider.setValue(int(100 * rx / state.RIGHT_ANALOG_X_MAX))
        self.ui.right_y_slider.setValue(int(100 * ry / state.RIGHT_ANALOG_Y_MAX))

    def send_signal(self):
        self.ble_interface.send(self.state.get_state())
        msg = self.ble_interface.recv()
        if msg is not None:
            self.pupper_color = msg['ps4_color']

    def closeEvent(self, event):
        self.active = False
        self.ble_interface.close()
        self.timer.stop()
        event.accept()


def set_toggle(obj, val):
    if obj.isChecked() != val:
        obj.toggle()


if __name__ == '__main__':
    launch_pupper_controller()
