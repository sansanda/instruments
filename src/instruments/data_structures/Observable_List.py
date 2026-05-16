import sys
from collections import deque
from queue import Queue
from time import sleep

from observer.Observer import Observer
from observer.Observer import Observable


class Observable_List(Observable, list, Observer):
    LEN_IS_MULTIPLE_OF_EVENT = "LEN_IS_MULTIPLE_OF_"
    LIST_IS_EMPTY_EVENT = "LIST_IS_EMPTY"

    def __init__(self, events):
        """events is a list"""
        if events is None:
            events = []

        Observable.__init__(self, events)
        list.__init__(self)

    def append(self, object):

        list.append(self, object)
        self.__check_events__()

    def clear(self):
        list.clear(self)
        self.__check_events__()

    def __check_events__(self):
        # get the keys of the dictionary of events
        ks = self.event_observers.keys()

        #LIST_IS_EMPTY_EVENT has priority
        if Observable_List.LIST_IS_EMPTY_EVENT in ks:
            # LIST_IS_EMPTY_EVENT
            if len(self) == 0:
                e = Observable_List.LIST_IS_EMPTY_EVENT
                self.notify(e, e)
                return

        for k in ks:
            # LEN_IS_MULTIPLE_OF_EVENT (and contains elements) check if match
            if str(k).startswith(Observable_List.LEN_IS_MULTIPLE_OF_EVENT):
                number = int(str(k)[len(Observable_List.LEN_IS_MULTIPLE_OF_EVENT):])
                if (len(self) % number) == 0 and len(self) > 0:
                    e = Observable_List.LEN_IS_MULTIPLE_OF_EVENT + str(number)
                    self.notify(e, self[-number:])


