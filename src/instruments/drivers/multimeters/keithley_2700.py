import re
import time

from instruments.drivers.instruments.SCPIInstrument import (
    SCPIInstrument,
    SUPPORTED_FUNCTIONS,
    SUPPORTED_TCON,
    SUPPORTED_TEMPERATURE_TRANSDUCERS,
    SUPPORTED_TCOUPLES,
    SUPPORTED_FRTDS
)

from src.instruments.models.configuration_models import MultimeterConfig


# =========================
# STATIC FUNCTIONS
# =========================

def parse_reading(raw):
    raw = re.sub(r'[^\x20-\x7E]', '', raw)

    parts = raw.strip().split(",")

    parsed = {}

    for part in parts:
        if "SECS" in part:
            parsed["time"] = float(part.replace("SECS", ""))

        elif "RDNG" in part:
            parsed["reading_number"] = int(part.replace("RDNG#", ""))

        elif "C" in part:
            parsed["value"] = float(part.replace("C", ""))

        else:
            try:
                parsed["value"] = float(part)
            except:
                pass

    return parsed


def parse_channel_list(value):

    if value is None:
        return []

    if isinstance(value, list):
        return value

    if not isinstance(value, str):
        raise ValueError(f"Unsupported type for channel parsing: {type(value)}")

    cleaned = (
        value
        .strip()
        .replace("@", "")
        .replace("(", "")
        .replace(")", "")
    )

    result = []

    for item in cleaned.split(","):

        item = item.strip()

        if not item:
            continue

        try:
            result.append(int(item))

        except ValueError:
            raise ValueError(f"Invalid channel value: '{item}'")

    return result


