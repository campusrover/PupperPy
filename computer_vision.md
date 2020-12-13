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
##### Motivation
The version of MobileNetV2 mentioned above, was pretrained on the [COCO dataset](https://cocodataset.org/#home "COCO dataset homepage") to recognize 90 different object classes. One of these classes is "sports ball" which was close to our desired goal (a tennis ball). We therefore evaluated the performance of this network "out of the box". We found that while this network was capable of recognizing tennis balls in an image, the tennis ball needed to be fairly close to the robot to be detected and usually had a low associated confidence. This is most likely due to the fact that there were few tennis balls (labeled as sports balls) in the COCO training set.
| Undetected               | Detected
:-------------------------:|:---------------------:
![failure]                 | ![success]

[failure]: /figures/original_net_detection_failure.png
[success]: /figures/original_net_detection_success.png

We therefore decided to use a transfer learning protocol to retrain the last few layers of the MobileNetV2 on a custom dataset taken from within our robotics lab (see the `Vision/retraining/learn_custom/custom/images` for the images used). We speculated that by retraining specifically on images of tennis balls we would be able to improve the detection range. 

Transfer learning is a method for taking a network trained on one dataset, and using the learned features to predict outputs for a new dataset with few examples. The idea is that you remove only the last few layers from the pre-trained network (the layers that essentially map the learned features to output class probabilities) and retrain new output layers on your custom classes. This allows you to reuse the previously learned and hopefully general learned features in the earlier layers of the network. The retraining process then simply learns a mapping from the pretrained features to your new output classes. This saves lots of training time (since you are training many fewer parameters) and allows you to have fewer examples of your custom classes. In our case, we are hoping to reuse the features learned on the COCO dataset (what this version of mobilenet_v2 was trained on) to learn to detect specifically tennis balls, humans, and chairs (common objects around the robotics lab). The below instructions are meant to be sufficiently general that you could retrain the mobilenet_v2 network on your own custom dataset. 

##### Dataset organization
To collect a custom dataset, we simply placed tennis balls around the robotics lab and continuously captured images using the picamera mounted on the robot. Once the images were acquired, we copied them off of the pi to an Ubuntu laptop (the rest of the retraining procedure all happens off of the pi). The images now need to be labeled by adding bounding boxes around all of the objects we wished to recognize. To do this, we used [labelImg](https://github.com/tzutalin/labelImg "labelImg github page") which allows you to go through a directory of images and draw boxes around objects in each image. Note that you will need to create a .txt file with all of your desired classes (see the `predefined_classes.txt` file in the data folder of the labelImg repo for an example). Once you have finished annotating the images, you will have a .xml file for each image with a list of the associated bounding boxes. Go ahead and put all of the image and .xml files into one folder.

We now want to split the annotated dataset into a training set and a test set. For this we've written a python script `split_data.py` which accepts 2 required and 1 optional command line argument.  
e.g.  
```python
    python3 split_data.py \  
    --data_dir=/path/to/dataset/ \  
    --output_dir=/where/to/store/output/ \  
    --train_frac=0.5   
```
where `train_frac` gives the fraction of the total dataset to be used as training data.
This will create two directories, train and test, in the `output_dir` directory.

Once this is done, we need to convert our training and test sets into TFRecord files. To do this we can use the `generate_tfrecord.py` script in `pupperpy/Vision/transfer_learning/`. We will convert the training and test sets separately. For example, for the training set, if all the image and .xml files for the training set are in a directory `data/train`, run:
```python
python3 generate_tfrecord.py \
--xml_dir=data/train \
--labels_path=/path/to/labels.pbtxt \
--output_path=/path/to/output/tfrecord/train.record \
--image_dir=data/train
```
If this code runs successfully, there should now be a train.record file in your desired output location. Repeat the same process but for the test set now to create a test.record file.

Lastly, we need to create a label map file called pupper_label_map.pbtxt (see example in the Vision/transfer_learning/learn_custom/custom folder). List all of your desired output classes in this file like this:
```
item {
  id: 1
  name: 'ball'
}

item {
  id: 2
  name: 'human'
}

item {
  id: 3
  name: 'chair'
}
.
.
.
```

##### Retraining the network
Now that we have our train/test.record files, we can move on to actually retraining the network. To do this, we will follow a [tutorial on the coral webpage](https://coral.ai/docs/edgetpu/retrain-detection/#requirements "Transfer Learning tutorial") for retraining the last few layers of the mobilenet_v2 model in docker. This tutorial is meant to retrain the network to recognize certain breeds of cats and dogs, but we will utilize the retraining code and just substitute in our own dataset. Note, however that we will need to modify some of the files in the tutorial in order to use our custom dataset.

1. The first step is to [install docker](https://docs.docker.com/engine/install/ubuntu/ "install docker") onto your machine.

2. Follow the instructions in the tutorial for cloning the coral tutorials repo and starting the Docker container.
```shell
CORAL_DIR=${HOME}/google-coral && mkdir -p ${CORAL_DIR}
cd ${CORAL_DIR}
git clone https://github.com/google-coral/tutorials.git
cd tutorials/docker/object_detection
docker build . -t detect-tutorial-tf1
DETECT_DIR=${PWD}/out && mkdir -p $DETECT_DIR

docker run --name edgetpu-detect \
--rm -it --privileged -p 6006:6006 \
--mount type=bind,src=${DETECT_DIR},dst=/tensorflow/models/research/learn_custom \
detect-tutorial-tf1
```
Note that the line starting with --mount links the directory `DETECT_DIR` in your normal file system to the directory `/tensorflow/models/research/learn_custom` in the docker container's file system. This means that the contents of the `learn_custom` folder in the container are maintained in `DETECT_DIR` even after the docker container is closed (every other newly created folder in the docker container will be erased). This is important to know since if your container closes for some reason before the retraining is finished, any newly created or edited files not in `/tensorflow/models/research/learn_custom` will be lost upon restarting the container.

3. Once you start the docker container, your command prompt should be inside the Docker container at the path `/tensorflow/models/research` and you should see an empty directory titled `learn_custom` inside the research directory. The `learn_pet` directory referenced in the tutorial will not appear since we replaced that with `learn_custom` in the `--mount` flag above. You can create and populate the `learn_pet` directory if you want to run the original tutorial or just to see the file structure if your run the line:
```shell
./prepare_checkpoint_and_dataset.sh --network_type mobilenet_v2_ssd --train_whole_model false
```
from the original tutorial. This will download the images and annotations, download the model checkpoint, modify the pipeline.config file, and create .record files out of the downloaded dataset. In the steps below we will recreate these steps for our own dataset in the `learn_custom` directory. 

4. Inside `/tensorflow/models/research/learn_custom/` create 4 subdirectories:  
```shell
cd learn_custom
mkdir ckpt models custom train
cd ..
```

5. Next, you will see a `constants.sh` file in the `research` directory. Copy that file to a new file `pupper_constants.sh`. We need to change the specified paths at the bottom of this file to use our dataset. Change the lines (starting at `OBJ_DET_DIR=...`) to read the following:  
```shell
OBJ_DET_DIR="$PWD"
LEARN_DIR="${OBJ_DET_DIR}/learn_custom"
DATASET_DIR="${LEARN_DIR}/custom
CKPT_DIR="${LEARN_DIR}/ckpt"
TRAIN_DIR="${LEARN_DIR}/train"
OUTPUT_DIR="${LEARN_DIR}/models"
```
Now save and close this file.

6. From a terminal outside the docker container, use the `docker cp` command to copy the train.record, test.record, and pupper_label_map.pbtxt files into the the learn_custom/custom directory in the docker container:
e.g.
```shell
docker cp /path/to/train.record edgetpu-detect:/tensorflow/models/research/learn_custom/custom
docker cp /path/to/test.record edgetpu-detect:/tensorflow/models/research/learn_custom/custom
docker cp /path/to/pupper_label_map.pbtxt edgetpu-detect:/tensorflow/models/research/learn_custom/custom
```

7. Now we need to get the model checkpoint and pipeline files into the `learn_custom/ckpt` directory. The easiest way to do this is to copy the contents of the `Vision/transfer_learning/learn_custom/ckpt` directory in the PupperPy repo into the `/tensorflow/models/research/learn_custom/ckpt` directory in the docker container.
e.g.
```shell
docker cp /path/to/pupperpy/Vision/transfer_learning/learn_custom/ckpt/ edgetpu-detect:/tensorflow/models/research/learn_custom/
```

Alternatively, if you ran the `prepare_checkpoint_and_dataset.sh` file above, you can copy the contents of the `learn_pet/ckpt` directory to `learn_custom/ckpt`

8. Next, we need to configure the `pipeline.config` file in `learn_custom/ckpt/`. If you copied the `ckpt` directory from the PupperPy repo, you should only need to change the `num_classes` field below. The critical lines are:
   1. (line 19) `num_classes: x`
      * change whatever x is to the number of classes you want to detect (must agree with the number of classes in you pupper_label_map.pbtxt)
   2. (line 27) Make sure this line is `type: "ssd_mobilenet_v2"`
   3. (line 174) This gives the path to the model checkpoint file to use. Make sure it says:
      * `fine_tune_checkpoint: "/tensorflow/models/research/learn_custom/ckpt/model.ckpt"`
   4. (line 194) Gives the path to the .pbtxt label map. Shoud be:
      * `label_map_path: "/tensorflow/models/research/learn_custom/custom/pupper_label_map.pbtxt"`
   5. (line 196) Gives the path to the train.record file. Should be:
      * `input_path: "/tensorflow/models/research/learn_custom/custom/train.record"`
   6. (line 205) Same as line 194, path to .pbtxt label map.
   7. (line 209) Path to test.record file. Should be:
      * `input_path: "/tensorflow/models/research/learn_custom/custom/test.record"`

9. We are almost ready to begin training. Make sure you are in the `/tensorflow/models/research/` directory in the docker container. The last change we need to make is to the `retrain_detection_model.sh` script. Open this file then go down to the line that says:
```shell
source "${PWD}/constants.sh"
```
and change this to:
```shell
source "${PWD}/pupper_constants.sh"
```

10. Initiate the retraining by running:
```shell
NUM_TRAINING_STEPS=500 && NUM_EVAL_STEPS=100
./retrain_detection_model.sh \
--num_training_steps ${NUM_TRAINING_STEPS} \
--num_eval_steps ${NUM_EVAL_STEPS}
```
as in the tutorial. This will begin the retraining process using your CPU. As of now we are unsure how to use the code from this tutorial to utilize GPU resources for retraining. The retraining process will likely take several hours depending on how large your custom dataset is.

11. As stated in the tutorial, you can monitor the training progress by starting tensorboard in the docker container. In a new terminal:
```shell
sudo docker exec -it edgetpu-detect /bin/bash
tensorboard --logdir=./learn_custom/train
```
Then you can go to localhost:6006 in your browser and should get a tensorboard panel that will update as training progresses. At first, only the GRAPHS tab will be available, showing you a visualization of the mobilenet network architecture. However, after new checkpoints are saved in `learn_custom/train`, the SCALARS (showing various training metrics including the loss values) and IMAGES (showing predicted vs ground truth bounding boxes) tabs will appear allowing you to assess the quality of the training.

##### Compiling the model for the Edge TPU
Now that the network has been retrained, as stated in the [tutorial](https://coral.ai/docs/edgetpu/retrain-detection/#compile-the-model-for-the-edge-tpu "Compiling the model for the Edge TPU"), we need to convert the checkpoint file (found in `/tensorflow/models/research/learn_custom/train`) to a frozen graph, convert that graph to a TensorFlow Lite flatbuffer file, then compile that model for the Edge TPU. Fortunately the first 2 steps can be done using the `convert_checkpoint_to_edgetpu_tflite.sh` script in `/tensorflow/models/research`. However we need to make make one small change first. In `convert_checkpoint_to_edgetpu_tflite.sh` change the line:
```shell
source "${PWD}/constants.sh"
```
to:
```shell
source "${PWD}/pupper_constants.sh"
```
Now look in the `/tensorflow/models/research/learn_custom/train` directory and look for the .ckpt file with the highest number (let's call this number x). This is the most recent checkpoint file (the one from the end of training). We can now convert this checkpoint to a TensorFlow Lite model by calling the following from the `/tensorflow/models/research` directory:
```shell
./convert_checkpoint_to_edgetpu_tflite.sh --checkpoint_num x
```
where x is the checkpoint number. This will output the TensorFlow Lite model as a file named `output_tflite_graph.tflite` in the `/tensorflow/models/research/learn_custom/models/` directory. Recall that all of the files in the `/tensorflow/models/research/learn_custom/` directory in the docker container are also available on your host file system at `google-coral/tutorials/docker/object_detection/out` if you used the directions above when running the docker container.

Next, follow the instructions in the tutorial (replicated here) to install the Edge TPU Compiler:
```shell
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list
sudo apt update
sudo apt-get install edgetpu-compiler
```
Now change to the directory on your host filesystem with the .tflite model (should be `${HOME}/google-coral/tutorials/docker/object_detection/out/models`) and run the edgetpu_compiler on the .tflite model.
```shell
cd ${HOME}/google-coral/tutorials/docker/object_detection/models
edgetpu_compiler output_tflite_graph.tflite
```
The compiled file is named `output_tflite_graph_edgetpu.tflite` and is saved to the current directory. Rename this file to something more descriptive (ours is named `ssd_mobilenet_v2_pupper_quant_edgetpu.tflite`). 

To use the retrained model on the pupper, you will need to add it to the `pupperpy/Vision/models` directory. In addition, you will need to create a file with the output classes of the model (see `pupperpy/Vision/models/pupper_labels.txt` for an example) and also put it in the models folder. Lastly, you will need to change the `MODEL_PATH` and `LABEL_PATH` lines (lines 23 and 24) in pupper_vision.py to reflect your new model and class files.

*Congratulations* the next time you run `pupper_vision.py` your retrained model will be used. Just be sure to update any exisiting control code to use the class strings from your class file.
