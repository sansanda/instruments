from src.instruments.data_logging.temperature_data_loggers import TemperatureDataLogger
from src.instruments.data_structures.Observable_List import Observable_List
from src.instruments.delays.delay import Delay_Factory
from instruments.temperature.TCal import TCal
from src.instruments.drivers.ovens.Ovens import FakeOven
import sys


def main():
    fakeOven = FakeOven("fakeOven")
    ovenThermometer = fakeOven

    sampling_period_in_seconds = 1

    process_temperatures_list = Observable_List(None)
    stDev_temperatures_list = Observable_List(None)
    temperature_buffers = [process_temperatures_list, stDev_temperatures_list]

    temperature_data_logger = TemperatureDataLogger("temperature_data_logger",
                                                    ovenThermometer,
                                                    sampling_period_in_seconds,
                                                    temperature_buffers
                                                    )

    time_delay_params = [12000]
    # 120000 in milliseconds

    stdev_delay_params = (stDev_temperatures_list, 0.01, 120, 2, True)
    # stDev_temperatures_list --> Is the buffer which contains the temperatures
    # 0.01 --> stdev,
    # 120 --> nSamples for calculating the stdev,
    # 2 --> repetitions to match the delay,
    # True --> reset repetitions counter if not match the stdev (then repetitions must be consecutive)

    delay_type = Delay_Factory.DELAY_TIME

    multimeter = None
    results_file = None
    tCal = TCal("TCal", [100, 125, 150, 175, 200], fakeOven, delay_type, time_delay_params, multimeter, results_file)
    temperature_data_logger.start()
    tCal.start()


if __name__ == '__main__':
    sys.exit(main())  # next section explains the use of sys.exit
