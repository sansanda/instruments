import pyvisa
from pyvisa import Resource
from abc import ABC, abstractmethod

from instruments.interfaces.interfaces import (
    SCPIInstrumentInterface
)


# =========================
# CONSTANTS
# =========================

SUPPORTED_TEMPERATURE_TRANSDUCERS = {
    "TC", "FRTD", "THER"
}

SUPPORTED_TCOUPLES = {
    "J": "Type J (Iron-Constantan)",
    "K": "Type K (Chromel-Alumel)",
    "T": "Type T (Copper-Constantan)",
    "E": "Type E (Chromel-Constantan)",
    "R": "Type R (Platinum-Rhodium)",
    "S": "Type S (Platinum-Rhodium)",
    "B": "Type B (Platinum-Rhodium)",
    "N": "Type N (Nicrosil-Nisil)"
}

SUPPORTED_FRTDS = {
    "PT100": "Platinum RTD 100Ω",
    "D100": "DIN 100Ω RTD",
    "F100": "IEC 100Ω RTD",
    "PT3916": "Platinum RTD (α = 0.003916)",
    "PT385": "Platinum RTD (α = 0.00385)",
    "USER": "User-defined RTD (requires RZERO, ALPHA, BETA, DELTA)"
}

SUPPORTED_FUNCTIONS = {
    "VOLT:DC", "VOLT:AC",
    "CURR:DC", "CURR:AC",
    "RES", "FRES",
    "TEMP",
    "FREQ", "PER",
    "CONT"
}

SUPPORTED_AVG = [
    "VOLT:DC",
    "VOLT:AC",
    "CURR:DC",
    "CURR:AC",
    "RES",
    "FRES",
    "TEMP"
]

SUPPORTED_TCON = ["REP", "MOV"]  # Repeating / Moving

PARAM_MAP = {
    "nplc": "NPLC",
    "range": "RANG",
    "autorange": "RANG:AUTO",
    "digits": "DIG",
    "offset_comp": "OCOM",
    "tran": "TRAN",
    "frtd_type": "FRTD:TYPE"
}



