from .params import *
from .dram import DRAM
from .serial import Serial
from .rv_exception import RVException, ExceptionType
import logging
# from cache import Cache

class BUS:
    def __init__(self, program):
        self.dram = DRAM(program)
        self.serial = Serial()

    def load(self, address, size):
        if address >= DRAM_BASE and address <= DRAM_END:
            return self.dram.load(address, size)
        elif address >= SERIAL_BASE and address <= SERIAL_END:
            return self.serial.load(address, size)
        else:
            logging.warning("LoadAccessFault at address 0x{:08x}".format(address))
            raise RVException(ExceptionType.LOAD_ACCESS_FAULT, address)
        
    def store(self, address, value, size):
        if address >= DRAM_BASE and address <= DRAM_END:
            self.dram.store(address, value, size)
        elif address >= SERIAL_BASE and address <= SERIAL_END:
            self.serial.store(address, value, size)
        else:
            logging.warning("StoreAccessFault at address 0x{:08x}".format(address))
            raise RVException(ExceptionType.STORE_AMO_ACCESS_FAULT, address)

