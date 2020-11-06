# Script for pupper_vision.service
# Written by Ben Ballintyn (bbal@brandeis.edu) in 2020
# 
# Uses the edgetpu API to do object detection in as close to real time as possible
# Streams images from picamera to DetectionEngine and then sends relevant bounding
# box information over a UDP comms channel
import os.path
import argparse
import io
import time

from edgetpu.detection.engine import DetectionEngine

import pickle
import numpy as np
import picamera
from PIL import Image, ImageDraw

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--object_type', help='Type of object to capture images of', required=True)
    parser.add_argument('--n', help='Number of frames to acquire', required=True)
    args = parser.parse_args()
    print('Setting up to capture ' + args.n + ' images of type ' + args.object_type)
    LOG_FILE = '/home/cerbaris/pupper_code/PupperPy/pupperpy/Vision/training_image_acquistion_log.txt'
    SAVE_PATH = '/home/cerbaris/pupper_code/PupperPy/pupperpy/Vision/training_images/' + args.object_type + '/'
    if not os.path.isdir(SAVE_PATH):
        os.mkdir(SAVE_PATH)
        count = 0
    else:
        with open(SAVE_PATH + 'image_count.pkl','rb') as f:
            count = pickle.load(f)

    engine = DetectionEngine('/home/cerbaris/pupper_code/PupperPy/pupperpy/Vision/models/ssd_mobilenet_v2_coco_quant_postprocess_edgetpu.tflite')

    input('Press ENTER to begin capturing frames...')
    n = 0
    with picamera.PiCamera() as camera:
        camera.resolution = (640, 480)
        camera.framerate = 30
        _, height, width, _ = engine.get_input_tensor_shape()
        try:
            stream = io.BytesIO()
            for _ in camera.capture_continuous(SAVE_PATH + args.object_type + '_{timestamp:%f}.png', format='png', use_video_port=True, resize=(width, height)):
                #stream.truncate()
                #stream.seek(0)
                #input_tensor = np.frombuffer(stream.getvalue(), dtype=np.uint8)
                #image = Image.frombuffer('RGB',(320,304), stream.getvalue())
                #with open(SAVE_PATH + args.object_type + '_' + str(count) + '.jpg','wb') as f:
                #    image.save(f)
                count += 1
                n += 1
                if (n >= int(args.n)):
                    break
                else:
                    print('Captured image #' + str(n))
        except BaseException as e:
            with open(LOG_FILE,'w') as f:
                f.write("Failed to run image acquisition loop: {0}\n".format(str(e)))
    
    with open(SAVE_PATH + 'image_count.pkl','wb') as f:
        pickle.dump(count,f)

if __name__ == '__main__':
  main()
