from abc import ABC

from drivers.SCPIInstrument import SCPIInstrument
from drivers.sources.source_instrument import SourceInstrument


class VoltageSource(SourceInstrument):
    """
    Clase base abstracta para fuentes de tensión controladas mediante SCPI.

    Esta clase define la interfaz común que deben implementar todos los
    instrumentos capaces de generar tensión programable, como SMUs,
    fuentes de alimentación o generadores de tensión.

    Las clases derivadas deben sobrescribir todos los métodos para adaptar
    la comunicación al hardware específico.

    Si un método no es implementado en una clase hija y se invoca,
    se lanzará una excepción ``NotImplementedError``.
    """

    def set_voltage(self, voltage: float):
        """
        Configura el valor de tensión de salida.

        Parameters
        ----------
        voltage : float
            Tensión de salida en voltios.

        Raises
        ------
        NotImplementedError
            Si el método no ha sido implementado por la clase derivada.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__}.set_voltage() no implementado"
        )

    def get_voltage(self) -> float:
        """
        Obtiene el valor actual de tensión configurado o medido.

        Returns
        -------
        float
            Tensión en voltios.

        Raises
        ------
        NotImplementedError
            Si el método no ha sido implementado por la clase derivada.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__}.get_voltage() no implementado"
        )