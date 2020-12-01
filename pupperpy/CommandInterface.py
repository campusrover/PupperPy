from pupperpy.imu_tools import IMU
from pupperpy.position import PositionTracker
from pupperpy.daq_tools import RepeatTimer
from pupperpy.ControllerState import ControllerState
from pupperpy.object_detection import ObjectSensors
from pupperpy.PusherInterface import PusherClient
from UDPComms import Publisher, Subscriber, timeout
import numpy as np
from PS4Joystick import Joystick
import time

MESSAGE_RATE = 20
CMD_PUB_PORT = 8830
CMD_SUB_PORT = 8840
CV_SUB_PORT = 105
PUPPER_COLOR = {"red":0, "blue":0, "green":255}

class Control(object):
    STATES = ['off', 'rest', 'meander', 'goto', 'avoid']
    SCREEN_MID_X = 150
    def __init__(self, target='tennsi_ball'):
        self.timer = RepeatTimer(1/MESSAGE_RATE, self._step)
        self.control_state = ControllerState()
        self.pos = PositionTracker(self.control_state)
        self.obj_sensors = ObjectSensors()
        self.active = False
        self.walking = False
        self.user_stop = False
        self.cmd_pub = Publisher(CMD_PUB_PORT)
        self.cmd_sub = Subscriber(CMD_SUB_PORT)
        self.cv_sub = Subscriber(CV_SUB_PORT)
        self.joystick = Joystick()
        self.joystick.led_color(**PUPPER_COLOR)
        self.state = 'off'
        self.target = target
        self.current_target = None
        self.pusher_client = PusherClient()

    def move_forward(self, vel=ControllerState.LEFT_ANALOG_Y_MAX):
        self.control_state.left_analog_y = vel

    def move_backward(self, vel=-ControllerState.LEFT_ANALOG_Y_MAX):
        self.control_state.left_analog_y = vel

    def move_stop(self):
        self.control_state.left_analog_y = 0

    def turn_right(self, rate=ControllerState.RIGHT_ANALOG_X_MAX):
        self.control_state.right_analog_x = rate

    def turn_left(self, rate=-ControllerState.RIGHT_ANALOG_X_MAX):
        self.control_state.right_analog_x = rate

    def turn_stop(self):
        self.control_state.right_analog_x = 0

    def start_walk(self):
        if self.walking or not self.active:
            return

        self.reset()
        self.control_state.r1 = True
        self.toggle_cmd()
        self.walking = True
        self.control_state.walking = True
        self.reset()

    def activate(self):
        if self.active:
            return

        self.reset()
        self.control_state.l1 = True
        self.toggle_cmd()
        self.reset()

        self.active = True
        self.state = 'rest'
        self.walking = False
        self.control_state.walking = False
        if not self.pos.running:
            self.pos.run()

    def stop_walk(self):
        if not self.walking:
            return

        self.reset()
        self.control_state.r1 = True
        self.toggle_cmd()
        self.walking = False
        self.control_state.walking = False
        self.reset()
        self.state = 'rest'

    def reset(self):
        self.control_state.reset()

    def run_loop(self):
        self.timer.start()

    def stop_loop(self):
        self.timer.cancel()
        self.reset()
        self.stop_walk()
        self.pos.stop()
        self.active = False
        self.send_cmd()
        self.user_stop = True

    def toggle_cmd(self):
        # For toggle commands, they should be sent several times to ensure they
        # are put into effect
        for _ in range(3):
            self.send_cmd()
            time.sleep(1/MESSAGE_RATE)

    def send_cmd(self):
        cmd = self.control_state.get_state()
        self.cmd_pub.send(cmd)
        try:
            msg = self.cmd_sub.get()
            self.joystick.led_color(**msg["ps4_color"])
        except timeout:
            pass

    def _step(self):
        js_msg = self.joystick.get_input()
        
        # Force stop moving
        if js_msg['button_l2']:
            self.user_stop = True
            self.stop_walk()
            return

        # User activate
        if js_msg['button_l1']:
            self.user_stop = False
            self.activate()
            return

        if self.user_stop or not self.active:
            self.reset()
            self.send_cmd()
            return

        if not self.walking:
            self.start_walk()
            return

        # grab data
        obj = self.obj_sensors.read()
        pos = self.pos.data
        try:
            cv = self.cv_sub.get()
        except timeout:
            cv = []

        if any(obj.values()):
            # If object, dodge
            self.state = 'avoid'
            self.dodge(obj)
        elif any([x['bbox_label'] == self.target for x in cv]):
            # if target, chase
            self.state = 'goto'
            self.goto(cv)
        else:
            # if nothing, wander
            self.state = 'meander'
            self.meander()

        print(str(time.time()) +': ' + self.state)
        self.send_cmd()
        self.send_pusher_message(pos, obj, cv)

    def dodge(self, obj):
        '''Takes the object sensor data and adjusts the command to avoid any
        objects
        '''
        if obj['left'] and obj['right']:
            self.move_stop()
            self.turn_right()
        elif obj['left']:
            self.turn_right()
        elif obj['right']:
            self.turn_left()
        elif not any(obj.values()):
            self.turn_stop()

    def meander(self):
        '''moves forward and makes slight turns left and right to search for a
        target -- eventually, for now just move forward
        '''
        self.current_target = None
        self.move_forward()

    def goto(self, cv):
        '''takes a list of bounding boxes, picks the most likely ball and moves
        toward it
        '''
        tmp = [x for x in cv if x['bbox_label'] == self.target]
        if len(tmp) == 0:
            self.meander()

        conf = np.array([x['bbox_confidence'] for x in tmp])
        idx = np.argmax(conf)
        best = tmp[idx]
        center_x = best['bbox_x'] + best['bbox_w']/2
        if center_x < self.SCREEN_MID_X:
            self.turn_left()
        elif center_x > self.SCREEN_MID_X:
            self.turn_right()

        self.move_forward()
        self.current_target = best

    def send_pusher_message(self, pos, obj, cv):
        bbox = self.current_target
        timestamp = time.time()
        if bbox is None:
            bbox = {'bbox_x': np.nan,
                    'bbox_y': np.nan,
                    'bbox_h': np.nan,
                    'bbox_w': np.nan,
                    'bbox_label': '',
                    'bbox_confidence': np.nan}

        message = {'time': timestamp,
                   'x_pos': pos['x'],
                   'y_pos': pos['y'],
                   'x_vel': pos['x_vel'],
                   'y_vel': pos['y_vel'],
                   'x_acc': pos['x_acc'],
                   'y_acc': pos['y_acc'],
                   'yaw': pos['yaw'],
                   'yaw_rate': pos['yaw_rate'],
                   'left_sensor': obj['left'],
                   'center_sensor': obj['center'],
                   'right_sensor': obj['right'],
                   'state': self.state,
                   **bbox}

        self.pusher_client.send(message)

if __name__ == "__main__":
    control = Control()
    control.run_loop()
