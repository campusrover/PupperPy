import argparse
import io
import time

from edgetpu.detection.engine import DetectionEngine
from edgetpu.utils import dataset_utils
import numpy as np
import picamera

def main():
    parser = argparse.ArgumentParser()
