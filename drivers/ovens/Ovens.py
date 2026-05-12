import sys
from threading import Thread
from time import sleep

from logger_and_messages.printing_messages import print_message
from drivers.thermometers.Thermometers import Thermometer_I

import abc

# TODO: Seria más correcto llamar a Oven_I de otra manera. realmente lo que queremos decir es cualquier equipo al
#  cual se le pueda settear la temperatura

class Oven_I(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'update_temperatureSP') and
                callable(subclass.update_temperatureSP) and
                hasattr(subclass, 'get_temperatureSP') and
                callable(subclass.get_temperatureSP) or
                NotImplemented)

    @abc.abstractmethod
    def update_temperatureSP(self, temperature=0):
        """Load in the data set"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_temperatureSP(self):
        """Load in the data set"""
        raise NotImplementedError

class FakeOven(Oven_I, Thermometer_I, Thread):
    """A concrete thermometer"""

    def __init__(self, threadname="fake_oven", period_secs=1, actualTemp=0, sigma=1):
        self.actualTemp = actualTemp  # celsius
        self.temperatureSP = actualTemp  # celsius

        self.mu = actualTemp  # celsius
        self.sigma = sigma  # standard deviation

        self.period_secs = period_secs  # second
        self.time = 0

        Thread.__init__(self, name=threadname)

    def run(self):
        print_message("Starting Fake Oven", "*", "*")
        while True:
            #printMessage("Updating oven state....", "*", "*")
            sleep(self.period_secs)
            self.time = self.time + self.period_secs
            self.actualTemp = self.actualTemp + (self.temperatureSP - self.actualTemp) * 0.01

    def update_temperatureSP(self, temperatureSP=0):
        #printMessage("Updating Temperature SP to " + str(temperatureSP) + "ºC. ","*","*")
        self.temperatureSP = temperatureSP
        self.mu = temperatureSP

    def get_temperatureSP(self):
        return self.temperatureSP

    def read_temperature(self):
        print(self.actualTemp)
        return self.actualTemp

    def updateParameters(self, sigma):
        self.sigma = sigma

    def getParameters(self):
        return (self.mu, self.sigma)

def main():
    fakeOven = FakeOven("fakeOven")
    fakeOven.start()
    fakeOven.update_temperatureSP(100)

    while(True):
        sleep(1)
        fakeOven.read_temperature()

if __name__ == '__main__':
    sys.exit(main())  # next section explains the use of sys.exit
