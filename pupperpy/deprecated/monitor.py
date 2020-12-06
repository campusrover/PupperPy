from UDPComms import Subscriber
import time
import datetime

view_sub = Subscriber(8810)
MSG_INTERVAL = 20
CONTROL_LOG='/home/cerbaris/pupper_code/control.log'

if __name__ == "__main__":
    print('Waiting for messages...')
    last_msg = None
    while True:
        try:
            msg = view_sub.get() 
            if last_msg is None:
                last_msg = msg
                same = False
            else:
                same = True
                for k,v in msg.items():
                    if last_msg[k] != v:
                        same = False

            if not same:
                print('')
                print(datetime.datetime.now())
                print(msg)
                print('')

                curr_time = datetime.datetime.now()
                with open(CONTROL_LOG, 'a') as f:
                    print('-'*80, file=f)
                    print(curr_time, file=f)
                    print(msg, file=f)
                    print('-'*80, file=f)
                    print('', file=f)

            time.sleep(1 / MSG_INTERVAL)

        except:
            print ("\033[A                             \033[A")
            print('Waiting for messages...')
            time.sleep(5)
