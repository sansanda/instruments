from threading import Thread

from src.instruments.logging.printing_messages import print_message

import abc

import time
import statistics

class Control_I(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'match') and
                callable(subclass.match) and
                hasattr(subclass, 'update_control_input') and
                callable(subclass.update_control_input) or
                NotImplemented)

    @abc.abstractmethod
    def match(self):
        """Gets if the control input match with the criteria"""
        raise NotImplementedError

    @abc.abstractmethod
    def update_control_input(self, control_input):
        """updates the control input data"""
        raise NotImplementedError

    def start(self):
        """starts the control"""
        raise NotImplementedError


class Delay_Control(Control_I):
    """A concrete Control based on elapsed time"""

    def __init__(self, delay=1000, control_input=None):
        """
        :param delay: delays is a long as seconds (in ms)
        """
        self.delay = delay
        self.control_input = control_input
        self.tStamp = round(time.time() * 1000)
        self.state = 0

    def match(self):
        """
        :return: True if control_input matchs the delays. False otherwise
        """

        match = False
        if (self.control_input is None) or (not isinstance(self.control_input, int)) or (self.control_input < 0):
            pass
        else:
            if (self.control_input - self.tStamp) >= self.delay:
                match = True
        return match

    def update_control_input(self, control_input):
        """updates the control input data"""
        self.control_input = control_input

    def start(self):
        """starts the control"""
        self.tStamp = round(time.time() * 1000)


class StDev_Control(Control_I):
    """A concrete Control based on standard deviation of a tuple of numeric samples"""

    def __init__(self, st_dev, control_input=None):
        """
        :param st_dev: The standard deviation that control_input must match
        """
        self.st_dev = st_dev
        self.control_input = control_input

    def match(self):
        """
        :param control_input as a tuple of samples.
        :return True if control_input matchs the stdev (stdev of samples is less or qual than self.st_dev). False otherwise
        """

        match = False
        if (self.control_input is None) or (not isinstance(self.control_input, tuple)) or (len(self.control_input) < 2):
            pass
        else:
            st_dev = statistics.stdev(self.control_input)
            if st_dev <= self.st_dev:
                match = True
        return match

    def update_control_input(self, control_input):
        """updates the control input data"""
        if (self.control_input is None) or (not isinstance(self.control_input, tuple)) or (len(self.control_input) < 2):
            pass
        else:
            self.control_input = control_input

    def start(self):
        """starts the control"""
        pass