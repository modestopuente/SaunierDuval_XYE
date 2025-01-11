DOMAIN = "xye_saunier_duval"
"""Constants for the Stecagrid integration."""

CONF_XYE_HOST = "xye_host"
CONF_XYE_PORT = "xye_port"
CONF_XYE_TARGET = "xye_target"
CONF_XYE_SOURCE = "xye_source"
CONF_XYE_POLL = "scan_interval"
DEFAULT_INVERTER_POLLRATE = 5

MIN_TARGET_TEMP = 12
MAX_TARGET_TEMP = 30
TARGET_TEMP_STEP = 1
DEFAULT_SCAN_INTERVAL = 30
DEFAULT_CONF_DEVICE_ID = 0
DEFAULT_CONF_SOURCE = 0x33

class xye_const:
    PREAMBLE = 0xAA
    PROLOGUE = 0x55
    #MASTERID = 0x33
    FROMMASTER = 0x80
    PAYLOAD = [0x00,0x00,0x00,0x00,0x00,0x00,0x00]
    OFFSET =0x30

class xye_cmd:
    QUERY = 0xc0
    SET = 0xc3
    LOCK = 0xcc
    UNLOCK = 0xcd
    

#Oper Mode	0x00 - off, 0x80 - auto, 0x88 - Cool, 0x82 - Dry, 0x84 - Heat, 0x81 - Fan
class xye_mode:
    OFF = 0x00
    AUTO = 0x80
    COOL = 0x88
    DRY = 0x82
    HEAT = 0x84
    FAN = 0x81

# Fan	0x80 - Auto, 0x01 - High, 0x02 - Medium, 0x03 - Low
class xye_fan_speed:
    AUTO = 0x80
    HIGH = 0x01
    MEDIUM = 0x02
    LOW = 0x04
    OFF = 0x00


#Mode Flags	0x02 - Aux Heat (Turbo), 0x00 - norm, 0x01 - ECO Mode (sleep), 0x04 - SWING, 0x88 VENT
class mode_flag:
    AUXHEAT = 0x02
    NORM = 0x00
    ECO = 0x01
    SWING = 0x04
    VENT = 0x88

#Oper Flags	0x04 - water pump running, 0x80 - locked
class oper_flag:
    NORM = 0x00
    PUMPON = 0x04
    LOCKED = 0x88