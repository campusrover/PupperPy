---
layout: template
title: Introduction
---
As a team we set out to build the [Standford Pupper
robot](https://stanfordstudentrobotics.org/pupper) and see how far we could
extend the software, hardware and overall functionality of the system over the
course of a semester.

## Project Goals
We initally set out to create a robot that could freely move around an
enviroment autonomously and seek out visual targets without colliding with any
objects. While we accomplished this goal, we had also hoped, but were unable,
to fully implement odometry and environment mapping. So though Cerbaris can
autonomously seek out a designated target, it cannot -- yet -- do so in an
efficient and robust manner.

## Project Achievements 
Our team upgraded the Pupper by integrating a front-facing camera, a 9-DOF
inertial measurement unit (IMU), and 3 digital IR proximity sensors. With the
aid of a Google Coral TPU, camera data was utilized to quickly and
reliably identify human and tennis ball targets in real-time. We then created
software to have the pupper randomly search a room while avoiding obstacles
until it finds and chases down the target. Additionally, we were able to create
a web-based real-time monitor of Cerbaris's internal state.


<iframe width="560" height="315" src="https://www.youtube.com/embed/Xw1M4CqaYvM" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
