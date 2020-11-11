import os, pusher
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
    self.client.trigger('sensor_data', 'new', {'timestamp': message['time'], 'x_acc': message['x_acc'], 'y_acc': message['y_acc'], 'z_acc': message['z_acc'], 'left_obj': str(message['left_sensor']), 'center_obj': str(message['center_sensor']), 'right_obj': str(message['right_sensor']), 'gyro_calibration': message['gyro_calibration']})
    print()
