---
layout: template
---
### Pupper Vision
For this project, we used the [raspberry pi v2 camera](https://www.amazon.com/Raspberry-Pi-Camera-Module-Megapixel/dp/B01ER2SKFS/ref=sxts_sxwds-bia-wc-nc-drs1_0?cv_ct_cx=raspberry+pi+camera&dchild=1&keywords=raspberry+pi+camera&pd_rd_i=B01ER2SKFS&pd_rd_r=956aa0c4-1cb5-4b3c-a5a5-977edde184a8&pd_rd_w=cDFck&pd_rd_wg=P6cVG&pf_rd_p=0ec05f25-9534-48fe-9c3e-40b89957230e&pf_rd_r=KG6HEMGWM3EBRMW5DSTP&psc=1&qid=1607705316&sr=1-1-88388c6d-14b8-4f70-90f6-05ac39e80cc0 "Amazon listing") to detect and localize our object of interest (tennis ball). At a high level, the vision systems works as follows:
1. Raspberry pi is started
2. `pupper_vision.py` is started either as a linux service or by calling it from a higher level python script. This loads the computer vision model and sets up the picamera.
3. Use `picamera.capture_continuous` method to continuously capture frames
4. Pass each frame through a retrained version of the mobilenet_v2 object detection network
5. Output top N bounding boxes (according to confidence level assigned by model) with associated class labels
6. Publish the bounding box info as a list of dictionaries via UDPcomms on port 105

#### Hardware Interface
To accelerate object detection inference onboard the robot, we used the [Coral TPU USB accelerator from Google](https://coral.ai/products/accelerator/ "TPU product page"). This plugs into one of the USB 3.0 ports on the raspberry pi 4.

To get started with the USB accelerator, follow the [instructions](https://coral.ai/docs/accelerator/get-started/) for installing the edgetpu runtime library.

#### Tensorflow
The Coral edge TPU is only compatible with Tensorflow Lite and since we only want to do inference with a .tflite model onboard the robot, we will [install just the TF Lite interpreter](https://www.tensorflow.org/lite/guide/python). Make sure to use the .whl for ARM 32 and your corresponding python version (we used python 3.7)

#### ML Models
To perform inference on the TPU, we are able to use the `DetectionEngine` in the [Edge TPU API](https://coral.ai/docs/edgetpu/api-intro/#install-the-library "Edge TPU API install"). This API abstracts away almost all of the tensor manipulation required to do inference. All we really need to do is find an object detection model that we can use. Currently, this API only supports [SSD (Single-Shot Detection)](https://arxiv.org/pdf/1512.02325.pdf "Original SSD paper") with a postprocessing operator ([such as non-maximum suppression](https://towardsdatascience.com/non-maximum-suppression-nms-93ce178e177c "NMS blog")). Additional restrictions on the network operations that are supported on the coral TPU can be found [here](https://coral.ai/docs/edgetpu/models-intro/#supported-operations "Supported operations").

Given the above restrictions, we decided to use a version of [MobileNetV2](https://arxiv.org/pdf/1801.04381.pdf "MobileNetV2 Paper") which is precompiled to be run on the Coral TPU. This model (MobileNetV2 SSD v2 COCO) and a couple other variants are available [here](https://coral.ai/models/ "Coral Models page"). The [MobileNet networks](https://arxiv.org/pdf/1704.04861.pdf "Original MobileNet paper"), developed by Google, are an attractice option since they utilize a modified convolution operation that requires only ~10% of the computation of a standard convolution operation. This means that they retain most of the accuracy of other vision models but can be run much faster allowing them to be used on mobile and edge devices.

#### Transfer Learning
The version of MobileNetV2 mentioned above, was pretrained on the [COCO dataset](https://cocodataset.org/#home "COCO dataset homepage") to recognize 90 different object classes. One of these classes is "sports ball" which was close to our desired goal (a tennis ball). We therefore evaluated the performance of this network "out of the box". We found that while this network was capable of recognizing tennis balls in an image, the tennis ball needed to be fairly close to the robot to be detected.
| Undetected               | Detected
:-------------------------:|:---------------------:
![failure]                 | ![success]
[failure]: https://github.com/nubs01/PupperPy/tree/gh-pages/figures/original_network_detection_failure.png
[success]: https://github.com/nubs01/PupperPy/tree/gh-pages/figures/original_network_detection_success.png
