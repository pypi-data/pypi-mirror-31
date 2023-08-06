import rovcontrol.drivers.adc.ADCTemp as ADCTemp

import Adafruit_MCP3008
import Adafruit_GPIO.SPI as SPI

class MCP3008(ADCTemp.ADCTemp):
    def __init__(self):
        self.adaadc = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(0, 0))
        super().__init__()

    def scale(self, value, bus):
        return (value / 1023) * self.get_vref(bus)

    def update_one_channel(self, bus, channel, data):
        if data['dirty']:
            data['mv'] = self.scale(self.adaadc.read_adc(channel), bus)
        super().update_one_channel(bus, channel, data)
