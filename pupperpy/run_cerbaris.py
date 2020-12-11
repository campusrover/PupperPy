from subprocess import Popen
from pupperpy.CommandInterface import Control
import os
import time
RUN_ROBOT_PATH = '/home/cerbaris/pupper_code/StanfordQuadruped/run_robot.py'
PATH = os.path.dirname(os.path.abspath(__file__))
VISION_SCRIPT = os.path.join(PATH, 'Vision', 'pupper_vision.py')

if __name__ == "__main__":
    try:
        pigpio_p = Popen(['pigpiod'])
        control = Control()
        vis_p = Popen(['python3', VISION_SCRIPT])
        robo_p = Popen(['python3', RUN_ROBOT_PATH])
        time.sleep(5)
        control.run_loop()
    except:
        pigpio_p.terminate()
        control.stop_loop()
        vis_p.kill()
        robo_p.kill()

