import os, pusher
from dotenv import load_dotenv
from pathlib import Path

class PusherClient:
  def __init__(self):
    # load .env from current directory
    load_dotenv(dotenv_path=Path(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')))
    self.client = pusher.Pusher(\
        app_id=os.getenv('PUSHER_APP_ID'), \
        key=os.getenv('PUSHER_KEY'), \
        secret=os.getenv('PUSHER_SECRET'), \
        cluster=os.getenv('PUSHER_CLUSTER'))

  def send(self, message, channel='data', event='new'):
    self.client.trigger(channel, event, message)
