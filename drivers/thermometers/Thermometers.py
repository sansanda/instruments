from logger_and_messages.printing_messages import print_message
import numpy as np
import abc


class Thermometer_I(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'read_temperature') and
                callable(subclass.read_temperature) or
                NotImplemented)

    @abc.abstractmethod
    def read_temperature(self):
        """Load in the data set"""
        raise NotImplementedError


class FakeThermometer(Thermometer_I):
    """A concrete thermometer"""

    def __init__(self, mu, sigma):
        self.mu = mu
        self.sigma = sigma

    def read_temperature(self):
        print_message("Reading Temperature....", "*", "*")
        return float(np.random.normal(self.mu, self.sigma, 1))

    def plug_transducer(self, transducer='4WRTD', channel=0):
        self.temp_transducer = transducer
        self.channel = channel

    def updateParameters(self,mu, sigma):
        self.mu = mu
        self.sigma = sigma

    def getParameters(self):
        return (self.mu, self.sigma)