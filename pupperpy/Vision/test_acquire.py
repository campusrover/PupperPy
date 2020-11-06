# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
r"""A demo for live classification with the Raspberry Pi camera.

This script is compatible only with a Raspberry Pi with a connected
Pi Camera and monitor (and a USB Accelerator). To setup the Pi Camera, see
https://www.raspberrypi.org/documentation/configuration/camera.md

Then simply run the following command to see the camera feed with real-time
classifications on your monitor:

python3 classify_capture.py \
--model models/mobilenet_v2_1.0_224_quant_edgetpu.tflite \
--label models/imagenet_labels.txt
"""

import argparse
import io
import time

from edgetpu.classification.engine import ClassificationEngine
from edgetpu.detection.engine import DetectionEngine
from edgetpu.utils import dataset_utils
import numpy as np
import picamera
from PIL import Image, ImageDraw

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument(
      '--model', help='File path of Tflite model.', required=True)
  parser.add_argument('--label', help='File path of label file.', required=True)
  args = parser.parse_args()

  labels = dataset_utils.read_label_file(args.label)
  engine = ClassificationEngine(args.model)
  detectionEngine = DetectionEngine('/home/cerbaris/pupper_code/PupperPy/pupperpy/Vision/models/ssd_mobilenet_v2_coco_quant_postprocess_edgetpu.tflite')
  detectionLabels = dataset_utils.read_label_file('/home/cerbaris/pupper_code/PupperPy/pupperpy/Vision/models/coco_labels.txt')

  with picamera.PiCamera() as camera:
    camera.resolution = (640, 480)
    camera.framerate = 30
    _, height, width, _ = engine.get_input_tensor_shape()
    camera.start_preview()
    try:
      stream = io.BytesIO()
      count = 0
      for _ in camera.capture_continuous(
          stream, format='rgb', use_video_port=True, resize=(width, height)):
        stream.truncate()
        stream.seek(0)
        input_tensor = np.frombuffer(stream.getvalue(), dtype=np.uint8)
        print(type(stream.getvalue()))
        image = Image.frombuffer('RGB',(width,height), stream.getvalue())
        draw = ImageDraw.Draw(image)

        with open('/home/cerbaris/pupper_code/PupperPy/pupperpy/Vision/test_images/' + str(count) + '.png','wb') as f:
            image.save(f)
        start_ms = time.time()
        results = engine.classify_with_input_tensor(input_tensor, top_k=1)
        objects = detectionEngine.detect_with_image(image,threshold=0.1,keep_aspect_ratio=True,relative_coord=False,top_k=3)
        elapsed_ms = time.time() - start_ms
        print('--------------------------')
        for obj in objects:
            if detectionLabels:
                print(detectionLabels[obj.label_id] + ' score = ' + str(obj.score))
            box = obj.bounding_box.flatten().tolist()
            print('box = ', box)
            draw.rectangle(box, outline='red')
            draw.text((box[0],box[1]), detectionLabels[obj.label_id] + " " + str(obj.score)) 
        if not objects:
            print('No objects detected')
        else:
            with open('/home/cerbaris/pupper_code/PupperPy/pupperpy/Vision/test_images/' + str(count) + '_boxes.png','wb') as f:
                image.save(f)

        count+=1
        #if results:
        #  camera.annotate_text = '%s %.2f\n%.2fms' % (
        #      labels[results[0][0]], results[0][1], elapsed_ms * 1000.0)
    finally:
      camera.stop_preview()


if __name__ == '__main__':
  main()
