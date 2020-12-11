---
layout: template
---
# Basic Pupper Software
The Pupper robot operates by using a PS4 controller to send commands to the robot via bluetooth.To do this it utilizes the following 4 repositories from Stanford Robotics Club:
- [StanfordQuadruped](https://github.com/stanfordroboticsclub/StanfordQuadruped)
- [Pupper Command](https://github.com/stanfordroboticsclub/PupperCommand)
- [PS4Joystick](https://github.com/stanfordroboticsclub/PS4Joystick)
- [UDPComms](http://github.com/stanfordroboticsclub/UDPComms)

## UDPComms
This package is central to how the robot communicates between asynhronously running parallel processes. This package functions through the use of [Sockets](https://docs.python.org/3/library/socket.html) and functions by setting up Server (`UDPComms.Publisher`) and Client (`UDPComms.Subscriber`) sockets on a local ethernet port facilitating one-way communication. Both the Publisher and Subscriber must be created before a message is sent or read, and if either end of the communication path is closed then both must be re-created.
To use UDPComms, the local ethernet, eth0, must be set to static IP 10.0.0.255. 

Example usage of UDPComms:
```python
from UDPComms import Publisher, Subscriber, timeout
pub = Publisher(1234)
sub = Subscriber(1234)

msg = {'name': 'John', 'height': 172}
pub.send(msg)
msg2 = {'name': 'Mary', 'height': 160}
pub.send(msg)

try:
    recevied = sub.get()
except timeout:
    received = None
```
The above code would result in `received` being `{'name': 'Mary', 'height': 160}` since that was the last message sent. The Publisher adds messages to a first-in-last-out stack and the Subscriber pops the top message from the stack. Calling `sub.get()` again would return John's information. UDPComms sends messages by first converting them to bytes, so any object that can be reliably converted into bytes can be sent via UDPComms.

## PS4Joystick
This library handles connection and communcation with a PS4 controller via bluetooth. This is handled through the `Joystick` object which when instantiated will wait for a PS4 controller to connect. The PS4 controller can be paired by holding the share and power buttons at the same time until you see a double-blinking white light. 

Example:
```python
from PS4Joystick import Joystick
joystick = Joystick()
joystick.led_color(red=0, blue=0, green=255)
values = joystick.get_input()
```
The `get_input()` command will return a dictionary representing the current state of the controller. 

Keys:
- left_analog_x
- left_analog_y
- right_analog_x
- right_analog_y
- l2_analog
- r2_analog
- button_r1
- button_r2
- button_square
- button_cross
- button_circle
- button_triangle
- dpad_right
- dpad_left
- dpad_up
- dpad_down

## PupperCommand
This repository houses the `joystick.py` script which run a loops that periodically queries the PS4 joystick and reformats the command to send to the Pupper robot command loop via UDPComms channel 8830. This can be run directly as python script or via a UNIX background service. 

## StanfordQuadruped
This project contains the code that actually controls to robot's movement,
chooses it's gait and behavior and sends PWM signals to the servos. This is all
carried out by the execution of the `run_robot.py` script. This script
initalizes and maintains 4 important objects:
- a `State` object which keeps track of the Pupper's behavioral_state (REST,
  TROT, HOP, FINSIHHOP, or DEACTIVATED), orientation, velocity, foot locations
  and joint angles
- a `JoystickInterface` which reads command input from UDP channel 8830 which
  should be coming form the __PupperCommand__ `joystick.py` script.
- a `Conrtoller` which uses the current state and command input to compute the
  next joint angles for the robot and update the State object.
- a `HardwareInterface` which gets the joint angles from the state object and
  sets the servos to those angles. 

This process can be run directly as a python script or run as a background unix
service. See [Softwar Setup](software_setup.md) to see how to setup and run
this.