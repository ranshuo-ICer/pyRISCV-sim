import logging
from .params import *
from .bus import BUS
from .csr import Csr
from .instruction_executor import InstructionExecutor

class CPU(object):

    RVABI = [
        "zero", "ra", "sp", "gp", "tp", "t0", "t1", "t2",
        "s0", "s1", "a0", "a1", "a2", "a3", "a4", "a5",
        "a6", "a7", "s2", "s3", "s4", "s5", "s6", "s7",
        "s8", "s9", "s10", "s11", "t3", "t4", "t5", "t6",
    ]

    instructionExecutor = InstructionExecutor()

    def __init__(self, program):
        self.pc = DRAM_BASE  # set program counter to start of DRAM
        self.regs = [0] * 32
        self.bus = BUS(program)
        
        self.regs[2] = DRAM_END  # set stack pointer to end of DRAM
        self.csr = Csr()
        self.privilegeLevel = PrivilegeLevel.MACHINE

    def load(self, address, size):
        address &= 0xFFFFFFFF  # make sure address is 32-bit
        return self.bus.load(address, size)
    
    def store(self, address, value, size):
        address &= 0xFFFFFFFF  # make sure address is 32-bit
        self.bus.store(address, value, size)

    def update_pc(self):
        return self.pc + 4

    def fetch(self):
        return self.load(self.pc, 32)
    
    def execute(self, inst):
        exe = self.instructionExecutor.execute(self, inst)
        return exe

    def dump_regs(self):
        print("------------------------------------------")
        print("Registers:\tDecimal\t\t\tHex")
        for i in range(32):
            dec = self.regs[i]
            print("x{} ({}):\t{:#10d}\t\t{:#010x}".format(i, self.RVABI[i], dec, dec))

    def dump_pc(self):
        print("------------------------------------------")
        print("PC:\t\t{}\t\t{}".format(self.pc, hex(self.pc)))
