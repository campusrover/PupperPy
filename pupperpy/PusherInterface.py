import os, pusher, random
from dotenv import load_dotenv
from pathlib import Path

class PusherClient:
  def __init__(self):
    # load .env from current directory
    load_dotenv(dotenv_path=Path(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')))
    self.client = pusher.Pusher(\
        app_id=os.getenv('PUSHER_APP_ID'),
        key=os.getenv('PUSHER_KEY'),
        secret=os.getenv('PUSHER_SECRET'),
        cluster=os.getenv('PUSHER_CLUSTER'))

  def send(self, message):
    self.client.trigger('sensor_data', 'new', {
        'timestamp': message['time'], 
        'yaw': message['yaw'],
        'x_pos': message['x_pos'],
        'y_pos': message['y_pos'],
        'x_acc': message['x_acc'],
        'y_acc': message['y_acc'],
    #    'z_acc': message['z_acc'],
        'left_obj': str(message['left_sensor']), 
        'center_obj': str(message['center_sensor']), 
        'right_obj': str(message['right_sensor'])
    })
    self.client.trigger('vision_data', 'new', {
        'timestamp': message['time'],
        'bbox_label': message['bbox_label'],
        'bbox_confidence': message['bbox_confidence'],
        'bbox_x': message['bbox_x'], 
        'bbox_y': message['bbox_y'], 
        'bbox_w': message['bbox_w'], 
        'bbox_h': message['bbox_h']
    })
    self.client.trigger('state_data', 'new', {
        'timestamp': message['time'],
        'state': message['state'],
        'yaw_rate': message['yaw_rate'],
        'x_vel': message['x_vel'], 
        'y_vel': message['y_vel']
    })
    self.client.trigger('tree_data', 'new', {
        'node_id': random.randint(0, 15)
    })
