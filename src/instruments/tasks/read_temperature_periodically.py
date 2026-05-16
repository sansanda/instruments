from threading import Thread
from time import sleep

class read_temperature_periodically_task(Thread):
    def __init__(self, threadname, thermometer, temperatures_q, period_secs=1):
        self.thermometer = thermometer
        self.temperatures_q = temperatures_q
        self.period_secs = period_secs
        Thread.__init__(self, name=threadname)

    def run(self):
        while(True):
            t = self.thermometer.read_temperature()
            self.temperatures_q.put(t)
            sleep(self.period_secs)
