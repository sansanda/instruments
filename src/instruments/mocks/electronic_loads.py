from instruments.interfaces.interfaces import (
    ElectronicLoadInterface
)

class FakeHPElectronicLoad6060B(
    ElectronicLoadInterface
):
    """
    Simulador de carga electrónica HP 6060B.

    Diseñado para:
    - testing,
    - desarrollo offline,
    - integración continua,
    - simulación básica.

    Notes
    -----
    Este fake NO implementa:
    - VISA,
    - SCPI real,
    - timing real,
    - comportamiento físico avanzado.

    Simula únicamente:
    - almacenamiento de configuración,
    - medidas simples derivadas,
    - estados internos.
    """

    # =========================================================
    # CONSTANTS
    # =========================================================

    MODE_CC = "CURR"
    MODE_CV = "VOLT"
    MODE_CR = "RES"
    MODE_CP = "POW"

    VALID_MODES = [
        MODE_CC,
        MODE_CV,
        MODE_CR,
        MODE_CP
    ]

    TRIGGER_BUS = "BUS"
    TRIGGER_IMMEDIATE = "IMM"
    TRIGGER_EXTERNAL = "EXT"

    VALID_TRIGGER_SOURCES = [
        TRIGGER_BUS,
        TRIGGER_IMMEDIATE,
        TRIGGER_EXTERNAL
    ]

    VALID_CURRENT_RANGES = [6, 60]

    # =========================================================
    # INIT
    # =========================================================

    def __init__(self):
        """
        Inicializa fake electronic load.
        """

        self._connected = True

        self._output_enabled = False

        self._mode = self.MODE_CC

        self._current = 0.0

        self._voltage = 0.0

        self._power = 0.0

        self._resistance = 1.0

        self._current_range = 60

        self._current_slew_rate = 1.0

        self._trigger_source = (
            self.TRIGGER_BUS
        )

    # =========================================================
    # CONNECTION
    # =========================================================

    @property
    def connected(self) -> bool:

        return self._connected

    def connect(self):

        self._connected = True

    def disconnect(self):

        self._connected = False

    # =========================================================
    # IDENTIFICATION
    # =========================================================

    def idn(self) -> str:

        return (
            "HEWLETT-PACKARD,"
            "6060B,"
            "FAKE0001,"
            "1.0"
        )

    # =========================================================
    # RESET
    # =========================================================

    def reset(self):

        self.set_default_configuration()

    # =========================================================
    # OUTPUT
    # =========================================================

    @property
    def output_enabled(self) -> bool:

        return self._output_enabled

    @output_enabled.setter
    def output_enabled(
            self,
            value: bool
    ):

        self._output_enabled = bool(value)

    def output_on(self):

        self.output_enabled = True

    def output_off(self):

        self.output_enabled = False

    # =========================================================
    # MODE
    # =========================================================

    @property
    def mode(self) -> str:

        return self._mode

    @mode.setter
    def mode(self, value: str):

        value = value.upper()

        if value not in self.VALID_MODES:

            raise ValueError(
                f"Invalid mode: {value}"
            )

        self._mode = value

    # =========================================================
    # CURRENT
    # =========================================================

    @property
    def current(self) -> float:

        return self._current

    @current.setter
    def current(self, value: float):

        self._current = float(value)

    # =========================================================
    # VOLTAGE
    # =========================================================

    @property
    def voltage(self) -> float:

        return self._voltage

    @voltage.setter
    def voltage(self, value: float):

        self._voltage = float(value)

    # =========================================================
    # POWER
    # =========================================================

    @property
    def power(self) -> float:

        return self._power

    @power.setter
    def power(self, value: float):

        self._power = float(value)

    # =========================================================
    # RESISTANCE
    # =========================================================

    @property
    def resistance(self) -> float:

        return self._resistance

    @resistance.setter
    def resistance(self, value: float):

        self._resistance = float(value)

    # =========================================================
    # CURRENT RANGE
    # =========================================================

    @property
    def current_range(self) -> float:

        return self._current_range

    @current_range.setter
    def current_range(self, value: int):

        if value not in self.VALID_CURRENT_RANGES:

            raise ValueError(
                f"Invalid current range: {value}"
            )

        self._current_range = value

    # =========================================================
    # CURRENT SLEW RATE
    # =========================================================

    @property
    def current_slew_rate(self) -> float:

        return self._current_slew_rate

    @current_slew_rate.setter
    def current_slew_rate(
            self,
            value: float
    ):

        self._current_slew_rate = float(value)

    # =========================================================
    # TRIGGER SOURCE
    # =========================================================

    @property
    def trigger_source(self) -> str:

        return self._trigger_source

    @trigger_source.setter
    def trigger_source(self, value: str):

        value = value.upper()

        if value not in (
                self.VALID_TRIGGER_SOURCES
        ):

            raise ValueError(
                f"Invalid trigger source: {value}"
            )

        self._trigger_source = value

    # =========================================================
    # MEASUREMENTS
    # =========================================================

    @property
    def measured_voltage(self) -> float:

        return self._voltage

    @property
    def measured_current(self) -> float:

        return self._current

    @property
    def measured_power(self) -> float:

        return (
            self._voltage
            * self._current
        )

    # =========================================================
    # QUICK CONFIGURATION
    # =========================================================

    def configure_cc(
            self,
            current: float,
            current_range: int = 60
    ):

        self.mode = self.MODE_CC

        self.current_range = current_range

        self.current = current

    def configure_cv(
            self,
            voltage: float
    ):

        self.mode = self.MODE_CV

        self.voltage = voltage

    def configure_cr(
            self,
            resistance: float
    ):

        self.mode = self.MODE_CR

        self.resistance = resistance

    def configure_cp(
            self,
            power: float
    ):

        self.mode = self.MODE_CP

        self.power = power

    # =========================================================
    # UTILITIES
    # =========================================================

    def set_default_configuration(
            self,
            current_range: int = 60,
            slew_rate: float = 1.0,
            current: float = 0.0
    ):

        self.mode = self.MODE_CC

        self.current_range = current_range

        self.current_slew_rate = slew_rate

        self.current = current

        self.output_enabled = False