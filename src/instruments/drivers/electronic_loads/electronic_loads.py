"""
HP 6060B Electronic Load Driver.

Driver SCPI para la carga electrónica HP / Agilent 6060B.

Este driver implementa una API Pythonic basada en properties
para facilitar el control del instrumento.

Características
---------------
- Modos:
    * CC (Current)
    * CV (Voltage)
    * CR (Resistance)
    * CP (Power)

- Configuración mediante properties
- Medidas
- Trigger
- Slew rate
- Rango de corriente
- Input ON/OFF

Ejemplos
--------
Modo corriente constante:

>>> load = HPElectronicLoad6060B("GPIB0::5::INSTR")
>>> load.mode = load.MODE_CC
>>> load.current_range = 60
>>> load.current = 5
>>> load.input_enabled = True

Medidas:

>>> voltage = load.measured_voltage
>>> current = load.measured_current
>>> power = load.measured_power

Trigger:

>>> load.trigger_source = load.TRIGGER_BUS
>>> load.trigger()

Modo potencia constante:

>>> load.mode = load.MODE_CP
>>> load.power = 120
"""

from src.instruments.interfaces.interfaces import (
    ElectronicLoadInterface
)

from ..sources.source_instrument import SourceInstrument


class HPElectronicLoad6060B(
    SourceInstrument,
    ElectronicLoadInterface
):
    """
    Driver SCPI para HP / Agilent 6060B.

    Parameters
    ----------
    resource_name : str
        Dirección VISA del instrumento.

    timeout : int, optional
        Timeout VISA en milisegundos.

    read_termination : str, optional
        Terminador VISA de lectura.

    write_termination : str, optional
        Terminador VISA de escritura.
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

    def __init__(
            self,
            resource_name: str,
            timeout: int = 10000,
            read_termination: str = "\n",
            write_termination: str = "\n"
    ):
        """
        Inicializa el driver del instrumento.
        """

        super().__init__(
            resource_name=resource_name,
            timeout=timeout,
            read_termination=read_termination,
            write_termination=write_termination
        )

    # =========================================================
    # MODE
    # =========================================================

    @property
    def mode(self) -> str:
        """
        Modo de funcionamiento actual.

        Returns
        -------
        str
            Modo SCPI actual.
        """

        return self.query("MODE?")

    @mode.setter
    def mode(self, value: str):
        """
        Configura modo de funcionamiento.
        """

        value = value.upper()

        if value not in self.VALID_MODES:
            raise ValueError(
                f"Invalid mode: {value}"
            )

        self.write(f"MODE {value}")

    # =========================================================
    # CURRENT
    # =========================================================

    @property
    def current(self) -> float:
        """
        Corriente programada.

        Returns
        -------
        float
            Corriente en amperios.
        """

        return self.query_float("CURR?")

    @current.setter
    def current(self, value: float):
        """
        Configura corriente.
        """

        self.write(f"CURR {value}")

    # =========================================================
    # VOLTAGE
    # =========================================================

    @property
    def voltage(self) -> float:
        """
        Voltaje programado.

        Returns
        -------
        float
            Voltaje en voltios.
        """

        return self.query_float("VOLT?")

    @voltage.setter
    def voltage(self, value: float):
        """
        Configura voltaje.
        """

        self.write(f"VOLT {value}")

    # =========================================================
    # POWER
    # =========================================================

    @property
    def power(self) -> float:
        """
        Potencia programada.

        Returns
        -------
        float
            Potencia en vatios.
        """

        return self.query_float("POW?")

    @power.setter
    def power(self, value: float):
        """
        Configura potencia.
        """

        self.write(f"POW {value}")

    # =========================================================
    # RESISTANCE
    # =========================================================

    @property
    def resistance(self) -> float:
        """
        Resistencia programada.

        Returns
        -------
        float
            Resistencia en ohmios.
        """

        return self.query_float("RES?")

    @resistance.setter
    def resistance(self, value: float):
        """
        Configura resistencia.
        """

        self.write(f"RES {value}")

    # =========================================================
    # CURRENT RANGE
    # =========================================================

    @property
    def current_range(self) -> float:
        """
        Rango de corriente activo.

        Returns
        -------
        float
            Rango configurado.
        """

        return self.query_float("CURR:RANG?")

    @current_range.setter
    def current_range(self, value: int):
        """
        Configura rango de corriente.
        """

        if value not in self.VALID_CURRENT_RANGES:
            raise ValueError(
                f"Current range must be one of "
                f"{self.VALID_CURRENT_RANGES}"
            )

        self.write(f"CURR:RANG {value}")

    # =========================================================
    # CURRENT SLEW RATE
    # =========================================================

    @property
    def current_slew_rate(self) -> float:
        """
        Slew rate de corriente.

        Returns
        -------
        float
            Slew rate en A/us.
        """

        return self.query_float("CURR:SLEW?")

    @current_slew_rate.setter
    def current_slew_rate(self, value: float):
        """
        Configura slew rate.
        """

        self.write(f"CURR:SLEW {value}")

    # =========================================================
    # TRIGGER SOURCE
    # =========================================================

    @property
    def trigger_source(self) -> str:
        """
        Fuente de trigger actual.

        Returns
        -------
        str
            Fuente de trigger.
        """

        return self.query("TRIG:SOUR?")

    @trigger_source.setter
    def trigger_source(self, value: str):
        """
        Configura fuente de trigger.
        """

        value = value.upper()

        if value not in self.VALID_TRIGGER_SOURCES:
            raise ValueError(
                f"Invalid trigger source: {value}"
            )

        self.write(f"TRIG:SOUR {value}")

    # =========================================================
    # OUTPUT ENABLED
    # =========================================================

    @property
    def output_enabled(self) -> bool:
        """
        Estado del input/output.

        Returns
        -------
        bool
            True si está habilitado.
        """

        response = self.query("INPUT?").strip()

        return response in ["1", "ON"]

    @output_enabled.setter
    def output_enabled(self, value: bool):
        """
        Activa o desactiva input/output.
        """

        command = "INPUT ON" if value else "INPUT OFF"

        self.write(command)

    # =========================================================
    # OUTPUT CONTROL
    # =========================================================

    def output_on(self):
        """
        Activa input/output.
        """

        self.output_enabled = True

    def output_off(self):
        """
        Desactiva input/output.
        """

        self.output_enabled = False

    # =========================================================
    # MEASUREMENTS
    # =========================================================

    @property
    def measured_voltage(self) -> float:
        """
        Voltaje medido.
        """

        return self.query_float("MEAS:VOLT?")

    @property
    def measured_current(self) -> float:
        """
        Corriente medida.
        """

        return self.query_float("MEAS:CURR?")

    @property
    def measured_power(self) -> float:
        """
        Potencia medida.
        """

        return self.query_float("MEAS:POW?")

    # =========================================================
    # QUICK CONFIGURATION
    # =========================================================

    def configure_cc(
            self,
            current: float,
            current_range: int = 60
    ):
        """
        Configuración rápida modo CC.
        """

        self.mode = self.MODE_CC

        self.current_range = current_range

        self.current = current

    def configure_cv(self, voltage: float):
        """
        Configuración rápida modo CV.
        """

        self.mode = self.MODE_CV

        self.voltage = voltage

    def configure_cr(self, resistance: float):
        """
        Configuración rápida modo CR.
        """

        self.mode = self.MODE_CR

        self.resistance = resistance

    def configure_cp(self, power: float):
        """
        Configuración rápida modo CP.
        """

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
        """
        Configuración inicial recomendada.
        """

        self.reset()

        self.clear()

        self.trigger_source = self.TRIGGER_BUS

        self.configure_cc(
            current=current,
            current_range=current_range
        )

        self.current_slew_rate = slew_rate

        self.output_enabled = True