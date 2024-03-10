from .params import *

class DRAM:
    def __init__(self, program):
        self.size = DRAM_SIZE
        self.data = [0] * DRAM_SIZE 
        self.data[:len(program)] = program

    def load(self, address, size):
        if size != 8 and size!= 16 and size!= 32:
            raise ValueError(f"Invalid size, size should be 8, 16 or 32, but got {size}")
        
        nbytes = size // 8
        index = address - DRAM_BASE
        if index < 0 or index + nbytes > DRAM_SIZE:
            raise ValueError("Invalid address")
        
        data = self.data[index:index+nbytes]
        return int.from_bytes(data, byteorder='little')
    
    def store(self, address, value, size):
        if size != 8 and size!= 16 and size != 32:
            raise ValueError(f"Invalid size, size should be 8, 16 or 32, but got {size}")
        
        nbytes = size // 8
        index = address - DRAM_BASE
        if index < 0 or index + nbytes > DRAM_SIZE:
            raise ValueError("Invalid address")
        data = list(int.to_bytes(value, nbytes, byteorder='little'))
        self.data[index:index+nbytes] = data