class Keithley2700(SCPIInstrument):

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

        resource_name = f"GPIB{gpib_card}::{gpib_address}::INSTR"

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

    # =========================
    # CONFIG
    # =========================

    def enable_scan(self, enable=False):

        self.write_scpi(
            subsystem="ROUT",
            function="SCAN:LSEL",
            value="INT" if enable else "NONE"
        )

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

        self.enable_scan(enable=False)

        self.configure_output_format()

        self.enable_auto_zero()

    def configure(self, cfg: MultimeterConfig):

        # =========================
        # GPIB
        # =========================

        gpib_cfg = cfg.gpib

        current_resource = self.inst.resource_name

        new_resource = (
            f"GPIB{gpib_cfg.gpib_card}::"
            f"{gpib_cfg.address}::INSTR"
        )

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

        # =========================
        # TEMPERATURE
        # =========================

        temp_cfg = cfg.temperature

        self.set_function("TEMP")

        if temp_cfg.sensor:

            self.configure_temperature_transducer(
                transducer=temp_cfg.sensor.type,
                transducer_type=temp_cfg.sensor.subtype
            )

        if temp_cfg.measure.nplc:

            self.set_nplc(
                nplc=temp_cfg.measure.nplc
            )

        if temp_cfg.measure.measurement_resolution:

            self.set_measurement_resolution(
                n_digits=temp_cfg.measure.measurement_resolution
            )

        if temp_cfg.averaging:

            avg = temp_cfg.averaging

            if avg.enabled:

                self.enable_averaging(
                    count=avg.count,
                    tcontrol=avg.type,
                    window=avg.window
                )

            else:

                self.disable_averaging()

        # =========================
        # CHANNELS
        # =========================

        enabled_channels = [
            ch.channel
            for ch in temp_cfg.channels.values()
            if ch.enabled
        ]

        if enabled_channels:
            pass

    # =========================
    # DISPLAY
    # =========================

    def enable_display(self, enable=True):

        return self.write_scpi(
            subsystem="DISP",
            function="ENAB",
            value=enable
        )

    # =========================
    # FORMAT
    # =========================

    def configure_output_format(
            self,
            read=True,
            time=False,
            unit=False,
            status=False,
            channel=False,
            reading_number=False
    ):

        elements = []

        if read:
            elements.append("READ")

        if time:
            elements.append("TIME")

        if unit:
            elements.append("UNIT")

        if status:
            elements.append("STAT")

        if channel:
            elements.append("CHAN")

        if reading_number:
            elements.append("NUM")

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
    # ROUTE
    # =========================

    def close_channels(self, channels=None, delay=0.1):

        if isinstance(channels, list):

            cmd = self.write_scpi(
                subsystem="ROUT",
                function="MULT:CLOS",
                channels=channels
            )

        else:

            cmd = self.write_scpi(
                subsystem="ROUT",
                function="CLOS",
                channels=channels
            )

        if delay:
            time.sleep(delay)

        return cmd

    def open_all_channels(self):

        return self.write_scpi(
            subsystem="ROUT",
            function="OPEN:ALL"
        )

    def are_channels_closed(self, channels=None):

        response = self.query_scpi(
            subsystem="ROUTE",
            function="CLOS:STAT",
            channels=channels,
            debug=True
        )

        return [
            int(x.strip())
            for x in response.split(",")
            if x.strip()
        ]

    def get_closed_channels(self):

        return self.query_scpi(
            subsystem="ROUTE",
            function="CLOS",
            debug=True
        )

    # =========================
    # SENSE
    # =========================

    def set_nplc(self, nplc=1.0, channel_list=None):

        return self.write_scpi(
            subsystem="SENS",
            function=f"{self.get_function()}:NPLC",
            value=nplc,
            channels=channel_list
        )

    def get_nplc(self, channel_list=None):

        return self.query_scpi(
            subsystem="SENS",
            function=f"{self.get_function()}:NPLC",
            channels=channel_list
        )

    def set_measurement_resolution(
            self,
            n_digits=6,
            channel_list=None
    ):

        return self.write_scpi(
            subsystem="SENS",
            function=f"{self.get_function()}:DIG",
            value=n_digits,
            channels=channel_list
        )

    def get_measurement_resolution(self, channel_list=None):

        return self.query_scpi(
            subsystem="SENS",
            function=f"{self.get_function()}:DIG",
            channels=channel_list
        )

    def set_function(self, function: str):

        function = function.upper()

        if function not in SUPPORTED_FUNCTIONS:
            raise ValueError(f"Función no válida: {function}")

        return self.write_scpi(
            subsystem="SENS",
            function="FUNC",
            value=function,
            quoted=True
        )

    def get_function(self, channel_list=None):

        response = self.query_scpi(
            subsystem="SENS",
            function="FUNC",
            channels=channel_list
        )

        return response.strip().replace('"', '')

    def configure_temperature_transducer(
            self,
            transducer='FRTD',
            transducer_type='PT100',
            channels=None
    ):

        if transducer is None or transducer_type is None:
            raise ValueError(
                "Transducer type y transducer subtype "
                "deben ser valores str"
            )

        transducer = transducer.upper()
        transducer_type = transducer_type.upper()

        if transducer not in SUPPORTED_TEMPERATURE_TRANSDUCERS:
            raise ValueError(f"Transducer no válido: {transducer}")

        if (
                transducer == "TC"
                and transducer_type not in SUPPORTED_TCOUPLES
        ):
            raise ValueError(
                f"Thermocouple no válida: {transducer_type}"
            )

        if (
                transducer == "FRTD"
                and transducer_type not in SUPPORTED_FRTDS
        ):
            raise ValueError(
                f"FRTD no válida: {transducer_type}"
            )

        self.write_scpi(
            subsystem="SENS",
            function="TEMP:TRAN",
            value=transducer,
            channels=channels
        )

        if transducer == "TC":

            self.write_scpi(
                subsystem="SENS",
                function="TEMP:TC:TYPE",
                value=transducer_type,
                channels=channels
            )

        if transducer == "FRTD":

            self.write_scpi(
                subsystem="SENS",
                function="TEMP:FRTD:TYPE",
                value=transducer_type,
                channels=channels
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
    # UNIT
    # =========================

    def set_unit(self, unit=None):

        return self.write_scpi(
            subsystem="UNIT",
            function=self.get_function(),
            value=unit
        )

    def get_unit(self, channel_list=None):

        return self.query_scpi(
            subsystem="UNIT",
            function=self.get_function(),
            channels=channel_list
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
            tcontrol='REP',
            window=None
    ):

        actual_function = self.get_function()

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

        if window is not None:

            if tcontrol != "MOV":

                raise ValueError(
                    "WINDOW solo es válido cuando TCON = MOV"
                )

            self.write_scpi(
                subsystem="SENS",
                function=f"{actual_function}:AVER:WIND",
                value=window
            )

    def disable_averaging(self):

        return self.write_scpi(
            subsystem="SENS",
            function=f"{self.get_function()}:AVER:STAT",
            value="OFF"
        )


def main():

    k2700 = Keithley2700(
        gpib_address=14,
        timeout=10000,
        read_termination="\n",
        write_termination="\n"
    )

    k2700.init_config()

    k2700.set_function(function="TEMP")

    k2700.set_unit(unit="C")

    k2700.set_measurement_resolution(n_digits=5)

    k2700.configure_temperature_transducer(
        transducer='FRTD',
        transducer_type='PT100'
    )

    k2700.set_nplc(1)

    k2700.enable_averaging(
        count=2,
        tcontrol="REP",
        window=None
    )

    k2700.enable_scan(enable=False)

    k2700.open_all_channels()

    k2700.close_channels(
        channels=[104, 114, 124, 125]
    )

    k2700.wait_opc()

    print(
        k2700.are_channels_closed(
            channels=[104, 114, 105, 115]
        )
    )

    print(
        k2700.get_closed_channels()
    )

    while True:

        result = k2700.read()

        k2700.wait_opc()

        print(result)

        time.sleep(1)


if __name__ == "__main__":
    main()