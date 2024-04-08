from .params import *

class Csr:
    def __init__(self):
        self.csrs = [0] * NUM_CSRS
    
    def dump_csrs(self):
        print("-----------------------------")
        print("CSRs:")
        print("mstatus: {:#010x}".format(self.load(MSTATUS)))
        print("mtvec: {:#010x}".format(self.load(MTVEC)))
        print("mepc: {:#010x}".format(self.load(MEPC)))
        print("mcause: {:#010x}".format(self.load(MCAUSE)))
        print()
        print("sstatus: {:#010x}".format(self.load(SSTATUS)))
        print("stvec: {:#010x}".format(self.load(STVEC)))
        print("sepc: {:#010x}".format(self.load(SEPC)))
        print("scause: {:#010x}".format(self.load(SCAUSE)))

    def load(self, addr):
        if addr == SIE:
            return self.csrs[MIE] & self.csrs[MIDELEG]
        elif addr == SIP:
            return self.csrs[MIP] & self.csrs[MIDELEG]
        elif addr == SSTATUS:
            return self.csrs[SSTATUS] & MASK_SSTATUS
        else:
            return self.csrs[addr]

    def store(self, addr, data):
        if addr == SIE:
            self.csrs[MIE] = (self.csrs[MIE] & ~self.csrs[MIDELEG]) | (data & self.csrs[MIDELEG])
        elif addr == SIP:
            self.csrs[MIP] = (self.csrs[MIP] & ~self.csrs[MIDELEG]) | (data & self.csrs[MIDELEG])
        elif addr == SSTATUS:
            self.csrs[SSTATUS] = (self.csrs[SSTATUS] & ~MASK_SSTATUS) | (data & MASK_SSTATUS)
        else:
            self.csrs[addr] = data

    def is_medelegated(self, value):
        return ((self.csrs[MEDELEG] >> value) & 0x1) == 1
    
    def is_midelegated(self, cause):
        return ((self.csrs[MIDELEG] >> cause) & 0x1) == 1