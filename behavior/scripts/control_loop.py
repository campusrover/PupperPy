import random
from ControllerState import ControllerState
from CameraData import BoundingBox
from CameraData import CameraData

TURNING_VELOCITY = .1
FORWARD_VELOCITY = .1
BOX_SIZE_LIMIT = 200
MAXIUMUM_WAIT_TIME = 60
cam_dat = CameraData()
front_sensor_dat = False
timer = 0
robot_state = "RANDOM_SEARCH"
pos = None


"""
Does random search (roomba) until target is found.
"""


def randomSearch():
    global cam_dat, front_sensor_dat, robot_state
    new_command = ControllerState()

    if not cam_dat:  # target not found yet
        if front_sensor_dat:
            new_command.right_analog_x = TURNING_VELOCITY  # just turn
        else:
            new_command.left_analog_y = FORWARD_VELOCITY  # go forward
    robot_state = "MOVE_TO_TARGET"

    return new_command


"""
Returns a new robot command based off camera and position data.
"""


def moveToTarget():
    global cam_dat, front_sensor_dat, robot_state
    new_command = ControllerState()

    if cam_dat:

        if cam_dat.target_bounding_box.area() > BOX_SIZE_LIMIT:  # if too close to object, stop
            robot_state = "SUCCESS"
            return new_command

        # calculate how far bounding box is from center into offset
        target_x = cam_dat.target_bounding_box.median_point()[0]
        offset = target_x - cam_dat.SIZE_X / 2

        # adjust yaw based on offset
        new_command.right_analog_x = offset * TURNING_VELOCITY / cam_dat.SIZE_X
        new_command.left_analog_y = FORWARD_VELOCITY

        # print(new_command.right_analog_x)

    else:  # no target found

        if front_sensor_dat:
            robot_state = "AVOID_OBSTACLES"
        else:
            robot_state = "RANDOM_SEARCH"  # object probably moved

    return new_command


"""
Returns new robot command to avoid and attempt to wall follow immediate obstacles.
"""


def avoidObstacles():
    global cam_dat, front_sensor_dat, robot_state
    new_command = ControllerState()

    if front_sensor_dat:
        new_command.right_analog_x = TURNING_VELOCITY  # just turn
    elif left_sensor_dat:
        # go forward (follow wall)
        new_command.left_analog_y = FORWARD_VELOCITY
    else:
        timer = 0
        robot_state = "MEMORY_NAVIGATION"

    return new_command


"""
Returns new robot command to navigate towards target last location.
"""


def memoryNavigation():
    global cam_dat, front_sensor_dat, robot_state
    new_command = ControllerState()

    if cam_dat:
        robot_state = "MOVE_TO_TARGET"
    # elif timer > MAXIMUM_WAIT_TIME:
    #    robot_state = "RANDOM_SEARCH"
    elif front_sensor_dat:
        robot_state = "AVOID_OBSTACLES"
    else:
        # TODO: turn toward target last known bearing()
        new_command.left_analog_y = FORWARD_VELOCITY

    return new_command


"""
Main loop.
"""
while True:
    robot_command = None

    if robot_state == "RANDOM_SEARCH":
        robot_command = randomSearch()
    elif robot_state == "MOVE_TO_TARGET":
        robot_command = moveToTarget()
    elif robot_state == "AVOID_OBSTACLES":
        robot_command = avoidObstacles()
    elif robot_state == "MEMORY_NAVIGATION":
        robot_command = memoryNavigation()
    else:
        pass
        # wait()

    # sendCommand(robot_command)
    print(robot_state + " " + robot_command.__str__())
