from pynput import keyboard
import numpy as np
import sys
import os
import configparser

__location__ = sys.path[0]
KEY_CONFIG = os.path.join(__location__, 'keyboard_mapping.conf')
MESSAGE_RATE = 20
PUPPER_COLOR = {"red":0, "blue":0, "green":255}

# So on mac at least, holding down a key counts as repeated presses with no release, except shift and capslock those are only single
class Test(object):
        def __init__(self):
            self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
            self.last_key = None
            self.n = 0

        def on_release(self, key):
            if key == keyboard.Key.esc:
                print(key.name)
                return False  # stop listener
            else:
                try:
                    k = key.char
                    print('char: ' + k)
                except:
                    print('name: ' + key.name)

            self.n = 0

        def on_press(self, key):
            if key == self.last_key:
                self.n += 1
            else:
                self.n = 0

            self.last_key = key
            print(self.n)

        def run(self):
            self.listener.start()

        def join(self):
            self.listener.join()


class ControllerState(object):
    LEFT_ANALOG_X_STEP = 0.1
    LEFT_ANALOG_Y_STEP = 0.1
    RIGHT_ANALOG_X_STEP = 0.1
    RIGHT_ANALOG_Y_STEP = 0.1
    DPAD_X_STEP = 0.1
    DPAD_Y_STEP = 0.1

    LEFT_ANALOG_X_MAX = 1
    LEFT_ANALOG_Y_MAX = 1
    RIGHT_ANALOG_X_MAX = 1
    RIGHT_ANALOG_Y_MAX = 1
    DPAD_X_MAX = 1
    DPAD_Y_MAX = 1

    def __init__(self, keymap=KEY_CONFIG):
        self.left_analog_x = 0
        self.left_analog_y = 0
        self.right_analog_x = 0
        self.right_analog_y = 0
        self.dpad_x = 0
        self.dpad_y = 0
        self.l1 = 0
        self.l2 = 0
        self.r1 = 0
        self.r2 = 0
        self.square = 0
        self.circle = 0
        self.cross = 0
        self.triangle = 0

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

    @left_analog_x.setter
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
            step = getattr(self, (attr + _step).upper())
            x += step
            setattr(self, attr, x)
        except:
            print('Attribute %s not found.' % attr)

    def decrement(self, attr):
        try:
            x = getattr(self, attr)
            step = getattr(self, (attr + _step).upper())
            x -= step
            setattr(self, attr, x)
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
        out['l1'] = self.l1
        out['button_square'] = self.square
        out['button_circle'] = self.circle
        out['button_triangle'] = self.triangle
        out['button_cross'] = self.cross


class StateManager(object):
    def __init__(self, keymap=KEY_CONFIG):
        self.config = configparser.ConfigParser()
        self.config.read(keymap)
        self.state = ControllerState()
        self.listener = keyboard.Listener(on_press=self.on_press,
                                          on_release=self.on_release)

    def on_press(self, key):
        if key == keyboard.Key.esc:
            self.state = ControllerState() # set state to default
            return False  # stop Listener

        try:
            k = key.char
        except:
            k = key.name

        # if statements to match to keyboard_mapping and set correct variables
        group, key_val = None, None
        for k1, v1 in self.config.items():
            for k2, v2 in v1.items():
                if k == v2:
                    group = k1
                    key_val = k2
                    break
        if group is not None and group != 'toggle':
            if key_val == 'increment':
                self.state.increment(group)
            elif key_val == 'decrement':
                self.state.decrement(group)
            else:
                raise ValueError('Unknown keyword %s' % key_val)

        elif k == RESET_KEY:
            # reset key sends resets controller state to default
            self.state = ControllerState()

    def on_release(self, key):
        # handle toggles on release
        # if one is turned on, turn off all others
        if key == keyboard.Key.esc:
            self.state = ControllerState() # set state to default
            return False # stop listener

        try:
            k = key.char
        except:
            k = key.name

        group, key_val = None, None
        for k1, v1 in self.config.items():
            for k2, v2 in v1.items():
                if k == v2:
                    group = k1
                    key_val = k2
                    break

        if group is not None and group == 'toggle':
            for attr in config['toggle']:
                setattr(self.state, attr, 0)

            setattr(self.state, key_val, 1)
        elif k == RESET_KEY:
            # reset key sends resets controller state to default
            self.state = ControllerState()

    def get_state(self):
        '''returns dict with controller state information, ready to be passed to PupperBLE via bluetooth
        '''
        return self.state.get_state()

    def start(self):
        self.listener.start()

    def stop(self):
        self.listener.stop()

    def join(self):
        self.listener.join()

    def __enter__(self):
        self.listener.start()
        return self

    def __exit__(self, type, value, tb):
        self.state = ControllerState()
        self.listener.stop()


class ControlGUI(ttk.Frame):
    '''This will start a keyboard listener and display the controller state. It will loop and poll the listener for controller state, then send the state on to the raspberry pi via Bluetooth, will also check for a response from the pi
    '''
    def __init__(self, parent, state, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.root = parent
        self.root.style = ttk.Style()
        self.root.style.theme_use('clam')
        self.root.geometry('1024x720')
        self.pack(fill='both', expand=True)
        window_center(self.root)

        self.state = state
        self.pupper_color = PUPPER_COLOR
        self.initUI()

    def initUI(self):
        # Left analog x : y velocity, no its not a mistake, for some reason this is how its setup
        # Left analog y : x velocity

        # Right analog x: yaw rate
        # Right analog y: pitch

        # Dpad x: roll movement
        # Dpad y: height

        # R1: activate toggle
        # L1: gait toggle
        # cross: hop toggle

        # pupper color box

        # initialize layout and widgets then use update
        pass

    def update(self, state=None, pupper_msg=None):
        if state is not None:
            self.state = state

        if pupper_msg is not None:
            self.pupper_color = pupper_msg['ps4_color']
        pass

def launch_pupper_controller():
    # start a StateManager to grab keyboard input
    with StateManager() as listener:
        # create a GUI
        state = listener.get_state()
        root = tk.Tk()
        cgi = ControlGUI(state)
        # create a bluetooth interface
        ble_interface = BluetoothInterface() # TODO: Make This

        # first receive inital message from pupper
        msg = ble_interface.recv()
        cgi.update(pupper_msg=msg)

        # run loop to poll state from listener and then pass it to the pupper then listen to the pupper for any returned data, then pass both to gui for update

        active = True
        while active:
            state = listener.get_state()
            ble_interface.send(state)
            msg = ble_interface.recv()
            cgi.update(state, msg)
            time.sleep(1 / MESSAGE_RATE)
            pass


def window_center(win):
    win.update_idletasks()
    width = win.winfo_width()
    height = win.winfo_height()
    x = (win.winfo_screenwidth() // 2) - (width // 2)
    y = (win.winfo_screenheight() // 2) - (height // 2)
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))


if __name__ == '__main__':
    #listener = keyboard.Listener(on_press=on_press)
    #listener.start()
    test = Test()
    test.run()
    print('cats')
