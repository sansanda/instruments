from ..drivers.electronic_loads.electronic_loads import (
    HPElectronicLoad6060B,
    ElectronicLoadInterface
)


class FakeHPElectronicLoad6060B(
    ElectronicLoadInterface,
    HPElectronicLoad6060B
):
    """
    Fake instrument para HP 6060B.

    Esta clase simula el comportamiento interno de la carga
    electrónica HP / Agilent 6060B sin necesidad de hardware
    real ni comunicación VISA.

    Diseñada para:
    - Tests unitarios
    - Tests de integración
    - Desarrollo offline
    - Simulación SCPI

    Características
    ---------------
    - Mantiene estado interno
    - Simula respuestas SCPI
    - Guarda comandos enviados
    - Valida parámetros
    - Simula medidas

    Notes
    -----
    No llama al constructor VISA real para evitar acceso
    a hardware físico.

    Examples
    --------
    >>> load = FakeHPElectronicLoad6060B()

    >>> load.configure_cc(
    ...     current=5,
    ...     current_range=60
    ... )

    >>> print(load.current)
    5

    >>> print(load.commands)
    ['MODE CURR', 'CURR:RANG 60', 'CURR 5']
    """

    # =========================================================
    # INIT
    # =========================================================

    def __init__(self):
        """
        Inicializa el fake instrument.

        Se crean variables internas para almacenar el estado
        simulado del instrumento.

        Examples
        --------
        >>> load = FakeHPElectronicLoad6060B()
        """

        # NO llamar super().__init__()
        # para evitar VISA real

        self._mode = self.MODE_CC

        self._current = 0.0
        self._voltage = 0.0
        self._power = 0.0
        self._resistance = 1.0

        self._current_range = 60

        self._current_slew_rate = 1.0

        self._trigger_source = self.TRIGGER_BUS

        self._input_enabled = False

        self._measured_voltage = 0.0
        self._measured_current = 0.0
        self._measured_power = 0.0

        self.commands = []

    # =========================================================
    # LOW LEVEL SCPI
    # =========================================================

    def write(self, command: str):
        """
        Simula escritura SCPI.

        Parameters
        ----------
        command : str
            Comando SCPI enviado.

        Notes
        -----
        El comando queda almacenado en `commands`.

        Examples
        --------
        >>> load.write("CURR 5")
        """

        self.commands.append(command)

    def query(self, command: str) -> str:
        """
        Simula consulta SCPI de texto.

        Parameters
        ----------
        command : str
            Consulta SCPI.

        Returns
        -------
        str
            Respuesta simulada.

        Examples
        --------
        >>> mode = load.query("MODE?")
        """

        self.commands.append(command)

        mapping = {
            "MODE?": self._mode,
            "TRIG:SOUR?": self._trigger_source
        }

        return mapping.get(command, "")

    def query_float(self, command: str) -> float:
        """
        Simula consulta SCPI numérica.

        Parameters
        ----------
        command : str
            Consulta SCPI.

        Returns
        -------
        float
            Valor numérico simulado.

        Examples
        --------
        >>> current = load.query_float("CURR?")
        """

        self.commands.append(command)

        mapping = {
            "CURR?": self._current,
            "VOLT?": self._voltage,
            "POW?": self._power,
            "RES?": self._resistance,
            "CURR:RANG?": self._current_range,
            "CURR:SLEW?": self._current_slew_rate,
            "MEAS:VOLT?": self._measured_voltage,
            "MEAS:CURR?": self._measured_current,
            "MEAS:POW?": self._measured_power
        }

        return mapping.get(command, 0.0)

    # =========================================================
    # MODE
    # =========================================================

    @property
    def mode(self):
        """
        Modo de funcionamiento actual.

        Returns
        -------
        str
            Modo SCPI actual.

        Examples
        --------
        >>> print(load.mode)
        CURR
        """

        return self._mode

    @mode.setter
    def mode(self, value):
        """
        Configura modo de funcionamiento.

        Parameters
        ----------
        value : str
            Modo SCPI.

        Valores válidos
        ----------------
        - CURR
        - VOLT
        - RES
        - POW

        Examples
        --------
        >>> load.mode = load.MODE_CC
        """

        value = value.upper()

        if value not in self.VALID_MODES:
            raise ValueError(
                f"Invalid mode: {value}"
            )

        self._mode = value

        self.write(f"MODE {value}")

    # =========================================================
    # CURRENT
    # =========================================================

    @property
    def current(self):
        """
        Corriente programada.

        Returns
        -------
        float
            Corriente en amperios.
        """

        return self._current

    @current.setter
    def current(self, value):
        """
        Configura corriente.

        Parameters
        ----------
        value : float
            Corriente en amperios.

        Examples
        --------
        >>> load.current = 5
        """

        self._current = value

        self.write(f"CURR {value}")

    # =========================================================
    # VOLTAGE
    # =========================================================

    @property
    def voltage(self):
        """
        Voltaje programado.

        Returns
        -------
        float
            Voltaje en voltios.
        """

        return self._voltage

    @voltage.setter
    def voltage(self, value):
        """
        Configura voltaje.

        Parameters
        ----------
        value : float
            Voltaje en voltios.

        Examples
        --------
        >>> load.voltage = 12
        """

        self._voltage = value

        self.write(f"VOLT {value}")

    # =========================================================
    # POWER
    # =========================================================

    @property
    def power(self):
        """
        Potencia programada.

        Returns
        -------
        float
            Potencia en vatios.
        """

        return self._power

    @power.setter
    def power(self, value):
        """
        Configura potencia.

        Parameters
        ----------
        value : float
            Potencia en vatios.

        Examples
        --------
        >>> load.power = 100
        """

        self._power = value

        self.write(f"POW {value}")

    # =========================================================
    # RESISTANCE
    # =========================================================

    @property
    def resistance(self):
        """
        Resistencia programada.

        Returns
        -------
        float
            Resistencia en ohmios.
        """

        return self._resistance

    @resistance.setter
    def resistance(self, value):
        """
        Configura resistencia.

        Parameters
        ----------
        value : float
            Resistencia en ohmios.

        Examples
        --------
        >>> load.resistance = 10
        """

        self._resistance = value

        self.write(f"RES {value}")

    # =========================================================
    # CURRENT RANGE
    # =========================================================

    @property
    def current_range(self):
        """
        Rango de corriente activo.

        Returns
        -------
        int
            Rango de corriente.
        """

        return self._current_range

    @current_range.setter
    def current_range(self, value):
        """
        Configura rango de corriente.

        Parameters
        ----------
        value : int
            Rango deseado.

        Valores válidos
        ----------------
        - 6
        - 60

        Examples
        --------
        >>> load.current_range = 60
        """

        if value not in self.VALID_CURRENT_RANGES:
            raise ValueError(
                f"Invalid current range: {value}"
            )

        self._current_range = value

        self.write(f"CURR:RANG {value}")

    # =========================================================
    # CURRENT SLEW RATE
    # =========================================================

    @property
    def current_slew_rate(self):
        """
        Slew rate de corriente.

        Returns
        -------
        float
            Slew rate en A/us.
        """

        return self._current_slew_rate

    @current_slew_rate.setter
    def current_slew_rate(self, value):
        """
        Configura slew rate.

        Parameters
        ----------
        value : float
            Slew rate en A/us.

        Examples
        --------
        >>> load.current_slew_rate = 2.0
        """

        self._current_slew_rate = value

        self.write(f"CURR:SLEW {value}")

    # =========================================================
    # TRIGGER SOURCE
    # =========================================================

    @property
    def trigger_source(self):
        """
        Fuente de trigger actual.

        Returns
        -------
        str
            Fuente de trigger.
        """

        return self._trigger_source

    @trigger_source.setter
    def trigger_source(self, value):
        """
        Configura fuente de trigger.

        Parameters
        ----------
        value : str
            Fuente de trigger.

        Valores válidos
        ----------------
        - BUS
        - IMM
        - EXT

        Examples
        --------
        >>> load.trigger_source = load.TRIGGER_BUS
        """

        value = value.upper()

        if value not in self.VALID_TRIGGER_SOURCES:
            raise ValueError(
                f"Invalid trigger source: {value}"
            )

        self._trigger_source = value

        self.write(f"TRIG:SOUR {value}")

    # =========================================================
    # INPUT
    # =========================================================

    @property
    def input_enabled(self):
        """
        Estado del input.

        Returns
        -------
        bool
            True si el input está activo.
        """

        return self._input_enabled

    @input_enabled.setter
    def input_enabled(self, value):
        """
        Activa o desactiva el input.

        Parameters
        ----------
        value : bool
            Estado deseado.

        Examples
        --------
        >>> load.input_enabled = True
        """

        self._input_enabled = bool(value)

        command = "INPUT ON" if value else "INPUT OFF"

        self.write(command)

    # =========================================================
    # MEASUREMENTS
    # =========================================================

    @property
    def measured_voltage(self):
        """
        Voltaje medido.

        Returns
        -------
        float
            Voltaje medido en voltios.
        """

        return self._measured_voltage

    @property
    def measured_current(self):
        """
        Corriente medida.

        Returns
        -------
        float
            Corriente medida en amperios.
        """

        return self._measured_current

    @property
    def measured_power(self):
        """
        Potencia medida.

        Returns
        -------
        float
            Potencia medida en vatios.
        """

        return self._measured_power

    # =========================================================
    # TEST HELPERS
    # =========================================================

    def set_measurements(
            self,
            voltage: float,
            current: float,
            power: float
    ):
        """
        Configura medidas simuladas.

        Parameters
        ----------
        voltage : float
            Voltaje simulado.

        current : float
            Corriente simulada.

        power : float
            Potencia simulada.

        Examples
        --------
        >>> load.set_measurements(
        ...     voltage=12,
        ...     current=5,
        ...     power=60
        ... )
        """

        self._measured_voltage = voltage
        self._measured_current = current
        self._measured_power = power

    # =========================================================
    # UTILITIES
    # =========================================================

    def trigger(self):
        """
        Simula trigger manual.

        Examples
        --------
        >>> load.trigger()
        """

        self.write("*TRG")

    def reset(self):
        """
        Simula reset del instrumento.

        Examples
        --------
        >>> load.reset()
        """

        self.write("*RST")

    def clear(self):
        """
        Simula clear del instrumento.

        Examples
        --------
        >>> load.clear()
        """

        self.write("*CLS")