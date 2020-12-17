import os
import pusher
import random
from dotenv import load_dotenv
from pathlib import Path


class PusherClient:
    def __init__(self):
        # load .env from current directory
        load_dotenv(dotenv_path=Path(os.path.join(
            os.path.dirname(os.path.abspath(__file__)), '.env')))
        self.client = pusher.Pusher(
            app_id=os.getenv('PUSHER_APP_ID'),
            key=os.getenv('PUSHER_KEY'),
            secret=os.getenv('PUSHER_SECRET'),
            cluster=os.getenv('PUSHER_CLUSTER'))

    def send(self, message):
        self.client.trigger('sensor_data', 'new', {
            'timestamp': message['time'],
            'yaw': message['yaw'],
            'xPos': message['x_pos'],
            'yPos': message['y_pos'],
            'xAcc': message['x_acc'],
            'yAcc': message['y_acc'],
            'leftObj': str(message['left_sensor']),
            'centerObj': str(message['center_sensor']),
            'rightObj': str(message['right_sensor'])
        })
        self.client.trigger('vision_data', 'new', {
            'timestamp': message['time'],
            'bboxLabel': message['bbox_label'],
            'bboxConfidence': message['bbox_confidence'],
            'bboxX': message['bbox_x'],
            'bboxY': message['bbox_y'],
            'bboxW': message['bbox_w'],
            'bboxH': message['bbox_h']
        })
        self.client.trigger('state_data', 'new', {
            'timestamp': message['time'],
            'state': message['state'],
            'yawRate': message['yaw_rate'],
            'xVel': message['x_vel'],
            'yVel': message['y_vel']
        })

        if 'active_node' in message.keys():
            self.client.trigger('tree_data', 'new', {
                'timestamp': message['time'],
                'nodeId': message['active_node']
            })
