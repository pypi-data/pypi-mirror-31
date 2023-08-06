import rovcontrol.drivers.current.CurrentTemp as CurrentTemp
import rovcontrol.drivers.abstract.ADCBlock as ADCBlock

class PololuCurrent(CurrentTemp.CurrentTemp):
    VREF = 5000
    def __init__(self, channels, adcl):
        adcl.set_vref(self.VREF)
        self.adcl = adcl
        super().__init__(channels)

    def scale(self, value):
        return 1000 * (value - 50) / 20.0

    def update_one_channel(self, channel, data):
        if data['dirty']:
            data['current'] = self.scale(adcl.get_mv(channel))
        super().update_one_channel(channel, data)
