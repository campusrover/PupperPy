---
layout: template
---
# Build/Assembly

We recieved a parts kit from COMPANY_NAME_HERE which came with the full set of
parts and tools needed to build robot. Assembly was fairly straightforward and
generally followed the official [Pupper build
guide](https://pupper.readthedocs.io/en/latest/) except as noted below. Our
inital build took roughly 10 hours, though later, an almost complete teardown
and rebuild took less than 4 hours. A huge part of this change in assembly time
was simply having a second hex screwdriver that fit the M3 button head screws.

## Build Notes and Deviations from the guide
- When setting the servos to their neutral position, keep in mind that the
  servos rotate slightly over 180 deg. As such it is difficult to set them to
  exactly neutral. Regardless, what is most important is to come up with a method
  for determining neutral and then being consistent on all motors. 
- When attaching the metal disks to the servos, use the M3x6 __socket__ head screws.
- When attaching the carbon fiber leg pieces to the servos, use the M3x6 __button__ head screws.
- To attach the upper leg extension (the silver threaded rod / hamstring), use
  the M3x10 button head screws and the locknuts on both the upper and lower
  connections (not just the lower). 
- For body assembly step 3, there are no M4x8 plastic screws, instead use the M4x10 screws
- For body assembly step 4, it says to use M3x6 screws, but instead use M3x8
- To attach the top and bottom plates, use M3x8 screws instead of M3x6 
- The 3D printed plate with the tiny slit cutout is the back of the robot, the
  solid plate is the front of the robot.
- When mounting the legs onto the middle 3D pritned body parts, be very careful
  about orientation. If those plates are mounted backwards then the screw holes
  will not line up with the top and bottom plates. 

## Battery & Charging
The pupper came with a 5200mAh 2S LiPo Battery. To properly charge the battery we used the LiPo battery charger in LiPo Balance Charge mode with 5.2A current and 7.4V(2S). On the machine, simply plugin the yellow and white connectors on the battery and scroll to the LiPo balance charge setting and press play. It should auto-detect the appopriate settings and simply ask you to confirm. You can use the +/- button to change the setting and hold play to confirm. It will then ask you to confirm the 2S charge rate and then it will charge.

From fully depleted the battery was able to charge in about 45 minutes. A full charge can power the robot and all peripherals for roughly 1.5-2hrs.

# Repairs

## First damage
Once while calibrating the right front leg ran into and got stuck on a usb
cable plugged into the pupper. Since the leg continued to try and go to the
position it was told to, extreme strain was placed on the green metal spacers
connecting the inner and outer hip casings. These 3D pritned parts cracked and
we had to get new ones and swap them out. 

## Next damage
After this was repaired we let the pupper run autonomously for ~45min. During
this time we noticed the pupper getting lower and lower to the ground over
time, especially in the front. When we stopped operation we noticed that cracks
had appeared around the same screw holes but now on 3 separate hips. On this
occasion the robot never crashed or collapsed and there was nothing obstructing
leg movement. Our best guess is that during operation, the button head screws
between the inner and outer leg motors loosened and began to hit each other.
Also brittleness or weakness of the PLA 3D printed parts may simply be unable
to handle to movement of the robot for exteded periods of time.

We repalced all of the hips with nylon 3D pritned parts with slightly thicker
walls, and now the robot is very stable. The new parts seem both more durable
and more flexible than the previous parts. 

# Sensors

Here is the a connection diagram for attaching the IMU and object sensors to the raspberry pi.
![Sensor Connection Diagram](/figures/Pupper_Peripherals_Layout.png)

## Intertial Measurement Unit (IMU)
We chose to install a 9-DOF IMU in hopes of accurately tracking orientation and
position. To this end we used the [Adafruit BNO055 Absolute Orientation
Sensor](https://www.adafruit.com/product/2472?gclid=CjwKCAiAq8f-BRBtEiwAGr3DgSWEaPsjRwxAkKPiMBIgWYkN3LRUsc1ZK5mTCsGi_OcU1QQbBcek1xoC6CcQAvD_BwE)
which boasts on-board sensor fusion. This means that this unit already takes
sensor readings from the gyroscope, accelerometers and magnetometer and
appropriately rotates the data to provide euler angles relative to magnetic
north and linear acceleration values with gravity already removed. 

