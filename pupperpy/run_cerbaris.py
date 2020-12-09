from subprocess import Popen
from pupperpy.CommandInterface import Control
import os
RUN_ROBOT_PATH = '/home/cerbaris/pupper_code/StanfordQuadrupped/run_robot.py'
PATH = os.path.dirname(os.path.abspath(__file__))
VISION_SCRIPT = os.path.join(PATH, 'Vision', 'pupper_vision.py')

if __name__ == "__main__":
    control = Control()
    vis_p = Popen('python3', VISION_SCRIPT)
    robo_p = Popen('python3', RUN_ROBOT_PATH)
    control.run_loop()

