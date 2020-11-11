import time, random
from pupperpy.PusherInterface import PusherClient

def main():
    """Main program
    """
    dt = .5
    last_loop = time.time()
    pusher_client = PusherClient()

    while True:
        now = time.time()
        if now - last_loop < dt:
            continue
        last_loop = time.time()

        pusher_client.send({'metadata': {'timestamp': now}, 'data': {'first': 'SOME STRING', 'second': random.random()}})

if __name__ == "__main__":
    main()
