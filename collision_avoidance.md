---
layout: template
---
# Collision Avoidance
For this project we chose to use 3 front mounted IR object sensors. These sensors switch from HIGH to LOW when an object is detected. They can detect objects up to 30cm though some objects do not reflect IR well and thus have a much shorter detection range (such as black plastic cabinets). The detection range can be tuned by a screw on the back of each sensors. 

## Hardware Interface
The hardware communcation is achieved through the `pigpio` package. For ease of use the `pupperpy.object_detection.ObjectSensors` object can be instatiated to quickly and easily grad sensor data.
```python
from pupperpy.object_detection import ObjectSensors

sensors = ObjectSensors()
sensors.read() # returns dict with keys 'left', 'right' and 'center' which have
               # boolean values
```

## Current Usage
The current Control flow uses this information to avoid collisions by simply turning away from any detected objects. If the object is only on the left or right sensor then the robot continues moving forward while turning, but if the object is also present on the center sensor -- or only present on the center sensors--- then the robot stops and turns until the object is no longer detected. 

## Moving Forward
Going forward object avoidance can be made much smarter. The simplest and
probably most useful improvement would be to turn back after dodging an object
that only appeared in only the left or right sensor, this way it would acutally
go around and object and not just turn and walk off in an awkward direction,
possibly completely losing track of a previously tracked target. Additionally,
heading information could be used from the IMU to help relocalize a target that
was lost by a suddenly appearing obstacle.

One weakness of the current sensor array is low obstacle that could trip the
robot -- such as the legs of rolly chairs. It may be better to mount the
sensors pointing at a slight downward angle so as to detect and avoid those. 
