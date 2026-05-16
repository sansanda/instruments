from threading import Thread
from time import sleep

from src.instruments.interfaces.interfaces import (
    OvenInterface
)


class FakeOven(
    Thread,
    OvenInterface
):
    """
    Simulador simple de horno programable.

    Este fake oven simula:
    - dinámica térmica básica,
    - setpoint programable,
    - evolución gradual de temperatura.

    Diseñado para:
    - testing,
    - desarrollo offline,
    - simulaciones,
    - pruebas de rampas térmicas.

    Notes
    -----
    La dinámica térmica implementada es extremadamente
    simplificada y no representa un modelo físico real.

    Examples
    --------
    >>> oven = FakeOven()

    >>> oven.start()

    >>> oven.temperature_setpoint = 100

    >>> print(oven.temperature)
    """

    # =========================================================
    # INIT
    # =========================================================

    def __init__(
            self,
            thread_name: str = "fake_oven",
            period_secs: float = 1.0,
            initial_temperature: float = 25.0
    ):
        """
        Inicializa fake oven.

        Parameters
        ----------
        thread_name : str, optional
            Nombre del thread.

        period_secs : float, optional
            Periodo de actualización.

        initial_temperature : float, optional
            Temperatura inicial.
        """

        super().__init__(
            name=thread_name,
            daemon=True
        )

        self._connected = True

        self.period_secs = period_secs

        self._temperature = initial_temperature

        self._temperature_setpoint = (
            initial_temperature
        )

        self.time = 0.0

        self._running = True

    # =========================================================
    # THREAD
    # =========================================================

    def run(self):
        """
        Loop principal de simulación térmica.
        """

        while self._running:

            sleep(self.period_secs)

            self.time += self.period_secs

            # Modelo térmico simple
            self._temperature += (
                self._temperature_setpoint
                - self._temperature
            ) * 0.01

    # =========================================================
    # CONNECTION
    # =========================================================

    @property
    def connected(self) -> bool:
        """
        Estado de conexión.
        """

        return self._connected

    def connect(self):
        """
        Simula conexión del horno.
        """

        self._connected = True

    def disconnect(self):
        """
        Simula desconexión del horno.
        """

        self._connected = False

        self._running = False

    # =========================================================
    # IDENTIFICATION
    # =========================================================

    def idn(self) -> str:
        """
        Identificación simulada.

        Returns
        -------
        str
            ID simulada.
        """

        return (
            "FakeOven,"
            "VirtualThermalSystem,"
            "0001,"
            "1.0"
        )

    # =========================================================
    # RESET
    # =========================================================

    def reset(self):
        """
        Resetea estado del horno.
        """

        self._temperature_setpoint = 25.0

    # =========================================================
    # TEMPERATURE SETPOINT
    # =========================================================

    @property
    def temperature_setpoint(self) -> float:
        """
        Setpoint actual.
        """

        return self._temperature_setpoint

    @temperature_setpoint.setter
    def temperature_setpoint(
            self,
            temperature: float
    ):
        """
        Configura setpoint.
        """

        self._temperature_setpoint = temperature

    # =========================================================
    # TEMPERATURE
    # =========================================================

    @property
    def temperature(self) -> float:
        """
        Temperatura actual.

        Returns
        -------
        float
            Temperatura simulada.
        """

        return self._temperature