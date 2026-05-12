from logger_and_messages.printing_messages import print_message

import abc

from others.Control import Control_I

class Sweep_I(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'start') and
                callable(subclass.start) and
                hasattr(subclass, 'reset') and
                callable(subclass.reset) and
                hasattr(subclass, 'next') and
                callable(subclass.next) and
                hasattr(subclass, 'previous') and
                callable(subclass.previous) or
                NotImplemented)

    @abc.abstractmethod
    def start(self):
        """Starts the sweep"""
        raise NotImplementedError

    @abc.abstractmethod
    def reset(self):
        """Set the oven SP to the first point of the temperature profile"""
        raise NotImplementedError

    @abc.abstractmethod
    def next(self):
        """Set the oven SP to the next point of the temperature profile"""
        raise NotImplementedError

    @abc.abstractmethod
    def previous(self):
        """Set the oven SP to the previous point of the temperature profile"""
        raise NotImplementedError

class Tempearture_Sweep(Sweep_I):
    """A concrete temperature sweep"""

    def __init__(self, temperature_profile=[0], control=Control_I):
        self.temperature_profile = temperature_profile
        self.temperature_profile_index = 0
        self.control = control

    def start(self):
        print_message("Starting Temperature Sweep from Zero", "*", "*")
        self.reset()
        self.oven.update_temperatureSP(self.temperature_profile[self.temperature_profile_index])
        self.control.start()

    def reset(self):
        self.temperature_profile_index = 0

    def next(self):
        if (self.temperature_profile_index + 1) >= len(self.temperature_profile):
            pass
        else:
            self.temperature_profile_index = self.temperature_profile_index + 1
            self.oven.update_temperatureSP(self.temperature_profile[self.temperature_profile_index])

    def previous(self):
        if self.temperature_profile_index <= 0:
            pass
        else:
            self.temperature_profile_index = self.temperature_profile_index - 1
            self.oven.update_temperatureSP(self.temperature_profile[self.temperature_profile_index])

    def get_actual_temp_step(self):
        return self.temperature_profile[self.temperature_profile_index]