class SCPIInstrument(SCPIInstrumentInterface):
    """
    Clase base para instrumentos compatibles con SCPI.

    Esta clase implementa:
    - conexión VISA,
    - comunicación SCPI,
    - helpers SCPI,
    - comandos IEEE-488.2,
    - manejo de errores.

    Diseñada para ser heredada por drivers concretos:
    - Keithley2400
    - Keithley2700
    - HP6060B
    - etc.

    Notes
    -----
    La conexión NO se establece automáticamente en el
    constructor. Debe llamarse explícitamente a connect().

    Examples
    --------
    >>> inst = SCPIInstrument(
    ...     "GPIB0::5::INSTR"
    ... )

    >>> inst.connect()

    >>> print(inst.idn())

    >>> inst.disconnect()
    """

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
        Inicializa instrumento SCPI.

        Parameters
        ----------
        resource_name : str
            Dirección VISA.

        timeout : int, optional
            Timeout VISA en milisegundos.

        read_termination : str, optional
            Terminador de lectura.

        write_termination : str, optional
            Terminador de escritura.
        """

        self.resource_name = resource_name

        self._timeout = timeout

        self.read_termination = read_termination
        self.write_termination = write_termination

        self.rm = pyvisa.ResourceManager()

        self.inst: Resource | None = None

    # =========================================================
    # CONNECTION
    # =========================================================

    @property
    def connected(self) -> bool:
        """
        Estado de conexión.

        Returns
        -------
        bool
            True si el instrumento está conectado.
        """

        return self.inst is not None

    def connect(self):
        """
        Establece conexión VISA.

        Examples
        --------
        >>> inst.connect()
        """

        if self.connected:
            return

        self.inst = self.rm.open_resource(
            self.resource_name
        )

        # -------------------------
        # VISA CONFIGURATION
        # -------------------------

        self.inst.timeout = self._timeout

        self.inst.read_termination = (
            self.read_termination
        )

        self.inst.write_termination = (
            self.write_termination
        )

        self.inst.chunk_size = 102400

        # Limpieza inicial
        try:
            self.inst.clear()
        except Exception:
            pass

    def disconnect(self):
        """
        Cierra conexión VISA.

        Examples
        --------
        >>> inst.disconnect()
        """

        if not self.connected:
            return

        try:
            self.inst.close()

        finally:
            self.inst = None

    # =========================================================
    # PROPERTIES
    # =========================================================

    @property
    def timeout(self) -> int:
        """
        Timeout VISA actual.

        Returns
        -------
        int
            Timeout en milisegundos.
        """

        return self._timeout

    @timeout.setter
    def timeout(self, value: int):
        """
        Configura timeout VISA.

        Parameters
        ----------
        value : int
            Timeout en milisegundos.
        """

        self._timeout = value

        if self.connected:
            self.inst.timeout = value

    # =========================================================
    # RECONNECT
    # =========================================================

    def reconnect(
            self,
            resource_name: str,
            timeout: int = 10000,
            read_termination: str = "\n",
            write_termination: str = "\n"
    ):
        """
        Reconecta instrumento VISA.

        Parameters
        ----------
        resource_name : str
            Dirección VISA.

        timeout : int, optional
            Timeout VISA.

        read_termination : str, optional
            Terminador lectura.

        write_termination : str, optional
            Terminador escritura.
        """

        self.disconnect()

        self.resource_name = resource_name

        self._timeout = timeout

        self.read_termination = read_termination
        self.write_termination = write_termination

        self.connect()

    # =========================================================
    # LOW LEVEL
    # =========================================================

    def write(
            self,
            cmd: str,
            debug: bool = False
    ):
        """
        Envía comando SCPI.

        Parameters
        ----------
        cmd : str
            Comando SCPI.

        debug : bool, optional
            Imprime comando enviado.
        """

        if not self.connected:
            raise RuntimeError(
                "Instrument not connected"
            )

        if debug:
            print(f"[WRITE] {cmd}")

        self.inst.write(cmd)

    def query(
            self,
            cmd: str,
            debug: bool = False,
            debug_response: bool = False
    ) -> str:
        """
        Ejecuta query SCPI.

        Parameters
        ----------
        cmd : str
            Query SCPI.

        debug : bool, optional
            Imprime comando.

        debug_response : bool, optional
            Imprime respuesta.

        Returns
        -------
        str
            Respuesta SCPI.
        """

        if not self.connected:
            raise RuntimeError(
                "Instrument not connected"
            )

        if debug:
            print(f"[QUERY] {cmd}")

        response = self.inst.query(cmd).strip()

        if debug_response:
            print(
                f"[QUERY_RESPONSE] {response}"
            )

        return response

    # =========================================================
    # SCPI HELPERS
    # =========================================================

    def write_scpi(
            self,
            subsystem: str,
            function: str,
            value=None,
            channels=None,
            quoted: bool = False,
            debug: bool = False,
            check_esr: bool = True
    ):
        """
        Construye y envía comando SCPI.
        """

        cmd = get_function_scpi_command(
            subsystem=subsystem,
            function=function,
            value=value,
            channels=channels,
            quoted=quoted
        )

        self.write(cmd, debug=debug)

        if check_esr:

            esr = self.read_esr()

            if (
                    esr["command_error"]
                    or
                    esr["execution_error"]
            ):
                raise RuntimeError(
                    f"SCPI error detected: "
                    f"{esr} in command {cmd}"
                )

        return cmd

    def query_scpi(
            self,
            subsystem: str,
            function: str,
            channels=None,
            debug: bool = False
    ) -> str:
        """
        Construye y ejecuta query SCPI.
        """

        if not function.endswith("?"):
            function += "?"

        cmd = get_function_scpi_command(
            subsystem=subsystem,
            function=function,
            channels=channels
        )

        return self.query(cmd, debug=debug)

    # =========================================================
    # STANDARD SCPI
    # =========================================================

    def idn(self) -> str:
        """
        Lee identificación SCPI.

        Returns
        -------
        str
            Respuesta de *IDN?
        """

        return self.query("*IDN?")

    def reset(self):
        """
        Ejecuta reset SCPI (*RST).
        """

        self.write("*RST")

    def trigger(self):
        """
        Ejecuta trigger SCPI (*TRG).
        """

        self.write("*TRG")

    def clear(self):
        """
        Limpia registros SCPI (*CLS).
        """

        self.write("*CLS")

    def clear_status_and_errors(self):
        """
        Limpia estado y cola de errores.
        """

        self.write("*CLS")

        while True:

            err = self.query_scpi(
                "SYST",
                "ERR"
            )

            if err.startswith("0"):
                break

    def get_error(self):
        """
        Lee siguiente error SCPI.

        Returns
        -------
        tuple[int, str]
            Código y mensaje.
        """

        err = self.query_scpi(
            "SYST",
            "ERR"
        )

        code, msg = err.split(",", 1)

        return int(code), msg.strip('"')

    def wait_opc(self):
        """
        Espera fin de operación (*OPC?).
        """

        self.query("*OPC?")

    def read_esr(self) -> dict:
        """
        Lee ESR SCPI.

        Returns
        -------
        dict
            ESR interpretado.
        """

        response = self.query("*ESR?")

        try:
            esr = int(response)

        except ValueError:
            raise RuntimeError(
                f"Invalid ESR response: "
                f"{response}"
            )

        return {
            "raw": esr,
            "operation_complete":
                bool(esr & 0b00000001),

            "request_control":
                bool(esr & 0b00000010),

            "query_error":
                bool(esr & 0b00000100),

            "device_dependent_error":
                bool(esr & 0b00001000),

            "execution_error":
                bool(esr & 0b00010000),

            "command_error":
                bool(esr & 0b00100000),

            "user_request":
                bool(esr & 0b01000000),

            "power_on":
                bool(esr & 0b10000000),
        }


def get_function_scpi_command(
        subsystem: str,
        function: str,
        value=None,
        channels=None,
        quoted: bool = False
):
    """
    Construye un comando SCPI genérico.

    Examples
    --------
    SENS:FUNC 'TEMP'

    SENS:TEMP:NPLC 1

    SENS:TEMP:AVER:STAT ON

    SENS:TEMP:NPLC 1, (@101,102)

    Parameters
    ----------
    subsystem : str
        Subsistema SCPI.

    function : str
        Función SCPI.

    value :
        Valor opcional.

    channels :
        Canal o lista de canales.

    quoted : bool
        Si True añade comillas al valor.

    Returns
    -------
    str
        Comando SCPI generado.
    """

    if not subsystem:
        raise ValueError("Debes declarar el subsistema")

    if not function:
        raise ValueError("Debes declarar la función")

    subsystem = subsystem.upper()
    function = function.upper()

    command = f"{subsystem}:{function}"

    # -------------------------
    # VALUE
    # -------------------------

    if value is not None:

        if isinstance(value, bool):
            value = "ON" if value else "OFF"
        else:
            value = str(value)

        if quoted:
            value = f"'{value}'"

        command += f" {value}"

    # -------------------------
    # CHANNEL LIST
    # -------------------------

    if channels is not None:

        if isinstance(channels, int):
            channels = [channels]

        if not isinstance(channels, (list, tuple)):
            raise ValueError(
                "channels debe ser int, lista o tupla"
            )

        ch_str = ""

        if not channels:
            pass

        elif not all(isinstance(ch, int) for ch in channels):
            raise ValueError(
                "channels debe contener enteros"
            )

        else:
            ch_str = ",".join(str(ch) for ch in channels)

        command += f" (@{ch_str})"

    return command