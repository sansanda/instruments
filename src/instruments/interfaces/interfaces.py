from abc import ABC, abstractmethod

class InstrumentInterface(ABC):
    """
    Interfaz base universal para instrumentos.

    Define el contrato mínimo común para cualquier
    instrumento controlable por software.
    """

    # =========================================================
    # IDENTIFICATION
    # =========================================================

    @property
    @abstractmethod
    def connected(self) -> bool:
        """
        Estado de conexión.

        Returns
        -------
        bool
            True si el instrumento está conectado.
        """
        pass

    # =========================================================
    # CONNECTION
    # =========================================================

    @abstractmethod
    def connect(self):
        """
        Establece conexión con el instrumento.
        """
        pass

    @abstractmethod
    def disconnect(self):
        """
        Cierra conexión con el instrumento.
        """
        pass

    # =========================================================
    # STATUS
    # =========================================================

    @abstractmethod
    def reset(self):
        """
        Resetea el instrumento.
        """
        pass

    @abstractmethod
    def idn(self) -> str:
        """
        Devuelve identificación del instrumento.

        Returns
        -------
        str
            Identificación.
        """
        pass

class SCPIInstrumentInterface(
    InstrumentInterface,
    ABC
):
    """
    Interfaz abstracta para instrumentos compatibles con SCPI.

    Esta interfaz define el contrato común para cualquier
    instrumento controlado mediante comandos SCPI.

    Extiende InstrumentInterface añadiendo:
    - comunicación SCPI,
    - helpers SCPI,
    - comandos estándar IEEE-488.2,
    - manejo de errores.

    Diseñada para:
    - drivers VISA reales,
    - simuladores,
    - fakes de testing,
    - proxies remotos.

    Notes
    -----
    Esta interfaz NO define detalles específicos de VISA.
    VISA debe pertenecer a la implementación concreta,
    no al contrato abstracto.

    Examples
    --------
    >>> class MyInstrument(
    ...     SCPIInstrumentInterface
    ... ):
    ...     pass
    """

    # =========================================================
    # LOW LEVEL COMMUNICATION
    # =========================================================

    @abstractmethod
    def write(
            self,
            cmd: str,
            debug: bool = False
    ):
        """
        Envía un comando SCPI.

        Parameters
        ----------
        cmd : str
            Comando SCPI.

        debug : bool, optional
            Habilita impresión debug.
        """
        pass

    @abstractmethod
    def query(
            self,
            cmd: str,
            debug: bool = False,
            debug_response: bool = False
    ) -> str:
        """
        Ejecuta una query SCPI.

        Parameters
        ----------
        cmd : str
            Query SCPI.

        debug : bool, optional
            Habilita impresión debug.

        debug_response : bool, optional
            Imprime respuesta.

        Returns
        -------
        str
            Respuesta del instrumento.
        """
        pass

    # =========================================================
    # SCPI HELPERS
    # =========================================================

    @abstractmethod
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
        Construye y envía un comando SCPI.

        Parameters
        ----------
        subsystem : str
            Subsistema SCPI.

        function : str
            Función SCPI.

        value :
            Valor opcional.

        channels :
            Lista de canales opcional.

        quoted : bool
            Si True añade comillas al valor.

        debug : bool
            Habilita impresión debug.

        check_esr : bool
            Verifica ESR tras ejecutar comando.
        """
        pass

    @abstractmethod
    def query_scpi(
            self,
            subsystem: str,
            function: str,
            channels=None,
            debug: bool = False
    ) -> str:
        """
        Construye y ejecuta una query SCPI.

        Parameters
        ----------
        subsystem : str
            Subsistema SCPI.

        function : str
            Función SCPI.

        channels :
            Lista opcional de canales.

        debug : bool
            Habilita impresión debug.

        Returns
        -------
        str
            Respuesta SCPI.
        """
        pass

    # =========================================================
    # STANDARD SCPI
    # =========================================================

    @abstractmethod
    def clear(self):
        """
        Limpia registros y errores SCPI (*CLS).
        """
        pass

    @abstractmethod
    def trigger(self):
        """
        Ejecuta trigger SCPI (*TRG).
        """
        pass

    @abstractmethod
    def wait_opc(self):
        """
        Espera fin de operación (*OPC?).
        """
        pass

    @abstractmethod
    def read_esr(self) -> dict:
        """
        Lee ESR SCPI.

        Returns
        -------
        dict
            ESR interpretado.
        """
        pass

    @abstractmethod
    def get_error(self):
        """
        Lee siguiente error SCPI.

        Returns
        -------
        tuple[int, str]
            Código y mensaje.
        """
        pass

    @abstractmethod
    def clear_status_and_errors(self):
        """
        Limpia estado y cola de errores.
        """
        pass

class SourceInstrumentInterface(
    SCPIInstrumentInterface,
    ABC
):
    """
    Interfaz abstracta para instrumentos fuente SCPI.

    Esta interfaz define el contrato común para instrumentos
    capaces de generar una salida programable, como:

    - Fuentes de alimentación
    - Fuentes de corriente
    - SMUs
    - Electronic loads
    - Generadores programables

    Objetivos
    ---------
    - Estandarizar API
    - Desacoplar drivers concretos
    - Facilitar testing
    - Permitir polimorfismo

    Notes
    -----
    Las clases derivadas deben implementar toda la lógica
    específica del instrumento.

    Examples
    --------
    >>> class MyPowerSupply(
    ...     SourceInstrumentInterface
    ... ):
    ...     pass
    """

    # =========================================================
    # OUTPUT CONTROL
    # =========================================================

    @abstractmethod
    def output_on(self):
        """
        Activa la salida del instrumento.

        Examples
        --------
        >>> instrument.output_on()
        """
        pass

    @abstractmethod
    def output_off(self):
        """
        Desactiva la salida del instrumento.

        Examples
        --------
        >>> instrument.output_off()
        """
        pass

    # =========================================================
    # OUTPUT ENABLED
    # =========================================================

    @property
    @abstractmethod
    def output_enabled(self) -> bool:
        """
        Estado actual de la salida.

        Returns
        -------
        bool
            True si la salida está activada.

        Examples
        --------
        >>> print(instrument.output_enabled)
        True
        """
        pass

    @output_enabled.setter
    @abstractmethod
    def output_enabled(self, value: bool):
        """
        Activa o desactiva la salida.

        Parameters
        ----------
        value : bool
            Estado deseado.

        Examples
        --------
        >>> instrument.output_enabled = True
        """
        pass

class ElectronicLoadInterface(

    SourceInstrumentInterface,
    ABC
):
    """
    Interfaz abstracta para cargas electrónicas programables.

    Esta interfaz define el contrato común para cualquier
    electronic load soportada por el framework.

    Objetivos
    ---------
    - Desacoplar drivers concretos
    - Facilitar testing y simulación
    - Permitir múltiples fabricantes
    - Estandarizar API

    Notes
    -----
    Esta interfaz define únicamente capacidades propias
    de una electronic load.

    Funcionalidades comunes como:
    - conexión,
    - SCPI,
    - trigger,
    - reset,
    - output enable,
    ya se heredan desde interfaces superiores.

    Examples
    --------
    >>> class MyElectronicLoad(
    ...     ElectronicLoadInterface
    ... ):
    ...     pass
    """

    # =========================================================
    # MODE
    # =========================================================

    @property
    @abstractmethod
    def mode(self) -> str:
        """
        Modo de funcionamiento actual.

        Returns
        -------
        str
            Modo activo.
        """
        pass

    @mode.setter
    @abstractmethod
    def mode(self, value: str):
        """
        Configura modo de funcionamiento.

        Parameters
        ----------
        value : str
            Modo deseado.
        """
        pass

    # =========================================================
    # CURRENT
    # =========================================================

    @property
    @abstractmethod
    def current(self) -> float:
        """
        Corriente programada.

        Returns
        -------
        float
            Corriente en amperios.
        """
        pass

    @current.setter
    @abstractmethod
    def current(self, value: float):
        """
        Configura corriente.

        Parameters
        ----------
        value : float
            Corriente en amperios.
        """
        pass

    # =========================================================
    # VOLTAGE
    # =========================================================

    @property
    @abstractmethod
    def voltage(self) -> float:
        """
        Voltaje programado.

        Returns
        -------
        float
            Voltaje en voltios.
        """
        pass

    @voltage.setter
    @abstractmethod
    def voltage(self, value: float):
        """
        Configura voltaje.

        Parameters
        ----------
        value : float
            Voltaje en voltios.
        """
        pass

    # =========================================================
    # POWER
    # =========================================================

    @property
    @abstractmethod
    def power(self) -> float:
        """
        Potencia programada.

        Returns
        -------
        float
            Potencia en vatios.
        """
        pass

    @power.setter
    @abstractmethod
    def power(self, value: float):
        """
        Configura potencia.

        Parameters
        ----------
        value : float
            Potencia en vatios.
        """
        pass

    # =========================================================
    # RESISTANCE
    # =========================================================

    @property
    @abstractmethod
    def resistance(self) -> float:
        """
        Resistencia programada.

        Returns
        -------
        float
            Resistencia en ohmios.
        """
        pass

    @resistance.setter
    @abstractmethod
    def resistance(self, value: float):
        """
        Configura resistencia.

        Parameters
        ----------
        value : float
            Resistencia en ohmios.
        """
        pass

    # =========================================================
    # CURRENT RANGE
    # =========================================================

    @property
    @abstractmethod
    def current_range(self) -> float:
        """
        Rango de corriente activo.

        Returns
        -------
        float
            Rango configurado.
        """
        pass

    @current_range.setter
    @abstractmethod
    def current_range(self, value: int):
        """
        Configura rango de corriente.

        Parameters
        ----------
        value : int
            Rango deseado.
        """
        pass

    # =========================================================
    # CURRENT SLEW RATE
    # =========================================================

    @property
    @abstractmethod
    def current_slew_rate(self) -> float:
        """
        Slew rate de corriente.

        Returns
        -------
        float
            Slew rate en A/us.
        """
        pass

    @current_slew_rate.setter
    @abstractmethod
    def current_slew_rate(self, value: float):
        """
        Configura slew rate.

        Parameters
        ----------
        value : float
            Slew rate deseado.
        """
        pass

    # =========================================================
    # TRIGGER SOURCE
    # =========================================================

    @property
    @abstractmethod
    def trigger_source(self) -> str:
        """
        Fuente de trigger actual.

        Returns
        -------
        str
            Fuente de trigger.
        """
        pass

    @trigger_source.setter
    @abstractmethod
    def trigger_source(self, value: str):
        """
        Configura fuente de trigger.

        Parameters
        ----------
        value : str
            Fuente de trigger.
        """
        pass

    # =========================================================
    # MEASUREMENTS
    # =========================================================

    @property
    @abstractmethod
    def measured_voltage(self) -> float:
        """
        Voltaje medido.

        Returns
        -------
        float
            Voltaje medido.
        """
        pass

    @property
    @abstractmethod
    def measured_current(self) -> float:
        """
        Corriente medida.

        Returns
        -------
        float
            Corriente medida.
        """
        pass

    @property
    @abstractmethod
    def measured_power(self) -> float:
        """
        Potencia medida.

        Returns
        -------
        float
            Potencia medida.
        """
        pass

    # =========================================================
    # QUICK CONFIGURATION
    # =========================================================

    @abstractmethod
    def configure_cc(
            self,
            current: float,
            current_range: int = 60
    ):
        """
        Configuración rápida modo corriente constante.

        Parameters
        ----------
        current : float
            Corriente deseada.

        current_range : int, optional
            Rango de corriente.
        """
        pass

    @abstractmethod
    def configure_cv(self, voltage: float):
        """
        Configuración rápida modo voltaje constante.

        Parameters
        ----------
        voltage : float
            Voltaje deseado.
        """
        pass

    @abstractmethod
    def configure_cr(self, resistance: float):
        """
        Configuración rápida modo resistencia constante.

        Parameters
        ----------
        resistance : float
            Resistencia deseada.
        """
        pass

    @abstractmethod
    def configure_cp(self, power: float):
        """
        Configuración rápida modo potencia constante.

        Parameters
        ----------
        power : float
            Potencia deseada.
        """
        pass

    # =========================================================
    # UTILITIES
    # =========================================================

    @abstractmethod
    def set_default_configuration(
            self,
            current_range: int = 60,
            slew_rate: float = 1.0,
            current: float = 0.0
    ):
        """
        Configuración inicial recomendada.

        Parameters
        ----------
        current_range : int, optional
            Rango inicial.

        slew_rate : float, optional
            Slew rate inicial.

        current : float, optional
            Corriente inicial.
        """
        pass

class TemperatureMeasureInterface(
    ABC
):
    """
    Interfaz abstracta para instrumentos capaces
    de medir temperatura.

    Esta interfaz representa una capacidad reusable
    que puede implementarse en múltiples tipos de
    instrumentos:

    - Hornos
    - Multímetros
    - DAQs
    - Cámaras climáticas
    - Sensores
    - Adquisidores
    - Sistemas PID

    Objetivos
    ---------
    - Estandarizar lectura de temperatura
    - Facilitar polimorfismo
    - Reutilizar capacidades
    - Desacoplar tipos concretos

    Notes
    -----
    Esta interfaz NO define:
    - control térmico,
    - setpoints,
    - rampas,
    - regulación PID.

    Solo define capacidad de medida.

    Examples
    --------
    >>> class MyThermometer(
    ...     TemperatureMeasureInterface
    ... ):
    ...     pass
    """

    # =========================================================
    # TEMPERATURE
    # =========================================================

    @property
    @abstractmethod
    def temperature(self) -> float:
        """
        Temperatura actual medida.

        Returns
        -------
        float
            Temperatura actual.
        """
        pass

class OvenInterface(
    InstrumentInterface,
    TemperatureMeasureInterface,
    ABC
):
    """
    Interfaz abstracta para hornos programables.

    Esta interfaz define capacidades de:
    - control térmico,
    - regulación de temperatura,
    - setpoint programable.

    La capacidad de medida de temperatura se hereda
    desde TemperatureMeasureInterface.
    """

    # =========================================================
    # TEMPERATURE SETPOINT
    # =========================================================

    @property
    @abstractmethod
    def temperature_setpoint(self) -> float:
        """
        Setpoint actual de temperatura.

        Returns
        -------
        float
            Temperatura objetivo.
        """
        pass

    @temperature_setpoint.setter
    @abstractmethod
    def temperature_setpoint(
            self,
            temperature: float
    ):
        """
        Configura setpoint de temperatura.

        Parameters
        ----------
        temperature : float
            Temperatura objetivo.
        """
        pass

class VoltageSourceInterface(
    SourceInstrumentInterface,
    ABC
):
    """
    Interfaz abstracta para instrumentos capaces
    de generar tensión programable.

    Esta interfaz representa la capacidad de source
    de voltaje, independientemente del tipo concreto
    de instrumento.

    Puede implementarse en:
    - Fuentes de alimentación
    - SMUs
    - Calibradores
    - Simuladores
    - Generadores DC
    - Fuentes programables

    Objetivos
    ---------
    - Estandarizar generación de tensión
    - Facilitar polimorfismo
    - Reutilizar capacidades
    - Desacoplar drivers concretos

    Notes
    -----
    Esta interfaz define únicamente capacidad
    de generación de tensión.

    NO define:
    - medida,
    - corriente,
    - protección,
    - rampas,
    - modos avanzados.

    Examples
    --------
    >>> class MyPowerSupply(
    ...     VoltageSourceInterface
    ... ):
    ...     pass
    """

    # =========================================================
    # VOLTAGE
    # =========================================================

    @property
    @abstractmethod
    def voltage(self) -> float:
        """
        Voltaje programado.

        Returns
        -------
        float
            Voltaje en voltios.
        """
        pass

    @voltage.setter
    @abstractmethod
    def voltage(
            self,
            value: float
    ):
        """
        Configura voltaje de salida.

        Parameters
        ----------
        value : float
            Voltaje deseado en voltios.
        """
        pass

    # =========================================================
    # VOLTAGE RANGE
    # =========================================================

    @property
    @abstractmethod
    def voltage_range(self) -> float:
        """
        Rango de voltaje activo.

        Returns
        -------
        float
            Rango de voltaje configurado.
        """
        pass

    @voltage_range.setter
    @abstractmethod
    def voltage_range(
            self,
            value: float
    ):
        """
        Configura rango de voltaje.

        Parameters
        ----------
        value : float
            Rango de voltaje deseado.
        """
        pass

class CurrentSourceInterface(
    SourceInstrumentInterface,
    ABC
):
    """
    Interfaz abstracta para instrumentos capaces
    de generar corriente programable.

    Esta interfaz representa la capacidad de source
    de corriente, independientemente del tipo concreto
    de instrumento.

    Puede implementarse en:
    - Fuentes de corriente
    - SMUs
    - Calibradores
    - Simuladores
    - Fuentes programables
    - Drivers LED

    Objetivos
    ---------
    - Estandarizar generación de corriente
    - Facilitar polimorfismo
    - Reutilizar capacidades
    - Desacoplar drivers concretos

    Notes
    -----
    Esta interfaz define únicamente capacidad
    de generación de corriente.

    NO define:
    - medida,
    - voltaje,
    - compliance,
    - protección,
    - rampas,
    - modos avanzados.

    Examples
    --------
    >>> class MyCurrentSource(
    ...     CurrentSourceInterface
    ... ):
    ...     pass
    """

    # =========================================================
    # CURRENT
    # =========================================================

    @property
    @abstractmethod
    def current(self) -> float:
        """
        Corriente programada.

        Returns
        -------
        float
            Corriente en amperios.
        """
        pass

    @current.setter
    @abstractmethod
    def current(
            self,
            value: float
    ):
        """
        Configura corriente de salida.

        Parameters
        ----------
        value : float
            Corriente deseada en amperios.
        """
        pass

    # =========================================================
    # CURRENT RANGE
    # =========================================================

    @property
    @abstractmethod
    def current_range(self) -> float:
        """
        Rango de corriente activo.

        Returns
        -------
        float
            Rango de corriente configurado.
        """
        pass

    @current_range.setter
    @abstractmethod
    def current_range(
            self,
            value: float
    ):
        """
        Configura rango de corriente.

        Parameters
        ----------
        value : float
            Rango de corriente deseado.
        """
        pass



######### PROFILES ###############

class StepInterface(
    ABC
):
    """
    Interfaz abstracta para pasos ejecutables.

    Un step representa:
    - una consigna,
    - una duración,
    - una acción ejecutable.

    Diseñado para:
    - perfiles térmicos,
    - rampas de tensión,
    - secuencias de corriente,
    - stress tests,
    - automatización genérica.

    Notes
    -----
    Esta interfaz combina:
    - datos,
    - metadata,
    - comportamiento ejecutable.
    """

    # =========================================================
    # SETPOINT
    # =========================================================

    @property
    @abstractmethod
    def setpoint(self):
        """
        Setpoint del paso.

        Returns
        -------
        Any
            Valor objetivo.
        """
        pass

    @setpoint.setter
    @abstractmethod
    def setpoint(self, value):
        """
        Configura setpoint del paso.

        Parameters
        ----------
        value :
            Nuevo valor objetivo.
        """
        pass

    # =========================================================
    # DURATION
    # =========================================================

    @property
    @abstractmethod
    def duration_s(self) -> float:
        """
        Duración del paso.

        Returns
        -------
        float
            Tiempo en segundos.
        """
        pass

    @duration_s.setter
    @abstractmethod
    def duration_s(
            self,
            value: float
    ):
        """
        Configura duración del paso.

        Parameters
        ----------
        value : float
            Duración en segundos.
        """
        pass

    # =========================================================
    # NAME
    # =========================================================

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Nombre descriptivo del paso.

        Returns
        -------
        str
            Nombre del paso.
        """
        pass

    @name.setter
    @abstractmethod
    def name(
            self,
            value: str
    ):
        """
        Configura nombre descriptivo.

        Parameters
        ----------
        value : str
            Nombre del paso.
        """
        pass

    # =========================================================
    # EXECUTION
    # =========================================================

    @abstractmethod
    def execute(self, target):
        """
        Ejecuta el paso sobre un target.

        Parameters
        ----------
        target :
            Objeto objetivo sobre el que
            se ejecuta el step.
        """
        pass

