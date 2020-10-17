from picamera import PiCamera
from time import sleep
from os import path, mkdir

camera = PiCamera()
savedir = '/home/cerbaris/test/test_camera_results/'
if not path.isdir(savedir):
    mkdir(savedir)

print("Starting normal preview")
camera.start_preview()
sleep(5)
camera.stop_preview()
sleep(1)

print("Starting preview with 180 degree rotation")
camera.rotation = 180
camera.start_preview()
sleep(5)
camera.stop_preview()
sleep(1)

print("Rotation reversed... starting preview")
camera.rotation = 0
camera.start_preview()
sleep(5)
camera.stop_preview()
sleep(1)

print("Starting preview with alpha=200")
camera.start_preview(alpha=200)
sleep(5)
camera.stop_preview()
sleep(1)

print("Testing capture method. Results saved to test/test_camera_results/capture_1.jpg")
camera.start_preview()
sleep(5)
camera.capture('/home/cerbaris/test/test_camera_results/capture_1.jpg','jpeg')
camera.stop_preview()
sleep(1)

print("Testing capture method within loop for 5 frames")
camera.start_preview()
for i in range(2,7):
    sleep(5)
    camera.capture('/home/cerbaris/test/test_camera_results/capture_%s.jpg' % i)
camera.stop_preview()
sleep(1)

print("Testing start_recording method with .h264 output")
camera.start_preview()
camera.start_recording('/home/cerbaris/test/test_camera_results/recording_1.h264','h264')
sleep(5)
camera.stop_recording()
camera.stop_preview()
sleep(1)

print("Testing video_stabilization capabilities. Recording for 20 seconds. Please move camera")
camera.video_stabilization=True
camera.start_preview()
camera.start_recording('/home/cerbaris/test/test_camera_results/stabilized_recording.h264','h264')
sleep(20)
camera.stop_recording()
camera.stop_preview()
