import re

from instruments.drivers.instruments.SCPIInstrument import (
    SCPIInstrument,
    SUPPORTED_FUNCTIONS,
    SUPPORTED_TCON,
    SUPPORTED_TEMPERATURE_TRANSDUCERS,
    SUPPORTED_TCOUPLES,
    SUPPORTED_FRTDS
)

from src.instruments.models.configuration_models import SourceMeterConfig


# =========================
# STATIC FUNCTIONS
# =========================

def parse_reading(raw):

    raw = re.sub(r'[^\x20-\x7E]', '', raw)

    parts = raw.strip().split(",")

    parsed = {}

    for part in parts:

        if "SECS" in part:

            parsed["time"] = float(
                part.replace("SECS", "")
            )

        elif "RDNG" in part:

            parsed["reading_number"] = int(
                part.replace("RDNG#", "")
            )

        elif "C" in part:

            parsed["value"] = float(
                part.replace("C", "")
            )

        else:

            try:
                parsed["value"] = float(part)

            except:
                pass

    return parsed


class Keithley24xx(SCPIInstrument):

    DEFAULT_READ_TERMINATION = "\n"
    DEFAULT_WRITE_TERMINATION = "\n"

    def __init__(
            self,
            gpib_card=0,
            gpib_address=16,
            timeout=10000,
            read_termination=None,
            write_termination=None
    ):

        resource_name = (
            f"GPIB{gpib_card}::"
            f"{gpib_address}::INSTR"
        )

        super().__init__(
            resource_name=resource_name,
            timeout=timeout,

            read_termination=(
                read_termination
                if read_termination is not None
                else self.DEFAULT_READ_TERMINATION
            ),

            write_termination=(
                write_termination
                if write_termination is not None
                else self.DEFAULT_WRITE_TERMINATION
            )
        )

        self._source_mode = None

    # =========================
    # CONFIG
    # =========================

    def enable_incognito_mode(
            self,
            enable_beeper=False,
            enable_display=False
    ):

        self.enable_beeper(enable=enable_beeper)

        self.enable_display(enable=enable_display)

    def init_config(self):

        self.reset()

        self.wait_opc()

        self.clear()

        self.wait_opc()

        self.enable_incognito_mode(
            enable_beeper=False,
            enable_display=True
        )

        self.configure_output_format()

        self.enable_auto_zero()

    def configure(self, cfg: SourceMeterConfig):

        # =========================
        # GPIB
        # =========================

        gpib_cfg = cfg.gpib

        current_resource = self.inst.resource_name

        new_resource = (
            f"GPIB{gpib_cfg.gpib_card}::"
            f"{gpib_cfg.address}::INSTR"
        )

        # =========================
        # RECONNECT
        # =========================

        if current_resource != new_resource:

            self.reconnect(
                resource_name=new_resource,
                timeout_ms=gpib_cfg.timeout_ms,

                read_termination=getattr(
                    gpib_cfg,
                    "read_termination",
                    self.read_termination
                ),

                write_termination=getattr(
                    gpib_cfg,
                    "write_termination",
                    self.write_termination
                )
            )

        else:

            self.inst.timeout = gpib_cfg.timeout_ms

            self.inst.read_termination = getattr(
                gpib_cfg,
                "read_termination",
                self.read_termination
            )

            self.inst.write_termination = getattr(
                gpib_cfg,
                "write_termination",
                self.write_termination
            )

            self.read_termination = (
                self.inst.read_termination
            )

            self.write_termination = (
                self.inst.write_termination
            )

    # =========================
    # DISPLAY
    # =========================

    def enable_display(self, enable=True):

        return self.write_scpi(
            subsystem="DISP",
            function="ENAB",
            value=enable
        )

    def set_display_resolution(self, n_digits=6):

        return self.write_scpi(
            subsystem="DISP",
            function="DIG",
            value=n_digits
        )

    def get_display_resolution(self):

        return self.query_scpi(
            subsystem="SENS",
            function="DIG"
        )

    # =========================
    # FORMAT
    # =========================

    def configure_output_format(
            self,
            voltage=True,
            current=False,
            resistance=False,
            time=False,
            status=False
    ):

        elements = []

        if voltage:
            elements.append("VOLT")

        if current:
            elements.append("CURR")

        if resistance:
            elements.append("RES")

        if time:
            elements.append("TIME")

        if status:
            elements.append("STAT")

        if not elements:
            raise ValueError(
                "At least one output element must be selected"
            )

        value = ",".join(elements)

        return self.write_scpi(
            subsystem="FORM",
            function="ELEM",
            value=value
        )

    # =========================
    # OUTPUT
    # =========================

    def set_output(self, on=True):

        return self.write_scpi(
            subsystem="OUTP",
            function="STAT",
            value=on
        )

    def get_output_status(self):

        return self.query_scpi(
            subsystem="OUTP",
            function="STAT"
        )

    # =========================
    # ROUTE
    # =========================

    def set_output_route(self, route="FRONT"):

        return self.write_scpi(
            subsystem="ROUT",
            function="TERM",
            value=route
        )

    # =========================
    # SENSE
    # =========================

    def set_nplc(self, nplc=1.0):

        return self.write_scpi(
            subsystem="SENS",
            function=f"{self.get_sense_function()}:NPLC",
            value=nplc
        )

    def get_nplc(self):

        return self.query_scpi(
            subsystem="SENS",
            function=f"{self.get_sense_function()}:NPLC"
        )

    def set_sense_function(self, function: str):

        function = function.upper()

        if function not in SUPPORTED_FUNCTIONS:
            raise ValueError(
                f"Función no válida: {function}"
            )

        return self.write_scpi(
            subsystem="SENS",
            function="FUNC",
            value=function,
            quoted=True
        )

    def get_sense_function(self):

        response = self.query_scpi(
            subsystem="SENS",
            function="FUNC"
        )

        return response.strip().replace('"', '')

    def get_sense_compliance(self):

        source_mode = self.get_source_mode()

        if source_mode == "VOLT":

            return float(
                self.query_scpi(
                    subsystem="SENS",
                    function="CURR:PROT"
                )
            )

        elif source_mode == "CURR":

            return float(
                self.query_scpi(
                    subsystem="SENS",
                    function="VOLT:PROT"
                )
            )

        else:

            raise ValueError(
                f"Invalid source mode '{source_mode}'"
            )

    def set_sense_compliance(self, value: float):

        if not isinstance(value, (float, int)):
            raise TypeError(
                f"Compliance must be a float"
            )

        source_mode = self.get_source_mode()

        if source_mode == "VOLT":

            return self.write_scpi(
                subsystem="SENS",
                function="CURR:PROT",
                value=float(value)
            )

        elif source_mode == "CURR":

            return self.write_scpi(
                subsystem="SENS",
                function="VOLT:PROT",
                value=float(value)
            )

        else:

            raise ValueError(
                f"Invalid source mode '{source_mode}'"
            )

    def set_sense_range(self, value):

        quantity = (
            self.get_sense_function()
            .split(":")[0]
            .upper()
        )

        if quantity not in ("CURR", "VOLT"):

            raise ValueError(
                f"Range setting not supported "
                f"for '{quantity}'"
            )

        if isinstance(value, str):

            if value.strip().upper() == "AUTO":

                return self.write_scpi(
                    subsystem="SENS",
                    function=f"{quantity}:RANG:AUTO",
                    value="ON"
                )

            else:

                raise TypeError(
                    f"Invalid string value for range"
                )

        if isinstance(value, (float, int)):

            return self.write_scpi(
                subsystem="SENS",
                function=f"{quantity}:RANG",
                value=float(value)
            )

        raise TypeError(
            f"Range must be float or 'AUTO'"
        )

    def get_sense_range(self):

        quantity = (
            self.get_sense_function()
            .split(":")[0]
            .upper()
        )

        if quantity not in ("CURR", "VOLT"):

            raise ValueError(
                f"Range not supported for '{quantity}'"
            )

        auto = self.query_scpi(
            subsystem="SENS",
            function=f"{quantity}:RANG:AUTO"
        ).strip().upper()

        if auto == "ON":
            return "AUTO"

        return float(
            self.query_scpi(
                subsystem="SENS",
                function=f"{quantity}:RANG"
            )
        )

    # =========================
    # SOURCE
    # =========================

    def set_source_mode(self, mode="VOLT"):

        mode = mode.strip().upper()

        if mode not in ("VOLT", "CURR"):

            raise ValueError(
                f"Invalid source mode: {mode}"
            )

        result = self.write_scpi(
            subsystem="SOUR",
            function="FUNC:MODE",
            value=mode
        )

        self._source_mode = mode

        if mode == "VOLT":
            self.set_sense_function("CURR:DC")

        elif mode == "CURR":
            self.set_sense_function("VOLT:DC")

        return result

    def get_source_mode(self, refresh=False):

        if self._source_mode is None or refresh:

            response = self.query_scpi(
                subsystem="SOUR",
                function="FUNC:MODE"
            )

            self._source_mode = (
                response.strip().upper()
            )

        return self._source_mode

    def set_source_level(self, value: float):

        if not isinstance(value, (float, int)):

            raise TypeError(
                f"Source level must be numeric"
            )

        source_mode = self.get_source_mode()

        level = float(value)

        range_value = self.get_source_range()

        if range_value != "AUTO":

            if abs(level) > range_value:

                raise ValueError(
                    f"{source_mode} level "
                    f"({level}) exceeds "
                    f"configured range ({range_value})"
                )

        return self.write_scpi(
            subsystem="SOUR",
            function=f"{source_mode}",
            value=level
        )

    def get_source_level(self):

        source_mode = self.get_source_mode()

        return float(
            self.query_scpi(
                subsystem="SOUR",
                function=f"{source_mode}"
            )
        )

    def set_source_range(self, value):

        source_mode = self.get_source_mode()

        if source_mode not in ("VOLT", "CURR"):

            raise ValueError(
                f"Invalid source mode '{source_mode}'"
            )

        if isinstance(value, str):

            if value.strip().upper() == "AUTO":

                return self.write_scpi(
                    subsystem="SOUR",
                    function=f"{source_mode}:RANG:AUTO",
                    value="ON"
                )

            else:

                raise TypeError(
                    f"Invalid string value for range"
                )

        if isinstance(value, (float, int)):

            return self.write_scpi(
                subsystem="SOUR",
                function=f"{source_mode}:RANG",
                value=float(value)
            )

        raise TypeError(
            f"Range must be float or 'AUTO'"
        )

    def get_source_range(self):

        source_mode = self.get_source_mode()

        auto = self.query_scpi(
            subsystem="SOUR",
            function=f"{source_mode}:RANG:AUTO"
        ).strip().upper()

        if auto == "ON":
            return "AUTO"

        return float(
            self.query_scpi(
                subsystem="SOUR",
                function=f"{source_mode}:RANG"
            )
        )

    # =========================
    # SYSTEM
    # =========================

    def enable_beeper(self, enable=True):

        return self.write_scpi(
            subsystem="SYST",
            function="BEEP:STAT",
            value=enable
        )

    def enable_auto_zero(self, enable=True):

        return self.write_scpi(
            subsystem="SYST",
            function="AZER:STAT",
            value=enable
        )

    # =========================
    # MEASURE
    # =========================

    def read(self):

        reading = parse_reading(
            self.query("READ?")
        )

        self.wait_opc()

        return reading

    # =========================
    # FILTER
    # =========================

    def enable_averaging(
            self,
            count=5,
            tcontrol='REP'
    ):

        actual_function = (
            self.get_sense_function()
        )

        self.write_scpi(
            subsystem="SENS",
            function=f"{actual_function}:AVER:STAT",
            value="ON"
        )

        self.write_scpi(
            subsystem="SENS",
            function=f"{actual_function}:AVER:COUN",
            value=count
        )

        if tcontrol is not None:

            tcontrol = tcontrol.upper()

            if tcontrol not in SUPPORTED_TCON:

                raise ValueError(
                    f"TCON inválido: {tcontrol}"
                )

            self.write_scpi(
                subsystem="SENS",
                function=f"{actual_function}:AVER:TCON",
                value=tcontrol
            )

    def disable_averaging(self):

        return self.write_scpi(
            subsystem="SENS",
            function=f"{self.get_sense_function()}:AVER:STAT",
            value="OFF"
        )


def main():

    k24xx = Keithley24xx(
        gpib_address=22,
        timeout=10000,
        read_termination="\n",
        write_termination="\n"
    )

    k24xx.wait_opc()

    k24xx.enable_incognito_mode()

    print(k24xx.idn())

    k24xx.set_nplc(1)

    print(k24xx.get_nplc())

    k24xx.set_output_route("FRONT")

    print(k24xx.get_sense_function())

    k24xx.configure_output_format(
        voltage=True,
        current=True
    )

    k24xx.set_source_mode(mode="VOLT")

    k24xx.set_source_range(10)

    k24xx.set_source_level(5)

    k24xx.get_source_level()

    k24xx.set_sense_compliance(1)

    k24xx.set_output(on=True)

    print(k24xx.read())

    print(k24xx.read())


if __name__ == "__main__":
    main()