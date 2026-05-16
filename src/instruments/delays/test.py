import sys
import time
from time import sleep

from src.instruments.delays.delay import Time_Delay

def main():

    start = int(round(time.time() * 1000))
    print(start)
    tDelay = Time_Delay("tdelay",3000)
    tDelay.start()
    tDelay.join()
    #tDelay.abort()
    # tDelay.pause()
    # sleep(1)
    # tDelay.resume()
    stop = int(round(time.time() * 1000))
    print(stop)
    print(stop - start)


if __name__ == '__main__':
    sys.exit(main())  # next section explains the use of sys.exit
