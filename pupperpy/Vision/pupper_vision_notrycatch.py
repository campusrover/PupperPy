# Script for pupper_vision.service
# Written by Ben Ballintyn (bbal@brandeis.edu) in 2020
# 
# Uses the edgetpu API to do object detection in as close to real time as possible
# Streams images from picamera to DetectionEngine and then sends relevant bounding
# box information over a UDP comms channel

import argparse
import io
import time

from edgetpu.detection.engine import DetectionEngine
from edgetpu.utils import dataset_utils
import numpy as np
import picamera
from PIL import Image, ImageDraw
from UDPComms import Publisher

def main():
    cv_publisher = Publisher(105)
    MODELS_DIR = '/home/cerbaris/pupper_code/PupperPy/pupperpy/Vision/models/'
    MODEL_PATH = MODELS_DIR + 'ssd_mobilenet_v2_coco_quant_postprocess_edgetpu.tflite'
    LABEL_PATH = MODELS_DIR + 'coco_labels.txt'
    LOG_FILE = '/home/cerbaris/pupper_code/PupperPy/pupperpy/Vision/vision_log.txt'
    labels = dataset_utils.read_label_file(LABEL_PATH)
    engine = DetectionEngine(MODEL_PATH)

    with picamera.PiCamera() as camera:
        camera.resolution = (640, 480)
        camera.framerate = 30
        _, height, width, _ = engine.get_input_tensor_shape()
        
        stream = io.BytesIO()
        count = 0
        for _ in camera.capture_continuous(stream, format='rgb', use_video_port=True, resize=(width, height)):
            stream.truncate()
            stream.seek(0)
            input_tensor = np.frombuffer(stream.getvalue(), dtype=np.uint8)
            #image = Image.frombuffer('RGB',(width,height), stream.getvalue())
            image = Image.frombuffer('RGB',(320,304), stream.getvalue()) # to account for automatic upscaling by picamera when format='rgb'
            draw = ImageDraw.Draw(image)
            start_ms = time.time()
            results = engine.detect_with_image(image,threshold=0.1,keep_aspect_ratio=True,relative_coord=False,top_k=51)
            elapsed_ms = time.time() - start_ms
                
            detectedObjs = []
            for obj in results:
                if (obj.label_id == 0 or obj.label_id == 36):
                    if (obj.label_id == 36):
                        print('Tennis ball detected')
                    box = obj.bounding_box.flatten().tolist()
                    draw.rectangle(box, outline='red')
                    draw.text((box[0],box[1]), labels[obj.label_id] + " " + str(obj.score))
                    w = box[0] - box[2]
                    h = box[1] - box[3]
                    objInfo = {'bbox_x':float(box[0]),
                               'bbox_y':float(box[1]),
                               'bbox_h':float(h),
                               'bbox_w':float(w),
                               'bbox_label':labels[obj.label_id],
                               'bbox_confidence': float(obj.score)
                               }
                    detectedObjs.append(objInfo)
            cv_publisher.send(detectedObjs)
            #print(detectedObjs)

            with open('/home/cerbaris/pupper_code/PupperPy/pupperpy/Vision/test_images/' + str(count) + '.png','wb') as f:
                image.save(f)
            count+=1
        #except BaseException as e:
        #    with open(LOG_FILE,'w') as f:
        #        f.write("Failed to run detection loop: {0}\n".format(str(e)))

if __name__ == '__main__':
  main()
