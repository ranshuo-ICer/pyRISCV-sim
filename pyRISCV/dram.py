from .params import *
import logging
from .rv_exception import RVException, ExceptionType

class DRAM:
    def __init__(self, program):
        self.size = DRAM_SIZE
        self.data = [0] * DRAM_SIZE 
        self.data[:len(program)] = program

    def load(self, address, size):
        if size != 8 and size!= 16 and size!= 32:
            logging.warning(f"Invalid size, size should be 8, 16 or 32, but got {size}")
            raise RVException(ExceptionType.LOAD_ACCESS_FAULT, address)
        
        nbytes = size // 8
        index = address - DRAM_BASE
        if index < 0 or index + nbytes > DRAM_SIZE:
            logging.warning(f"Invalid address {address}")
            raise RVException(ExceptionType.LOAD_ACCESS_FAULT, address)
        
        data = self.data[index:index+nbytes]
        return int.from_bytes(data, byteorder='little')
    
    def store(self, address, value, size):
        if size != 8 and size!= 16 and size != 32:
            logging.warning(f"Invalid size, size should be 8, 16 or 32, but got {size}")
            raise RVException(ExceptionType.STORE_AMO_ACCESS_FAULT, address)
        
        nbytes = size // 8
        index = address - DRAM_BASE
        if index < 0 or index + nbytes > DRAM_SIZE:
            logging.warning(f"Invalid address {address}")
            raise RVException(ExceptionType.STORE_AMO_ACCESS_FAULT, address)
        data = list(int.to_bytes(value, nbytes, byteorder='little'))
        self.data[index:index+nbytes] = data