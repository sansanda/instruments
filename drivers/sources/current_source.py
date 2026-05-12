from abc import ABC
from drivers.SCPIInstrument import SCPIInstrument
from drivers.sources.source_instrument import SourceInstrument


class CurrentSource(SourceInstrument):
    """
    Clase base abstracta para fuentes de corriente controladas mediante SCPI.

    Esta clase define la interfaz común que deben implementar todos los
    instrumentos capaces de generar corriente programable, como SMUs,
    fuentes de alimentación o generadores de corriente.

    Las clases derivadas deben sobrescribir todos los métodos para adaptar
    la comunicación al hardware específico.

    Si un método no es implementado en una clase hija y se invoca,
    se lanzará una excepción ``NotImplementedError``.
    """

    def set_current(self, current: float):
        """
        Configura el valor de corriente de salida.

        Parameters
        ----------
        current : float
            Corriente de salida en amperios.

        Raises
        ------
        NotImplementedError
            Si el método no ha sido implementado por la clase derivada.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__}.set_current() no implementado"
        )

    def get_current(self) -> float:
        """
        Obtiene el valor actual de corriente configurado o medido.

        Returns
        -------
        float
            Corriente en amperios.

        Raises
        ------
        NotImplementedError
            Si el método no ha sido implementado por la clase derivada.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__}.get_current() no implementado"
        )