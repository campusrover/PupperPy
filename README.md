# PupperPy
Software for the control and management of the Stanford Pupper Robot

*This readme is behind. Please find more complete documentation [here](https://campusrover.github.io/PupperPy/)*

## Install Notes For Laptop Bluetooth controller
- in order to install pybluez you may first need to install libbluetooth-dev
    - `sudo apt-get install libbluetooth-dev`
- for PyQt you need (Only for keyboard interface, not needed on pupper):
    - sudo apt-get install python3-pyqt5 pyqt5-dev-tools qttools5-dev-tools


## Setup of Cerbaris Robot Code
The simplest way to setup the robot is to clone this github repo onto a USB and
copy it onto a raspberry pi 4 running a fresh install of Raspbian Buster. I
recommend creating a code folder in the home folder and then housing all of the
required code in there. For our build this folder was named pupper_code.

At first, you can simply open the file PupperPy/pupperpy/setup_script.sh
directly from the usb and following along. DO NOT run the setup_script, it is
not designed to be run. Instead treat it as a bunch of runnable code segements
and guiding comments to allow a few different setup configurations. Just
copy-pasta what you need into a terminal one line or block at a time.

# Automated Cerbaris Control
## Updated Usage
Though the below methods can still be used, a simpler but less versatile usage is to pip install the pupperpy package:
```bash
cd /your/path/to/PupperPy
sudo pip3 install -e pupperpy
```
and now you can startup all processes with one command:
```bash
sudo python3 /your/path/to/PupperPy/pupperpy/run_cerbaris.py
```
and then connecting your PS4 controller. Now cerbaris is ready to run. Just hit the L1 button to activate. L2 can be used to emergency stop the pupper, with L1 being able to re-activate.

## Usage
The automated control system is located in the pupperpy/CommandInterface.py
file. Currently control of the pupper is done using the
CommandInterface.Control object and the cerbaris_robot service, which simply
runs StandfordQuadrupped/run_robot.py.

When instantiated the Control object connects to a PS4 controller (for
activation and emergency stop). Also this creates instances of the objects
monitoring sensor data as well as UDPComms Subscribers & Publishers for getting
data from the pupper_vision.py script (can be run via the pupper_vision service
or called directly in terminal).

*In Terminal,*
```bash
cd /your/path/to/PupperPy
sudo ipython
```
*In IPython,*
```python
from pupperpy.CommandInterface import Control
control = Control()
```
    When prompted connect the PS4 controller by holding the power and "share"
    buttons simultaneously until you see a double-blinking white light. When the
    light turns green then the controller is connected to the robot.

The control loop functions by maintaining a ControllerState object and sending
it to the run_robot script ~every 50ms. This is important since the
PositionTracker has a pointer to this same object since it needs to know the
current command state to update the Kalman filter. This means that if you ever
re-instantiate the ControllerState object during your behaviors then the
PositionTracker will be unable to know what commands are controlling the robot.

After instantiating the Control object and connecting the PS4 controller, the
cerbaris_robot and pupper_vision services can be started (starting these before
Control object creation may cause them to error).

*In another Terminal,*
```bash
sudo python3 /your/path/to/PupperPy/pupperpy/Vision/pupper_vision.py &
sudo systemctl restart cerbaris_robot
```

Then the Control object can be run.

*In IPython,*
```python
control.run_loop()
```

This will start a timer that calls the `control._step()` function approximately
every 50 ms. To activate the robot you can either press the L1 button on the
PS4 controller, or use the `control.activate()` command in IPython.

The `_step()` function uses the sensors data to determine the appropriate
behavioral state and then calls a function to properly manipulate the
ControllerState object.

To help with implementation of behaviors the Control object has some built in
functions that can be used to build behaviors.
```python
control.move_forward()  # moves forward at max safe velocity
control.move_backward() # moves backward at max safe velocity
control.move_stop()     # stops forward and backward movement

control.turn_left()     # turns left
control.turn_right()    # turns right
control.turn_stop()     # stops turning

control.activate()      # Activates robot, initializes motor positions
control.start_walk()    # switches robot gait from REST to TROT
control.stop_walk()     # switches robot gait from TROT to REST
```

## Systems: Setup, Function and Progress
### Sensors

### Position Tracking

### Pupper Vision

### Cerbaris Web Monitor

### Decision Trees
