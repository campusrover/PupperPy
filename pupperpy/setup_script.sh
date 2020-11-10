# change username to cerbaris
# be sure to disable auto-login in raspi-config
sudo adduser cerbaris
sudo usermod -a -G adm,dialout,cdrom,sudo,audio,video,plugdev,games,users,input,netdev,gpio,i2c,spi cerbaris
sudo -su cerbaris
sudo pkill -u pi
# Log back in as cerbaris if necessary
sudo deluser -remove-home pi

# Change hostname
sudo hostnamectl set-hostname cerbaris
sud nano /etc/hosts
## replace raspberrypi with cerbaris

# Enable ssh
## With raspbian, use sudo raspi-config to enable ssh
## With ubuntu, sudo apt-get install openssh-server

# Install basic software
sudo apt-get update
sudo apg-get upgrade
sudo apt-get install -y vim python3-pip build-essential libbluetooth-dev libatlas-base-dev libsdl-ttf2.0-0 git i2c-tools 
sudo pip3 install numpy pybluez ds4drv msgpack pexpect transforms3d pigpio pyserial ipython adafruit-circuitpython-bno055 picamera pandas pathlib dotenv pusher

# Git grabs
mkdir /home/cerbaris/pupper_code
cd pupper_code
git clone https://github.com/stanfordroboticsclub/StanfordQuadruped.git
git clone https://github.com/stanfordroboticsclub/PupperCommand.git
git clone https://github.com/stanfordroboticsclub/PS4Joystick.git
git clone http://github.com/stanfordroboticsclub/UDPComms.git
git clone https://github.com/stanfordroboticsclub/uDHCPd.git
git clone https://github.com/nubs01/PupperPy.git

# And grab and install pigpio (the StanfordQuadruped install uses pigpio-v74,
# no idea why but it doesn't work with ubuntu, master should work with all
wget https://github.com/joan2937/pigpio/archive/master.zip
unzip master.zip
cd pigpio-master
make
sudo make install
cd ..

# Now install the pupper code
sudo pip3 install -e UDPComms
sudo bash uDHCPd/install.sh

# Setup symlinks and services
# go to PupperCommand/joystick.service and StanfordQuadruped/robot.service and change the paths to match your configuration
sudo ln -s $(realpath .)/StanfordQuadruped/robot.service /etc/systemd/system/
sudo ln -s $(realpath .)/PupperCommand/joystick.service /lib/systemd/system/
sudo ln -s $(realpath .)/UDPComms/rover.py /usr/local/bin/rover
sudo ln -s $(realpath .)/PupperPy/pupperpy/resources/pupperble.service /lib/systemd/system/
sudo ln -s $(realpath .)/PupperPy/pupperpy/resources/robotble.service /etc/systemd/system/

# enable services
sudo systemctl daemon-reload
sudo pigpiod

#### For PS4 Controller ###
sudo systemctl enable joystick
sudo systemctl enable robot
sudo systemctl start joystick
sudo systemctl start robot

### For Bluetooth from computer ###
#sudo systemctl enable pupperble
#sudo systemctl enable robotble
#sudo systemctl start pupperble
#sudo systemctl start robotble


# Enable eduroam
sudo bash PupperPy/pupperpy/resrouces/downgrade_wpa_supplicant.sh
sudo cp PupperPy/pupperpy/resources/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf


# Setup network insterfaces for use with UDPComms
cat PupperPy/pupperpy/resources/network_interfaces_extra.txt | sudo tee -a /etc/network/interfaces

# Configurations for IMU and Camera
# Change to /boot/firmware/config.txt for ubuntu mate
# IMU must be connected like this: Vin: 3.3V, GND: GND, SDA: GPIO_0, SCL:
# GPIO_1, RST: GPIO_16 (or any open GPIO, set to high, pulse low to reset)
cat PupperPy/pupperpy/resources/config_extra.txt | sudo tee -a /boot/config.txt

################################################################################
################    IMU and Camera Setup    ######################
################################################################################

# # Edits to /boot/config.txt (raspbian) or /boot/firmware/config.txt (ubuntu)
# ### For Camera
# start_x=1
# gpu_mem=128
# ### For IMU (BNO055) on GPIO 0 (SDA) & 1 (SCL)
# dtparam=i2c_arm=on,ic2_arm_baudrate=10000
# dtparam=i2c1=off
# dtparam=i2c0=on


# ################################################################################
# ################    Bluetooth Computer Interface Setup    ######################
# ################################################################################
#
# # Installing stuff
# sudo apt-get install libbluetooth-dev
# sudo pip install pybluez
# # techincally the root install is enough, but this lets you use it in ipython too
# pip install pybluez
#
# # Now enable bluetooth, this needs to be done everytime the interface is
# # used, still looking for an autoconnect
# bluetoothctl
# # Coppy the shown MAC address, put this into the file pupperpy/BluetoothInterface.py
# enable on
# pairable on
# discoverable on
# # Now find and pair cerbaris from your computer, and here a prompt will pop up to accept it
# # then exit bluetoothctl
# exit
#
# # Now setup the services
# ln -s /home/cerbaris/pupper_code/pupperpy/pupperpy/resources/pupperble.service /lib/systemd/system/
# ln -s /home/cerbaris/pupper_code/pupperpy/pupperpy/resources/robotble.service /etc/systemd/system/
# # Disable other services (alternatively you could just 'stop' them, I think
# # after disabling you have to relink them to use them again)
# # TODO: put aliases in bash_aliases to switch between the control modes
# sudo systemctl disable joystick
# sudo systemctl disable robot
# # Reload the daemon and start the new services
# sudo systemctl enable pupperble
# sudo systemctl enable robotble
# sudo systemctl start pupperble
# sudo systemctl start robotble

##############################################################################
######################### Camera and Coral TPU ###############################
##############################################################################
#
# Before continuing:
# 1. Turn off the pi
# 2. Install the Raspberry pi camera v2 into the raspberry pi camera slot
# 3. Turn the pi back on
#
# Install Edge TPU runtime
echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list

curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -

sudo apt-get update

sudo apt-get install libedgetpu1-std

# Install TensorFlow Lite library
pip3 install https://dl.google.com/coral/python/tflite_runtime-2.1.0.post1-cp37-cp37m-linux_armv7l.whl

# Install OpenCV
sudo apt-get install libhdf5-dev libhdf5-serial-dev libhdf5-103 libjasper-dev libavcodec-dev libavformat-dev libswscale-dev libqtgui4 libqt4-test

pip3 install opencv-contrib-python==4.1.0.25