class ProfileInterface(
    ABC
):
    """
    Interfaz abstracta para perfiles secuenciales.
    """

    # =========================================================
    # PROFILE INFO
    # =========================================================

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @name.setter
    @abstractmethod
    def name(self, value: str):
        pass

    @property
    @abstractmethod
    def total_steps(self) -> int:
        pass

    @property
    @abstractmethod
    def current_step_index(self) -> int:
        pass

    # =========================================================
    # RESET STEP
    # =========================================================

    @property
    @abstractmethod
    def first_step(self) -> StepInterface:
        """
        Devuelve el primer step del profile.

        Returns
        -------
        StepInterface
            Primer step del profile.
        """
        pass

    # =========================================================
    # NAVIGATION
    # =========================================================

    @property
    @abstractmethod
    def has_next_step(self) -> bool:
        pass

    @abstractmethod
    def get_current_step(
            self
    ) -> StepInterface:
        pass

    @abstractmethod
    def get_next_step(
            self
    ) -> StepInterface:
        pass

    @abstractmethod
    def reset(self):
        pass

class ProfileRunnerInterface(
    ABC
):
    """
    Interfaz abstracta para ejecutores
    de perfiles secuenciales.

    Un runner coordina:
    - ejecución,
    - timing,
    - avance de pasos,
    - pausas,
    - estado interno.

    Notes
    -----
    Esta interfaz es genérica y reutilizable
    para múltiples dominios:
    - temperatura,
    - tensión,
    - corriente,
    - potencia,
    - automatización.
    """

    # =========================================================
    # PROFILE
    # =========================================================

    @property
    @abstractmethod
    def profile(
            self
    ) -> ProfileInterface:
        """
        Perfil asociado.

        Returns
        -------
        ProfileInterface
            Perfil ejecutado.
        """
        pass

    # =========================================================
    # STATUS
    # =========================================================

    @property
    @abstractmethod
    def running(self) -> bool:
        """
        Estado de ejecución.

        Returns
        -------
        bool
            True si está ejecutándose.
        """
        pass

    @property
    @abstractmethod
    def paused(self) -> bool:
        """
        Estado de pausa.

        Returns
        -------
        bool
            True si está pausado.
        """
        pass

    @property
    @abstractmethod
    def finished(self) -> bool:
        """
        Estado de finalización.

        Returns
        -------
        bool
            True si el perfil terminó.
        """
        pass

    # =========================================================
    # EXECUTION CONTROL
    # =========================================================

    @abstractmethod
    def start(self):
        """
        Inicia ejecución.
        """
        pass

    @abstractmethod
    def stop(self):
        """
        Detiene ejecución.
        """
        pass

    @abstractmethod
    def pause(self):
        """
        Pausa ejecución.
        """
        pass

    @abstractmethod
    def resume(self):
        """
        Reanuda ejecución.
        """
        pass

    @abstractmethod
    def reset(self):
        """
        Reinicia ejecución.
        """
        pass

    # =========================================================
    # STEP EXECUTION
    # =========================================================

    @abstractmethod
    def execute_next_step(self):
        """
        Ejecuta siguiente paso.
        """
        pass

