from abc import ABC

from drivers.SCPIInstrument import SCPIInstrument


class SourceInstrument(SCPIInstrument, ABC):
    """
    Clase base abstracta para instrumentos fuente controlados mediante SCPI.

    Esta clase encapsula la funcionalidad común de instrumentos capaces
    de generar una salida programable, como fuentes de tensión,
    fuentes de corriente o SMUs.

    Proporciona métodos comunes para controlar el estado de la salida.
    Las clases derivadas deben implementar la lógica específica del
    instrumento y del tipo de magnitud generada.

    Si un método no es implementado en una clase hija y se invoca,
    se lanzará una excepción ``NotImplementedError``.
    """

    def output_on(self):
        """
        Activa la salida del instrumento.

        Raises
        ------
        NotImplementedError
            Si el método no ha sido implementado por la clase derivada.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__}.output_on() no implementado"
        )

    def output_off(self):
        """
        Desactiva la salida del instrumento.

        Raises
        ------
        NotImplementedError
            Si el método no ha sido implementado por la clase derivada.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__}.output_off() no implementado"
        )