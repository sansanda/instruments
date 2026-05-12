import abc

from drivers.ovens.Ovens import Oven_I

class Tempearture_Profile_Runner_I(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'hasnext') and
                callable(subclass.hasnext) and
                hasattr(subclass, 'reset') and
                callable(subclass.reset) and
                hasattr(subclass, 'next') and
                callable(subclass.next) or
                NotImplemented)

    @abc.abstractmethod
    def hasnext(self):
        """Ask if there is another step in the temperature profile"""
        raise NotImplementedError

    @abc.abstractmethod
    def next(self):
        """Set the oven SP to the next point of the temperature profile"""
        raise NotImplementedError

    @abc.abstractmethod
    def reset(self):
        """Set the oven SP to the first point of the temperature profile"""
        raise NotImplementedError

class Tempearture_Profile_Runner(Tempearture_Profile_Runner_I):
    """A concrete temperature profile runner"""

    def __init__(self, temperature_profile=[0], oven=Oven_I):
        self.temperature_profile = temperature_profile
        self.oven = oven
        self.temperature_profile_index = -1

    def hasnext(self):
        """Ask if there is another step in the temperature profile"""
        hasNext = False
        if self.temperature_profile_index <= (len(self.temperature_profile)-2):
            hasNext = True
        return hasNext

    def next(self):
        self.temperature_profile_index = self.temperature_profile_index + 1
        if self.temperature_profile_index >= len(self.temperature_profile): return
        self.oven.update_temperatureSP(self.temperature_profile[self.temperature_profile_index])

    def reset(self):
        self.temperature_profile_index = -1