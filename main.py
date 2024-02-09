import sys
from machine import I2C, Pin
from sensor_pack_2.bus_service import I2cAdapter
import veml6040mod
import time


def show_colors(clrs: [tuple, None], _lux: float = 0, hex_format: bool = False):
    """Выводит инфу о цветах и освещенности в люксах"""
    if tuple is None:
        return
    if hex_format:
        print(f"Red: 0x{clrs[0]:X}; Green: 0x{clrs[1]:X}; Blue: 0x{clrs[2]:X}; White: 0x{clrs[3]:X};")
        return
    print(f"Red: {clrs[0]}; Green: {clrs[1]}; Blue: {clrs[2]}; White: {clrs[3]}; lux: {_lux}")


def show_info(integr_time: int):
    _g_sens, _max_lux = veml6040mod.get_g_max_lux(integr_time)
    print(f"g sensitivity: {_g_sens}; max detectable lux: {_max_lux}")


def get_als_lux(green_channel: int, sensitivity: float) -> float:
    """возвращает освещенность в люксах по данным зеленого канала"""
    return sensitivity * green_channel


if __name__ == '__main__':
    i2c = I2C(id=1, scl=Pin(7), sda=Pin(6), freq=400_000)  # on Raspberry Pi Pico
    adapter = I2cAdapter(i2c)
    sensor = veml6040mod.VEML6040(adapter)
    if sensor.shutdown:
        sensor.shutdown = False
    wait_func = time.sleep_ms
    print("Режим однократных измерений!")
    sensor.start_measurement(integr_time=3, auto_mode=False)
    wait_time_ms = sensor.get_conversion_cycle_time()
    print(f"integration time: {sensor.integration_time}")
    show_info(sensor.integration_time)
    g_sens, max_lux = veml6040mod.get_g_max_lux(sensor.integration_time)
    print(f"Запуск измерения датчика явно из кода!")
    print(f"wait_time_ms: {wait_time_ms} мс")
    for _ in range(100):
        wait_func(wait_time_ms)
        colors = sensor.get_colors()
        lux = get_als_lux(colors[1], g_sens)
        show_colors(colors, lux)
        sensor.start_measurement(integr_time=3, auto_mode=False)

    print(32*"-")
    sensor.start_measurement(integr_time=2, auto_mode=True)
    wait_time_ms = sensor.get_conversion_cycle_time()
    print(f"Автоматический запуск измерения датчиком!")
    print(f"Использование протокола итератора. wait_time_ms: {wait_time_ms} мс")
    print(f"integration time: {sensor.integration_time}")
    show_info(sensor.integration_time)
    g_sens, max_lux = veml6040mod.get_g_max_lux(sensor.integration_time)

    counter = 0
    for colors in sensor:
        wait_func(wait_time_ms)
        if colors:
            lux = get_als_lux(colors[1], g_sens)
            show_colors(colors, lux)
        else:
            print(f"shutdown: {sensor.shutdown}; auto mode: {sensor.auto_mode}; it: {sensor.integration_time} [ms];")
        counter += 1
        if counter > 1000:
            # завершаю программу
            sys.exit(0)
