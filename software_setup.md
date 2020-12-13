---
layout: template
---
# Starting from a brand new Raspberry Pi 4
To start setting up the robot, I recommend plugging the raspberry pi into USB 3 power and a monitor, keyboard and mouse. This will make initial setup *much* easier.

To start with, you will need to install the lastest Raspberry Pi OS (Raspbian Buster) onto a fresh SD card. And you can follow the basic raspberry Pi [setup instructions](https://projects.raspberrypi.org/en/projects/raspberry-pi-setting-up).

## To connect to eduroam
An important note is that the newest Raspbian OS (Raspbian Buster) has issues
connecting to Brandeis's eduroam network. In order to get eduroam to connect
you must run the
[downgrade_wpa_supplicant.sh](https://github.com/nubs01/PupperPy/blob/master/pupperpy/resources/downgrade_wpa_supplicant.sh)
script, and then setup the eduroam network credentials in the wpa_supplicant
file. As such, the easiest way to get started is to put the
[downgrade_wpa_supplicant.sh](https://github.com/nubs01/PupperPy/blob/master/pupperpy/resources/downgrade_wpa_supplicant.sh)
and
[wpa_supplicant.conf](https://github.com/nubs01/PupperPy/blob/master/pupperpy/resources/wpa_supplicant.conf)
files onto a USB drive. Then you can boot up the raspberry pi with your SD card and after the initial setup:
* open a terminal
* cd to the usb drive: `cd /media/pi/name_of_usb/`
* downgrade wpa_supplicant: `sudo bash downgrade_wpa_supplicant.sh`
* add robotics eudroam credential: `sudo cp wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf`

Now when you reboot the pi, it should automatically connect to eduroam. If using a different wireless network, you will have to add it to `/etc/wpa_supplicant/wpa_supplicant.conf` manually.
 
## Setting up Cerbaris
Now that you have internet access you can clone the
[PupperPy](https://github.com/nubs01/PupperPy) repository and follow along in
the
[setup_script.sh](https://github.com/nubs01/PupperPy/blob/master/pupperpy/setup_script.sh).

I recommend creating a folder in your home folder for all of your code so as not to pollute the home directory. For our project this was the `pupper_code` folder.

*DO NOT* run the setup script. It is not designed to be executed. Instead
simply follow along and run each line or block of code as needed. The important
steps are:
* (optional) change username & hostname
* enable ssh, camera via raspi-config
* install all necessary software and python packages
* grab all necessary git repositories
* setup network interfaces for use with UDPComms
* edit `/boot/config.txt` for I2C communication and camera settings
* install pi gpio daemon
* run installs for the git repositories
* (optional) make symlinks for services
  * required for basic PS4 control of pupper
  * not needed for our autonomous control

## Running Cerbaris
Once setup is complete and you have installed the PuppyPy package through pip:
```bash
cd /path/to/PupperPy
pip install -e pupperpy
```

You can now run the robot and all necessary processes with one command:
```bash
sudo python3 /path/to/PupperPy/pupperpy/run_cerbaris.py
```
After running this line you can connect the PS4 controller by holding the power and share buttons simultaneously until you see a double-blinking white light. The light will turn green when connected.

* To activate the robot press the Left Bumper (L1).
* To stop to robot press the Left Trigger (L2).
* You can monitor the status of the robot on the web interface at https://cerbaris.netlify.app

## Creating new behaviors
The control class provides a easy framework for creating and implementing new behaviors.
All you need to do is inherit the Control class and override the update_behavior function.
```python
from pupperpy.CommandInterface import Control

class NewControl(Control):
    def __init__(self, target='tennis_ball'):
        super().__init__(target=target)
        self.hokey_pokey_ticks = 0
        self._last_turn = None

    def update_behavior(self):
        obj, pos, cv = self.get_sensor_data()
        if self.hokey_pokey_ticks > 0 & self.hokey_pokey_ticks < 300:
            self.do_the_hokey_pokey()
            return
        elif self.hokey_pokey_ticks >= 300:
            self.turn_stop()
            self.move_forward()
            return

        if obj['left']:
            self.hokey_pokey_ticks = 0
            self.do_the_hokey_pokey()

    def do_the_hokey_pokey(self):
        if self._last_turn is None:
            self.turn_left()
            self._last_turn = 'left'
            self.hokey_pokey_ticks += 1
            return

        if self.hokey_pokey_ticks % 40 == 0:
            if self._last_turn == 'left':
                self.turn_right()
                self._last_turn = 'right':
            else:
                self.turn_left()
                self._last_turn = 'left'

        self.hokey_pokey_ticks += 1
```

Now you just make a copy of run_cerbaris.py and change put your new class in
place of `Control()`
        
