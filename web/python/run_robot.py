import numpy as np
import time, random, os, pusher
from dotenv import load_dotenv

def main():
    """Main program
    """
    load_dotenv() # load environment variables
    dt = .5
    last_loop = time.time()
    pusher_client = pusher.Pusher(\
        app_id=os.getenv('PUSHER_APP_ID'), \
        key=os.getenv('PUSHER_KEY'), \
        secret=os.getenv('PUSHER_SECRET'), \
        cluster=os.getenv('PUSHER_CLUSTER'))

    while True:
        now = time.time()
        if now - last_loop < dt:
            continue
        last_loop = time.time()

        data = random.random()
        print('now: ' + str(now), 'data: ' + str(data))

        pusher_client.trigger('data', 'new', {'time': now, 'data': data})

if __name__ == "__main__":
    main()
