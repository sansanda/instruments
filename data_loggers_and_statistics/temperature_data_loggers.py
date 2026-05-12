from threading import Thread, Event
from time import sleep

from logger_and_messages.printing_messages import print_message
from drivers.thermometers.Thermometers import Thermometer_I

import abc


class Temperature_Data_Logger_I(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'update_sampling_period') and
                callable(subclass.update_sampling_period) and
                hasattr(subclass, 'get_sampling_period') and
                callable(subclass.get_sampling_period) or
                NotImplemented)

    @abc.abstractmethod
    def update_sampling_period(self, period_in_secs=1):
        """Set the temperature reading period"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_sampling_period(self):
        """Returns the temperature sampling peiod"""
        raise NotImplementedError


class TemperatureDataLogger(Temperature_Data_Logger_I, Thread):
    """A concrete thermometer"""

    def __init__(self, threadname="temperature_data_logger",
                 thermometer=Thermometer_I,
                 sampling_period_secs=1,
                 sampling_buffers=None):

        self.sampling_period = sampling_period_secs  # seconds
        self.thermometer = thermometer
        self.sampling_buffers = list()

        if sampling_buffers is not None:
            self.sampling_buffers.append(sampling_buffers)

        self.time = 0

        # For managing pause and resume the data_logger
        self.can_run = Event()
        self.can_run.set()

        Thread.__init__(self, name=threadname)

    def addEvent(self, buffer, event):
        """
        Add at event to an specific buffer
        :param buffer: Observable List
        :param event: str with the name of the event
        :return: None
        """
        if buffer in self.sampling_buffers:
            self.buffer.addEvent(event)

    def update_sampling_period(self, sampling_period_in_secs=1):
        """Set the temperature reading period"""
        self.sampling_period = sampling_period_in_secs

    def get_sampling_period(self):
        """Returns the temperature sampling peiod"""
        return self.sampling_period

    def run(self):
        print_message("Starting Temperature Data Logger...", "*", "*")
        while True:
            self.can_run.wait()
            for buffer in self.sampling_buffers:
                buffer.append(self.thermometer.read_temperature())
            self.time = self.time + self.sampling_period
            sleep(self.sampling_period)

    def pause(self):
        self.can_run.clear()

    def resume(self):
        self.can_run.set()
