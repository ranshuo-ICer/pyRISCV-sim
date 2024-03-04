import logging
from .params import *
from .bus import BUS

def uppack_inst(inst):
    rd = (inst >> 7) & 0x1F
    rs1 = (inst >> 15) & 0x1F
    rs2 = (inst >> 20) & 0x1F
    return rd, rs1, rs2

def to_signed(val, bits):
    if val & (1 << (bits - 1)):
        return val - (1 << bits)
    else:
        return val

def get_imm(inst, signed=True):
    imm = inst >> 20
    if signed:
        return to_signed(imm, 12)
    else:
        return imm


class InstructionExecutor:


    def execute_srli(self, cpu, inst):
        rd, rs1, _ = uppack_inst(inst)
        shamt = (inst >> 20) & 0x1F
        cpu.regs[rd] = cpu.regs[rs1] >> shamt & (0xFFFFFFFF >> shamt)
        return cpu.update_pc()

    def execute_srai(self, cpu, inst):
        rd, rs1, _ = uppack_inst(inst)
        shamt = (inst >> 20) & 0x1F
        cpu.regs[rd] = cpu.regs[rs1] >> shamt
        return cpu.update_pc()

    def execute_funct70x5(self, cpu, inst):
        funct7 = (inst >> 25) & 0x7F
        logging.debug("funct7: {:#010x}".format(funct7))
        if funct7 == 0x00:  # c.srli
            return self.execute_srli(cpu, inst)
        elif funct7 == 0x20:  # c.srai
            return self.execute_srai(cpu, inst)
        else:
            raise Exception("Invalid funct7: {:#010x}".format(funct7))

    def execute_fence(self, cpu, inst):
        logging.debug("FENCE")
        return cpu.update_pc()

    def execute_lb(self, cpu, inst):
        rd, rs1, _ = uppack_inst(inst)
        imm = get_imm(inst)
        logging.debug("LB: x{} = mem[x{} + {}]".format(rd, rs1, imm))
        cpu.regs[rd] = to_signed(cpu.load(cpu.regs[rs1] + imm, 8), 8)
        return cpu.update_pc()
    
    def execute_lh(self, cpu, inst):
        rd, rs1, _ = uppack_inst(inst)
        imm = get_imm(inst)
        logging.debug("LH: x{} = mem[x{} + {}]".format(rd, rs1, imm))
        cpu.regs[rd] = to_signed(cpu.load(cpu.regs[rs1] + imm, 16), 16)
        return cpu.update_pc()
    
    def execute_lw(self, cpu, inst):
        rd, rs1, _ = uppack_inst(inst)
        imm = get_imm(inst)
        logging.debug("LW: x{} = mem[x{} + {}]".format(rd, rs1, imm))
        cpu.regs[rd] = to_signed(cpu.load(cpu.regs[rs1] + imm, 32), 32)
        return cpu.update_pc()
    
    def execute_ld(self, cpu, inst):
        rd, rs1, _ = uppack_inst(inst)
        imm = get_imm(inst)
        logging.debug("LD: x{} = mem[x{} + {}]".format(rd, rs1, imm))
        cpu.regs[rd] = to_signed(cpu.load(cpu.regs[rs1] + imm, 64), 64)
        return cpu.update_pc()

    def execute_lbu(self, cpu, inst):
        rd, rs1, _ = uppack_inst(inst)
        imm = get_imm(inst)
        logging.debug("LBU: x{} = mem[x{} + {}]".format(rd, rs1, imm))
        cpu.regs[rd] = cpu.load(cpu.regs[rs1] + imm, 8)
        return cpu.update_pc()
    
    def execute_lhu(self, cpu, inst):
        rd, rs1, _ = uppack_inst(inst)
        imm = get_imm(inst)
        logging.debug("LHU: x{} = mem[x{} + {}]".format(rd, rs1, imm))
        cpu.regs[rd] = cpu.load(cpu.regs[rs1] + imm, 16)
        return cpu.update_pc()

    def execute_lwu(self, cpu, inst):
        rd, rs1, _ = uppack_inst(inst)
        imm = get_imm(inst)
        logging.debug("LWU: x{} = mem[x{} + {}]".format(rd, rs1, imm))
        cpu.regs[rd] = cpu.load(cpu.regs[rs1] + imm, 32)
        return cpu.update_pc()

    def execute_addi(self, cpu, inst):
        rd, rs1, _ = uppack_inst(inst)
        imm = get_imm(inst)
        logging.debug("ADDI: x{} = x{} + {}".format(rd, rs1, imm))
        cpu.regs[rd] = cpu.regs[rs1] + imm
        return cpu.update_pc()
    
    def execute_slli(self, cpu, inst):
        rd, rs1, _ = uppack_inst(inst)
        shamt = (inst >> 20) & 0x1F
        logging.debug("SLLI: x{} = x{} << {}".format(rd, rs1, shamt))
        cpu.regs[rd] = cpu.regs[rs1] << shamt
        return cpu.update_pc()
    
    def execute_slti(self, cpu, inst):
        rd, rs1, _ = uppack_inst(inst)
        imm = get_imm(inst)
        logging.debug("SLTI: x{} = x{} < {}".format(rd, rs1, imm))
        cpu.regs[rd] = 1 if cpu.regs[rs1] < imm else 0
        return cpu.update_pc()  
    
    def execute_sltiu(self, cpu, inst):
        rd, rs1, _ = uppack_inst(inst)
        imm = get_imm(inst, signed=False)
        unsigned_rs1 = cpu.regs[rs1] & 0xFFFFFFFF
        logging.debug("SLTIU: x{} = x{} < {}".format(rd, rs1, imm))
        cpu.regs[rd] = 1 if unsigned_rs1 < imm else 0
        return cpu.update_pc()  
    
    def execute_xori(self, cpu, inst):
        rd, rs1, _ = uppack_inst(inst)
        imm = get_imm(inst)
        logging.debug("XORI: x{} = x{} ^ {}".format(rd, rs1, imm))
        cpu.regs[rd] = cpu.regs[rs1] ^ imm
        return cpu.update_pc()
    
    def execute_ori(self, cpu, inst):
        rd, rs1, _ = uppack_inst(inst)
        imm = get_imm(inst)
        logging.debug("ORI: x{} = x{} | {}".format(rd, rs1, imm))
        cpu.regs[rd] = cpu.regs[rs1] | imm
        return cpu.update_pc()

    def execute_andi(self, cpu, inst):
        rd, rs1, _ = uppack_inst(inst)
        imm = get_imm(inst)
        logging.debug("ANDI: x{} = x{} & {}".format(rd, rs1, imm))
        cpu.regs[rd] = cpu.regs[rs1] & imm
        return cpu.update_pc()

    def execute_add(self, cpu, inst):
        rd, rs1, rs2 = uppack_inst(inst)
        logging.debug("ADD: x{} = x{} + x{}".format(rd, rs1, rs2))
        cpu.regs[rd] = cpu.regs[rs1] + cpu.regs[rs2]
        return cpu.update_pc()
    
    def excute_lui(self, cpu, inst):
        rd, _, _ = uppack_inst(inst)
        imm = inst & 0xFFFFF000
        imm = imm - (1 << 32) if imm >> 31 == 1 else imm
        logging.debug("LUI: x{} = {:#010x}".format(rd, abs(imm)))
        cpu.regs[rd] = imm
        return cpu.update_pc()
    
    def execute_auipc(self, cpu, inst):
        rd, _, _ = uppack_inst(inst)
        imm = inst & 0xFFFFF000
        imm = imm - (1 << 32) if imm >> 31 == 1 else imm
        logging.debug("AUIPC: x{} = {:#010x}".format(rd, abs(cpu.pc + imm)))
        cpu.regs[rd] = cpu.pc + imm
        return cpu.update_pc()
    
    def execute_jal(self, cpu, inst):
        rd, _, _ = uppack_inst(inst)
        imm = (0xFFF00000 if inst >> 31 == 1 else 0) | \
                (inst & 0x000FF000) | \
                ((inst >> 9) & 0x00008000) | \
                ((inst >> 20) & 0x7FE)
        logging.debug("JAL: x{} = {:#010x}, PC = {:#010x} + {:#010x}".format(rd, cpu.pc + 4, cpu.pc, imm))
        cpu.regs[rd] = cpu.pc + 4
        return cpu.pc + imm
    
    def execute_jalr(self, cpu, inst):
        rd, rs1, _ = uppack_inst(inst)
        imm = get_imm(inst)
        logging.debug("JALR: x{} = {:#010x}, PC = x{} + {:#010x}".format(rd, cpu.pc + 4, rs1, imm))
        cpu.regs[rd] = cpu.pc + 4
        return (cpu.regs[rs1] + imm) & 0xFFFFFFFE

    def execute(self, cpu, inst):
        op = inst & 0x7F
        funct3 = (inst >> 12) & 0x7
        cpu.regs[0] = 0  # set x0 to 0
        logging.debug("Executing instruction: {:#010x}, funct3: {:#04x}".format(inst, funct3))
        instruction_map = {
            0x37: self.excute_lui,
            0x17: self.execute_auipc,
            0x6F: self.execute_jal,
            0x67: self.execute_jalr,
            0x03:{
                0x0: self.execute_lb,
                0x1: self.execute_lh,
                0x2: self.execute_lw,
                0x3: self.execute_ld,
                0x4: self.execute_lbu,
                0x5: self.execute_lhu,
                0x6: self.execute_lwu
            },
            0x0f:{
                0x0: self.execute_fence
            },
            0x13:{
                0x00: self.execute_addi,
                0x01: self.execute_slli,
                0x02: self.execute_slti,
                0x03: self.execute_sltiu,
                0x04: self.execute_xori,
                0x05: self.execute_funct70x5,
                0x06: self.execute_ori,
                0x07: self.execute_andi,
            },
            0x33:{
                0x00: self.execute_add,
            }
        }
        exe = instruction_map.get(op, None)
        if exe is None:
            raise Exception("Invalid opcode: {:#010x}".format(op))
        if isinstance(exe, dict):
            exe = exe.get(funct3, None)
            if exe is None:
                raise Exception("Invalid funct3: {:#04x}".format(funct3))
            return exe(cpu, inst)
        else:
            return exe(cpu, inst)


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

    def load(self, address, size):
        return self.bus.load(address, size)
    
    def store(self, address, value, size):
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
