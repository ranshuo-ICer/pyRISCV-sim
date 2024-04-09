import logging
from .params import *
from .bus import BUS
from .csr import Csr
from .instruction_executor import InstructionExecutor
from .rv_exception import RVException, ExceptionType
from .rv_enum import PrivilegeLevel

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
        address &= 0xFFFFFFFF  # make sure address is unsigned 32-bit
        return self.bus.load(address, size)
    
    def store(self, address, value, size):
        address &= 0xFFFFFFFF  # make sure address is unsigned 32-bit
        self.bus.store(address, value, size)

    def update_pc(self):
        return self.pc + 4

    def fetch(self):
        try:
            inst = self.load(self.pc, 32)
            return inst
        except RVException:
            logging.warning("Error fetching instruction at address 0x{:08x}".format(self.pc))
            raise RVException(ExceptionType.INSTRUCTION_ACCESS_FAULT, self.pc)
    
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

    def handle_exception(self, exception):
        logging.warning("Exception occurred: {}".format(exception))
        pc = self.pc
        privaledgeLevel = self.privilegeLevel
        cause = exception.get_type()
        trap_in_s_mode = (privaledgeLevel.value <= PrivilegeLevel.SUPERVISOR.value) and self.csr.is_medelegated(cause.value)
        if trap_in_s_mode:
            logging.warning("Exception is delegated to supervisor mode")
            self.privilegeLevel = PrivilegeLevel.SUPERVISOR
            STATUS = SSTATUS
            TVEC = STVEC
            CAUSE = SCAUSE
            TVAL = STVAL
            EPC = SEPC
            MASK_PIE = MASK_SPIE
            pie_i = 5
            MASK_IE = MASK_SIE
            ie_i = 1
            MASK_PP = MASK_SPP
            pp_i = 8
        else:
            self.privilegeLevel = PrivilegeLevel.MACHINE
            STATUS = MSTATUS
            TVEC = MTVEC
            CAUSE = MCAUSE
            TVAL = MTVAL
            EPC = MEPC
            MASK_PIE = MASK_MIE
            pie_i = 7
            MASK_IE = MASK_MIE
            ie_i = 3
            MASK_PP = 0
            pp_i = 11
        
        self.pc = self.csr.load(TVEC) & 0xFFFFFFFC  # set PC to base address of vector
        self.csr.store(EPC, pc)  # set EPC to faulting instruction address
        self.csr.store(CAUSE, cause)  # set CAUSE to exception type
        self.csr.store(TVAL, exception.get_value())  # set TVAL to exception value

        status = self.csr.load(STATUS)  # get current status
        ie = (status & MASK_IE) >> ie_i  # get IE bit
        status = (status & ~MASK_PIE) | (ie << pie_i)  # set PIE bit if IE bit is set
        status &= ~MASK_IE  # clear IE bit
        status = (status & ~MASK_PP) | (privaledgeLevel.value << pp_i)  # set PP to current privilege level
        self.csr.store(STATUS, status)  # update status with new IE and PP bits