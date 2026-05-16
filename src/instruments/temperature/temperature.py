from src.instruments.interfaces.interfaces import (
    ProfileInterface,
    ProfileRunnerInterface,
    OvenInterface
)

class TemperatureSweep(
    ProfileRunnerInterface
):
    """
    Ejecutador de perfiles térmicos.

    Esta clase coordina:
    - un horno,
    - un perfil,
    - la ejecución secuencial de steps.

    Notes
    -----
    El comportamiento de reset y estados seguros
    se delega completamente al profile mediante
    reset_step.
    """

    # =========================================================
    # INIT
    # =========================================================

    def __init__(
            self,
            oven: OvenInterface,
            profile: ProfileInterface
    ):
        """
        Inicializa temperature sweep.

        Parameters
        ----------
        oven : OvenInterface
            Horno controlado.

        profile : ProfileInterface
            Perfil ejecutado.
        """

        self._oven = oven

        self._profile = profile

        self._running = False

        self._paused = False

        self._finished = False

    # =========================================================
    # PROFILE
    # =========================================================

    @property
    def profile(self) -> ProfileInterface:
        """
        Perfil asociado.

        Returns
        -------
        ProfileInterface
            Perfil activo.
        """

        return self._profile

    # =========================================================
    # OVEN
    # =========================================================

    @property
    def oven(self) -> OvenInterface:
        """
        Horno asociado.

        Returns
        -------
        OvenInterface
            Horno controlado.
        """

        return self._oven

    # =========================================================
    # STATUS
    # =========================================================

    @property
    def running(self) -> bool:
        """
        Estado de ejecución.
        """

        return self._running

    @property
    def paused(self) -> bool:
        """
        Estado de pausa.
        """

        return self._paused

    @property
    def finished(self) -> bool:
        """
        Estado de finalización.
        """

        return self._finished

    # =========================================================
    # EXECUTION CONTROL
    # =========================================================

    def start(self):
        """
        Inicia ejecución del perfil.
        """

        self.reset()

        self._running = True

        self._paused = False

        self._finished = False

        self.execute_next_step()

    def stop(self):
        """
        Detiene ejecución.
        """

        self._running = False

    def pause(self):
        """
        Pausa ejecución.
        """

        self._paused = True

    def resume(self):
        """
        Reanuda ejecución.
        """

        self._paused = False

    def reset(self):
        """
        Reinicia ejecución del perfil.
        """

        self.profile.reset()

        # Ejecutar el primer step
        self.profile.first_step.execute(
            self.oven
        )

        self._finished = False

    # =========================================================
    # STEP EXECUTION
    # =========================================================

    def execute_next_step(self):
        """
        Ejecuta siguiente step del perfil.
        """

        if not self.profile.has_next_step:

            self._finished = True

            self._running = False

            return

        step = self.profile.get_next_step()

        step.execute(self.oven)

    # =========================================================
    # HELPERS
    # =========================================================

    @property
    def current_step(self):
        """
        Step actual.

        Returns
        -------
        StepInterface
            Step actual.
        """

        return self.profile.get_current_step()

    @property
    def current_setpoint(self):
        """
        Setpoint actual.

        Returns
        -------
        Any
            Setpoint actual.
        """

        return self.current_step.setpoint


