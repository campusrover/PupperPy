from busio import I2C as _bI2C
from adafruit_blinka.microcontroller.generic_linux.i2c import I2C as _I2C
try:
    import threading
except ImportError:
    threading = None


class I2C(_bI2C):
    def __init__(self, port_id, sda, scl, frequency=400000):
        self.init(port_id, sda, scl, frequency)

    def init(self, port_id, sda, scl, frequency):
        self.deinit()
        self._i2c = _I2C(port_id, mode=_I2C.MASTER, baudrate=frequency)
        if threading is not None:
            self._lock = threading.RLock()
