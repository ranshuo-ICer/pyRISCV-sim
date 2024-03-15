
class Serial:

    def store(self, addr, value, size):
        assert size == 8, "Serial.store: size must be 8"
        print("%c" % (value & 0xff), end='')

    def load(self, addr, size):
        pass