import abc
import time
from threading import Thread

class Delay_Factory():

    DELAY_TIME = "TIME"
    DELAY_STDEV = "STDEV"

    def getDelay(type, params):
        delayer = Delay_Factory.__get_delayer(type)
        return delayer(params)

    def __get_delayer(type):
        if type == Delay_Factory.DELAY_TIME:
            return Delay_Factory.__getTimeDelay
        elif type == Delay_Factory.DELAY_STDEV:
            return Delay_Factory.__getStDevDelay
        else:
            raise ValueError(format)

    def __getTimeDelay(delay_params):
        return Time_Delay("time_delay", delay_params[0])

    def __getStDevDelay(delay_params):
        return Temperature_StDev_Delay("temperature_st_delay", delay_params[0])

class Delay_I(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'pause') and
                callable(subclass.pause) and
                hasattr(subclass, 'resume') and
                callable(subclass.resume) and
                hasattr(subclass, 'abort') and
                callable(subclass.abort) and
                hasattr(subclass, 'reset') and
                callable(subclass.reset) or
                NotImplemented)

    @abc.abstractmethod
    def pause(self):
        """Pauses the delays"""
        raise NotImplementedError

    @abc.abstractmethod
    def resume(self):
        """Resumes the delays"""
        raise NotImplementedError

    @abc.abstractmethod
    def abort(self):
        """Abort the delays"""
        raise NotImplementedError

    @abc.abstractmethod
    def reset(self):
        """reset the delays"""
        raise NotImplementedError

class Time_Delay(Delay_I, Thread):

    def __init__(self, threadname, mseconds):
        self.delay_mseconds = mseconds
        self.paused = False
        self.aborted = False

        Thread.__init__(self, name=threadname)

    def run(self):
        #Aqui debemos hacer un bucle while true con chequeo de pause, resume y abort
        #Este será un metodo sincrono
        self.reference = int(round(time.time() * 1000))
        actual = self.reference
        while actual < (self.reference + self.delay_mseconds):
            if self.aborted:
                self.aborted = False
                continue
            if not self.paused:
                actual = int(round(time.time() * 1000))
        return

    def pause(self):
        """Pauses the delays"""
        self.paused = True

    def resume(self):
        """Resumes the delays"""
        self.paused = False

    def abort(self):
        """Abort the delays"""
        self.aborted = True

    def reset(self):
        """Reset the delays"""
        self.reference = int(round(time.time() * 1000))

class Temperature_StDev_Delay(Delay_I, Thread):

    def __init__(self, stdev):
        self.stdev = stdev

    def run(self):
        pass

    def pause(self):
        """Pauses the delays"""
        pass

    def resume(self):
        """Resumes the delays"""
        pass

    def abort(self):
        """Abort the delays"""
        pass

    def reset(self):
        """Reset the delays"""
        pass
