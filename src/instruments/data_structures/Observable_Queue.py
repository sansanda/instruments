import sys
from collections import deque
from queue import Queue

from observer.Observer import Observer
from observer.Observer import Observable

class Observable_Queue(Observable, Queue, Observer):

    def __init__(self, events, max_size):
        """events is a list"""
        if events is None:
            events = []
        if "full" not in events:
            events.append("full")

        Observable.__init__(self,events)
        Queue.__init__(self,max_size)

    '''Variant of Queue that retrieves most recently added entries first.'''

    def put(self, item, block=True, timeout=None):
        Queue.put(self,item, block, timeout)
        if self.full():
            self.notify("full",
                        "Queue is full. Actual size is " + str(self.qsize()) + " and max_size = " + str(self.maxsize))

    def get(self, block=True, timeout=None):
        return Queue.get(self, block, timeout)

def main():

    oq = Observable_Queue(['full'],2)
    oq.put(1, False)
    oq.put(1, False)
    oq.put(2, block=True, timeout=1)


if __name__ == '__main__':
    sys.exit(main())  # next section explains the use of sys.exit