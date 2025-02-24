import esphome.codegen as cg
import esphome.config_validation as cv
from esphome import pins
from esphome.const import (
    CONF_ID,
    CONF_TYPE,
    CONF_KEY,
    CONF_MOSI_PIN,
    CONF_MISO_PIN,
    CONF_CLK_PIN,
    CONF_CS_PIN,
)

CONF_GDO0_PIN = "gdo0_pin"
CONF_GDO2_PIN = "gdo2_pin"

CONF_WMBUS_ID = "wmbus_id"
CONF_METER_ID = "meter_id"

CODEOWNERS = ["@SzczepanLeon"]

wmbus_ns = cg.esphome_ns.namespace('wmbus')
WMBusComponent = wmbus_ns.class_('WMBusComponent', cg.Component)
WMBusListener = wmbus_ns.class_('WMBusListener', cg.Component)

def my_key(value):
    value = cv.string_strict(value)
    parts = [value[i : i + 2] for i in range(0, len(value), 2)]
    if (len(parts) != 16) and (len(parts) != 0):
        raise cv.Invalid("Key must consist of 16 hexadecimal numbers")
    parts_int = []
    if any(len(part) != 2 for part in parts):
        raise cv.Invalid("Key must be format XX")
    for part in parts:
        try:
            parts_int.append(int(part, 16))
        except ValueError:
            # pylint: disable=raise-missing-from
            raise Invalid("Key must be hex values from 00 to FF")
    return "".join(f"{part:02X}" for part in parts_int)

METER_LISTENER_SCHEMA = cv.Schema(
    {
        cv.GenerateID(CONF_WMBUS_ID): cv.use_id(WMBusComponent),
        cv.Required(CONF_METER_ID): cv.hex_int,
        cv.Optional(CONF_TYPE, default="unknown"): cv.string_strict,
        cv.Optional(CONF_KEY, default=""): my_key,
    }
)

TEXT_LISTENER_SCHEMA = cv.Schema(
    {
        cv.GenerateID(CONF_WMBUS_ID): cv.use_id(WMBusComponent),
        cv.Optional(CONF_METER_ID, default=0xAFFFFFF5): cv.hex_int,
        cv.Optional(CONF_TYPE, default="text"): cv.string_strict,
    }
)

CONFIG_SCHEMA = cv.Schema({
    cv.GenerateID(): cv.declare_id(WMBusComponent),
    cv.Optional(CONF_MOSI_PIN, default=13): pins.internal_gpio_output_pin_schema,
    cv.Optional(CONF_MISO_PIN, default=12): pins.internal_gpio_input_pin_schema,
    cv.Optional(CONF_CLK_PIN,  default=14): pins.internal_gpio_output_pin_schema,
    cv.Optional(CONF_CS_PIN,   default=2):  pins.internal_gpio_output_pin_schema,
    cv.Optional(CONF_GDO0_PIN, default=5):  pins.internal_gpio_input_pin_schema,
    cv.Optional(CONF_GDO2_PIN, default=4):  pins.internal_gpio_input_pin_schema,
})


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)

    mosi = await cg.gpio_pin_expression(config[CONF_MOSI_PIN])
    miso = await cg.gpio_pin_expression(config[CONF_MISO_PIN])
    clk = await cg.gpio_pin_expression(config[CONF_CLK_PIN])
    cs = await cg.gpio_pin_expression(config[CONF_CS_PIN])
    gdo0 = await cg.gpio_pin_expression(config[CONF_GDO0_PIN])
    gdo2 = await cg.gpio_pin_expression(config[CONF_GDO2_PIN])

    cg.add(var.add_cc1101(mosi, miso, clk, cs, gdo0, gdo2))

    cg.add_library(
        None,
        None,
        "https://github.com/SzczepanLeon/wMbus-lib@0.9.11",
    )