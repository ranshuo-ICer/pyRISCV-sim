from .params import *
import logging
from .rv_enum import *

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

    def excute_lui(self, cpu, inst):
        rd, _, _ = uppack_inst(inst)
        imm = to_signed(inst & 0xFFFFF000, 32)
        logging.debug("LUI: x{} = {:#010x}".format(rd, imm))
        cpu.regs[rd] = imm
        return cpu.update_pc()
    
    def execute_auipc(self, cpu, inst):
        rd, _, _ = uppack_inst(inst)
        imm = to_signed(inst & 0xFFFFF000, 32)
        logging.debug("AUIPC: x{} = {:#010x}".format(rd, (cpu.pc + imm)))
        cpu.regs[rd] = cpu.pc + imm
        return cpu.update_pc()
    
    def execute_jal(self, cpu, inst):
        rd, _, _ = uppack_inst(inst)
        imm = (0xFFF00000 if inst >> 31 == 1 else 0) | \
                (inst & 0x000FF000) | \
                ((inst >> 9) & 0x00000800) | \
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

    def execute_beq(self, cpu, inst):
        _, rs1, rs2 = uppack_inst(inst)
        sign = (inst >> 31) & 0x1
        imm = to_signed(sign << 12 | ((inst >> 7) & 0x1E) | ((inst >> 20) & 0x7e0) | ((inst << 4) & 0x800), 13)
        logging.debug("BEQ: x{} = x{}? pc = {:#010x} + {:#010x}".format(rs1, rs2, cpu.pc, imm))
        if cpu.regs[rs1] == cpu.regs[rs2]:
            return cpu.pc + imm
        else:
            return cpu.update_pc()
        
    def execute_bne(self, cpu, inst):
        _, rs1, rs2 = uppack_inst(inst)
        sign = (inst >> 31) & 0x1
        imm = to_signed(sign << 12 | ((inst >> 7) & 0x1E) | ((inst >> 20) & 0x7e0) | ((inst << 4) & 0x800), 13)
        logging.debug("BNE: x{} = x{}? pc = {:#010x} + {:#010x}".format(rs1, rs2, cpu.pc, imm))
        if cpu.regs[rs1] != cpu.regs[rs2]:
            return cpu.pc + imm
        else:
            return cpu.update_pc()
        
    def execute_blt(self, cpu, inst):
        _, rs1, rs2 = uppack_inst(inst)
        sign = (inst >> 31) & 0x1
        imm = to_signed(sign << 12 | ((inst >> 7) & 0x1E) | ((inst >> 20) & 0x7e0) | ((inst << 4) & 0x800), 13)
        logging.debug("BLT: x{} = x{}? pc = {:#010x} + {:#010x}".format(rs1, rs2, cpu.pc, imm))
        if cpu.regs[rs1] < cpu.regs[rs2]:
            return cpu.pc + imm
        else:
            return cpu.update_pc()
        
    def execute_bge(self, cpu, inst):
        _, rs1, rs2 = uppack_inst(inst)
        sign = (inst >> 31) & 0x1
        imm = to_signed(sign << 12 | ((inst >> 7) & 0x1E) | ((inst >> 20) & 0x7e0) | ((inst << 4) & 0x800), 13)
        logging.debug("BGE: x{} = x{}? pc = {:#010x} + {:#010x}".format(rs1, rs2, cpu.pc, imm))
        if cpu.regs[rs1] >= cpu.regs[rs2]:
            return cpu.pc + imm
        else:
            return cpu.update_pc()
        
    def execute_bltu(self, cpu, inst):
        _, rs1, rs2 = uppack_inst(inst)
        sign = (inst >> 31) & 0x1
        imm = to_signed(sign << 12 | ((inst >> 7) & 0x1E) | ((inst >> 20) & 0x7e0) | ((inst << 4) & 0x800), 13)
        logging.debug("BLTU: x{} = x{}? pc = {:#010x} + {:#010x}".format(rs1, rs2, cpu.pc, imm))
        if (cpu.regs[rs1] & 0xFFFFFFFF) < (cpu.regs[rs2] & 0xFFFFFFFF):
            return cpu.pc + imm
        else:
            return cpu.update_pc()
        
    def execute_bgeu(self, cpu, inst):
        _, rs1, rs2 = uppack_inst(inst)
        sign = (inst >> 31) & 0x1
        imm = to_signed(sign << 12 | ((inst >> 7) & 0x1E) | ((inst >> 20) & 0x7e0) | ((inst << 4) & 0x800), 13)
        logging.debug("BGEU: x{} = x{}? pc = {:#010x} + {:#010x}".format(rs1, rs2, cpu.pc, imm))
        if (cpu.regs[rs1] & 0xFFFFFFFF) >= (cpu.regs[rs2] & 0xFFFFFFFF):
            return cpu.pc + imm
        else:
            return cpu.update_pc()

    def execute_fence(self, cpu, inst):
        logging.debug("FENCE")
        return cpu.update_pc()

    def execute_fence_vma(self, cpu, inst):
        logging.debug("FENCE.VMA")
        return cpu.update_pc()

    def execute_sret(self, cpu, inst):
        logging.debug("SRET")
        sstatus = cpu.csr.load(SSTATUS)
        cpu.privilegeLevel = PrivilegeLevel((sstatus & MASK_SPP) >> 8) # set privilege level to spp
        spie = (sstatus & MASK_SPIE) >> 5 # get spie
        sstatus = (sstatus & ~MASK_SIE) | (spie << 1) # set spie to spp
        sstatus = sstatus | MASK_SPIE # set spie to 1
        sstatus = sstatus & ~MASK_SPP # set spp to 0
        cpu.csr.store(SSTATUS, sstatus)
        mepc = cpu.csr.load(SEPC) & ~0b11
        cpu.pc = mepc # set pc to mepc
        return mepc

    def execute_mret(self, cpu, inst):
        logging.debug("MRET")
        mstatus = cpu.csr.load(MSTATUS)
        cpu.privilegeLevel = PrivilegeLevel((mstatus & MASK_MPP) >> 11)
        mpie = (mstatus & MASK_MPIE) >> 7
        mstatus = (mstatus & ~MASK_MIE) | (mpie << 3)
        mstatus = mstatus | MASK_MPIE
        mstatus = mstatus & ~MASK_MPP # set mpp to 0
        if (mstatus & MASK_MPP) != PrivilegeLevel.MACHINE.value: # if mpp is not 0b11, set mprv to 1
            mstatus = mstatus & ~MASK_MPRV # clear mprv if not machine mode
        cpu.csr.store(MSTATUS, mstatus)
        mepc = cpu.csr.load(MEPC) & ~0b11
        cpu.pc = mepc
        return mepc

    def execute_sfence_vma(self, cpu, inst):
        logging.debug("SFENCE.VMA")
        return cpu.update_pc()

    def execute_lb(self, cpu, inst):
        rd, rs1, _ = uppack_inst(inst)
        imm = get_imm(inst)
        logging.debug("LB: x{} = mem[x{} + {:#010x}]".format(rd, rs1, imm))
        cpu.regs[rd] = to_signed(cpu.load(cpu.regs[rs1] + imm, 8), 8)
        return cpu.update_pc()
    
    def execute_lh(self, cpu, inst):
        rd, rs1, _ = uppack_inst(inst)
        imm = get_imm(inst)
        logging.debug("LH: x{} = mem[x{} + {:#010x}]".format(rd, rs1, imm))
        cpu.regs[rd] = to_signed(cpu.load(cpu.regs[rs1] + imm, 16), 16)
        return cpu.update_pc()
    
    def execute_lw(self, cpu, inst):
        rd, rs1, _ = uppack_inst(inst)
        imm = get_imm(inst)
        logging.debug("LW: x{} = mem[x{} + {:#010x}]".format(rd, rs1, imm))
        cpu.regs[rd] = to_signed(cpu.load(cpu.regs[rs1] + imm, 32), 32)
        return cpu.update_pc()
    

    def execute_lbu(self, cpu, inst):
        rd, rs1, _ = uppack_inst(inst)
        imm = get_imm(inst)
        logging.debug("LBU: x{} = mem[x{} + {:#010x}]".format(rd, rs1, imm))
        cpu.regs[rd] = cpu.load(cpu.regs[rs1] + imm, 8)
        return cpu.update_pc()
    
    def execute_lhu(self, cpu, inst):
        rd, rs1, _ = uppack_inst(inst)
        imm = get_imm(inst)
        logging.debug("LHU: x{} = mem[x{} + {:#010x}]".format(rd, rs1, imm))
        cpu.regs[rd] = cpu.load(cpu.regs[rs1] + imm, 16)
        return cpu.update_pc()

    def execute_sb(self, cpu, inst):
        _, rs1, rs2 = uppack_inst(inst)
        imm = to_signed(((inst >> 7) & 0x1F) | ((inst >> 20) & 0xfe0), 12)
        logging.debug("SB: mem[x{} + {:#010x}] = x{}".format(rs1, imm, rs2))
        cpu.store(cpu.regs[rs1] + imm, cpu.regs[rs2] & 0xFF, 8)
        return cpu.update_pc()
    
    def execute_sh(self, cpu, inst):
        _, rs1, rs2 = uppack_inst(inst)
        imm = to_signed(((inst >> 7) & 0x1F) | ((inst >> 20) & 0xfe0), 12)
        logging.debug("SH: mem[x{} + {:#010x}] = x{}".format(rs1, imm, rs2))
        cpu.store(cpu.regs[rs1] + imm, cpu.regs[rs2] & 0xFFFF, 16)
        return cpu.update_pc()
    
    def execute_sw(self, cpu, inst):
        _, rs1, rs2 = uppack_inst(inst)
        imm = to_signed(((inst >> 7) & 0x1F) | ((inst >> 20) & 0xfe0), 12)
        logging.debug("SW: mem[x{} + {:#010x}] = x{}".format(rs1, imm, rs2))
        cpu.store(cpu.regs[rs1] + imm, cpu.regs[rs2] & 0xFFFFFFFF, 32)
        return cpu.update_pc()
    
    def execute_addi(self, cpu, inst):
        rd, rs1, _ = uppack_inst(inst)
        imm = get_imm(inst)
        logging.debug("ADDI: x{} = x{} + {:#010x}".format(rd, rs1, imm))
        cpu.regs[rd] = cpu.regs[rs1] + imm
        return cpu.update_pc()
    
    def execute_slli(self, cpu, inst):
        rd, rs1, _ = uppack_inst(inst)
        shamt = (inst >> 20) & 0x1F
        logging.debug("SLLI: x{} = x{} << {:#010x}".format(rd, rs1, shamt))
        cpu.regs[rd] = cpu.regs[rs1] << shamt
        return cpu.update_pc()
    
    def execute_slti(self, cpu, inst):
        rd, rs1, _ = uppack_inst(inst)
        imm = get_imm(inst)
        logging.debug("SLTI: x{} = x{} < {:#010x}".format(rd, rs1, imm))
        cpu.regs[rd] = 1 if cpu.regs[rs1] < imm else 0
        return cpu.update_pc()  
    
    def execute_sltiu(self, cpu, inst):
        rd, rs1, _ = uppack_inst(inst)
        imm = get_imm(inst, signed=False)
        unsigned_rs1 = cpu.regs[rs1] & 0xFFFFFFFF
        logging.debug("SLTIU: x{} = x{} < {:#010x}".format(rd, rs1, imm))
        cpu.regs[rd] = 1 if unsigned_rs1 < imm else 0
        return cpu.update_pc()  
    
    def execute_xori(self, cpu, inst):
        rd, rs1, _ = uppack_inst(inst)
        imm = get_imm(inst)
        logging.debug("XORI: x{} = x{} ^ {:#010x}".format(rd, rs1, imm))
        cpu.regs[rd] = cpu.regs[rs1] ^ imm
        return cpu.update_pc()
    
    def execute_ori(self, cpu, inst):
        rd, rs1, _ = uppack_inst(inst)
        imm = get_imm(inst)
        logging.debug("ORI: x{} = x{} | {:#010x}".format(rd, rs1, imm))
        cpu.regs[rd] = cpu.regs[rs1] | imm
        return cpu.update_pc()

    def execute_andi(self, cpu, inst):
        rd, rs1, _ = uppack_inst(inst)
        imm = get_imm(inst)
        logging.debug("ANDI: x{} = x{} & {:#010x}".format(rd, rs1, imm))
        cpu.regs[rd] = cpu.regs[rs1] & imm
        return cpu.update_pc()

    def execute_srli(self, cpu, inst):
        rd, rs1, _ = uppack_inst(inst)
        shamt = (inst >> 20) & 0x1F
        logging.debug("SRLI: x{} = x{} >> {:#010x}".format(rd, rs1, shamt))
        cpu.regs[rd] = cpu.regs[rs1] >> shamt & (0xFFFFFFFF >> shamt)
        return cpu.update_pc()

    def execute_srai(self, cpu, inst):
        rd, rs1, _ = uppack_inst(inst)
        shamt = (inst >> 20) & 0x1F
        logging.debug("SRAI: x{} = x{} >> {:#010x}".format(rd, rs1, shamt))
        cpu.regs[rd] = cpu.regs[rs1] >> shamt
        return cpu.update_pc()

    def execute_add(self, cpu, inst):
        rd, rs1, rs2 = uppack_inst(inst)
        logging.debug("ADD: x{} = x{} + x{}".format(rd, rs1, rs2))
        cpu.regs[rd] = cpu.regs[rs1] + cpu.regs[rs2]
        return cpu.update_pc()
    
    def execute_sub(self, cpu, inst):
        rd, rs1, rs2 = uppack_inst(inst)
        logging.debug("SUB: x{} = x{} - x{}".format(rd, rs1, rs2))
        cpu.regs[rd] = cpu.regs[rs1] - cpu.regs[rs2]
        return cpu.update_pc()
    
    def execute_sll(self, cpu, inst):
        rd, rs1, rs2 = uppack_inst(inst)
        logging.debug("SLL: x{} = x{} << x{}".format(rd, rs1, rs2))
        cpu.regs[rd] = cpu.regs[rs1] << cpu.regs[rs2]
        return cpu.update_pc()
    
    def execute_slt(self, cpu, inst):
        rd, rs1, rs2 = uppack_inst(inst)
        logging.debug("SLT: x{} = x{} < x{}".format(rd, rs1, rs2))
        cpu.regs[rd] = 1 if cpu.regs[rs1] < cpu.regs[rs2] else 0
        return cpu.update_pc()
    
    def execute_sltu(self, cpu, inst):
        rd, rs1, rs2 = uppack_inst(inst)
        logging.debug("SLTU: x{} = x{} < x{}".format(rd, rs1, rs2))
        unsigned_rs1 = cpu.regs[rs1] & 0xFFFFFFFF
        unsigned_rs2 = cpu.regs[rs2] & 0xFFFFFFFF
        cpu.regs[rd] = 1 if unsigned_rs1 < unsigned_rs2 else 0
        return cpu.update_pc()
    
    def execute_xor(self, cpu, inst):
        rd, rs1, rs2 = uppack_inst(inst)
        logging.debug("XOR: x{} = x{} ^ x{}".format(rd, rs1, rs2))
        cpu.regs[rd] = cpu.regs[rs1] ^ cpu.regs[rs2]
        return cpu.update_pc()
    
    def execute_srl(self, cpu, inst):
        rd, rs1, rs2 = uppack_inst(inst)
        logging.debug("SRL: x{} = x{} >> x{}".format(rd, rs1, rs2))
        cpu.regs[rd] = (cpu.regs[rs1] & 0xFFFFFFFF) >> cpu.regs[rs2]
        return cpu.update_pc()
    
    def execute_sra(self, cpu, inst):
        rd, rs1, rs2 = uppack_inst(inst)
        logging.debug("SRA: x{} = x{} >> x{}".format(rd, rs1, rs2))
        cpu.regs[rd] = cpu.regs[rs1] >> cpu.regs[rs2]
        return cpu.update_pc()
    
    def execute_or(self, cpu, inst):
        rd, rs1, rs2 = uppack_inst(inst)
        logging.debug("OR: x{} = x{} | x{}".format(rd, rs1, rs2))
        cpu.regs[rd] = cpu.regs[rs1] | cpu.regs[rs2]
        return cpu.update_pc()
    
    def execute_and(self, cpu, inst):
        rd, rs1, rs2 = uppack_inst(inst)
        logging.debug("AND: x{} = x{} & x{}".format(rd, rs1, rs2))
        cpu.regs[rd] = cpu.regs[rs1] & cpu.regs[rs2]
        return cpu.update_pc()

    def execute_mul(self, cpu, inst):
        rd, rs1, rs2 = uppack_inst(inst)
        logging.debug("MUL: x{} = x{} * x{}".format(rd, rs1, rs2))
        cpu.regs[rd] = to_signed((cpu.regs[rs1] * cpu.regs[rs2]) & 0xFFFFFFFF, 32)
        return cpu.update_pc()

    def execute_mulh(self, cpu, inst):
        rd, rs1, rs2 = uppack_inst(inst)
        logging.debug("MULH: x{} = x{} * x{}".format(rd, rs1, rs2))
        cpu.regs[rd] = (cpu.regs[rs1] * cpu.regs[rs2]) >> 32
        return cpu.update_pc()

    def execute_mulhsu(self, cpu, inst):
        rd, rs1, rs2 = uppack_inst(inst)
        logging.debug("MULHSU: x{} = x{} * x{}".format(rd, rs1, rs2))
        cpu.regs[rd] = (cpu.regs[rs1] * (cpu.regs[rs2] & 0xFFFFFFFF)) >> 32
        return cpu.update_pc()

    def execute_mulhu(self, cpu, inst):
        rd, rs1, rs2 = uppack_inst(inst)
        logging.debug("MULHU: x{} = x{} * x{}".format(rd, rs1, rs2))
        cpu.regs[rd] = ((cpu.regs[rs1] & 0xFFFFFFFF) * (cpu.regs[rs2] & 0xFFFFFFFF)) >> 32
        return cpu.update_pc()

    def execute_div(self, cpu, inst):
        rd, rs1, rs2 = uppack_inst(inst)
        logging.debug("DIV: x{} = x{} / x{}".format(rd, rs1, rs2))
        if rs2 == 0:
            raise ZeroDivisionError("division by zero")
        else:
            cpu.regs[rd] = cpu.regs[rs1] // cpu.regs[rs2]
        return cpu.update_pc()

    def execute_divu(self, cpu, inst):
        rd, rs1, rs2 = uppack_inst(inst)
        logging.debug("DIVU: x{} = x{} / x{}".format(rd, rs1, rs2))
        if rs2 == 0:
            raise ZeroDivisionError("division by zero")
        else:
            cpu.regs[rd] = (cpu.regs[rs1] & 0xFFFFFFFF) // (cpu.regs[rs2] & 0xFFFFFFFF)
        return cpu.update_pc()

    def execute_rem(self, cpu, inst):
        rd, rs1, rs2 = uppack_inst(inst)
        logging.debug("REM: x{} = x{} % x{}".format(rd, rs1, rs2))
        if rs2 == 0:
            raise ZeroDivisionError("division by zero")
        else:
            cpu.regs[rd] = cpu.regs[rs1] % cpu.regs[rs2]
        return cpu.update_pc()

    def execute_remu(self, cpu, inst):
        rd, rs1, rs2 = uppack_inst(inst)
        logging.debug("REMU: x{} = x{} % x{}".format(rd, rs1, rs2))
        if rs2 == 0:
            raise ZeroDivisionError("division by zero")
        else:
            cpu.regs[rd] = (cpu.regs[rs1] & 0xFFFFFFFF) % (cpu.regs[rs2] & 0xFFFFFFFF)
        return cpu.update_pc()

    def execute_csrrw(self, cpu, inst):
        rd, rs1, _ = uppack_inst(inst)
        csr_addr = get_imm(inst, signed=False)
        logging.debug("CSRRW: x{} = CSR[{:#010x}], x{}".format(rd, csr_addr, rs1))
        t = cpu.csr.load(csr_addr)
        cpu.csr.store(csr_addr, (cpu.regs[rs1] & 0xFFFFFFFF))
        cpu.regs[rd] = to_signed(t, 32)
        return cpu.update_pc()

    def execute_csrrs(self, cpu, inst):
        rd, rs1, _ = uppack_inst(inst)
        csr_addr = get_imm(inst, signed=False)
        logging.debug("CSRRS: x{} = CSR[{:#010x}], x{}".format(rd, csr_addr, rs1))
        t = cpu.csr.load(csr_addr)
        cpu.csr.store(csr_addr, t | (cpu.regs[rs1] & 0xFFFFFFFF))
        cpu.regs[rd] = to_signed(t, 32)
        return cpu.update_pc()
    
    def execute_csrrc(self, cpu, inst):
        rd, rs1, _ = uppack_inst(inst)
        csr_addr = get_imm(inst, signed=False)
        logging.debug("CSRRC: x{} = CSR[{:#010x}], x{}".format(rd, csr_addr, rs1))
        t = cpu.csr.load(csr_addr)
        cpu.csr.store(csr_addr, t & (~(cpu.regs[rs1] & 0xFFFFFFFF)))
        cpu.regs[rd] = to_signed(t, 32)
        return cpu.update_pc()
    
    def execute_csrrwi(self, cpu, inst):
        rd, imm, _ = uppack_inst(inst)
        csr_addr = get_imm(inst, signed=False)
        logging.debug("CSRRWI: x{} = CSR[{:#010x}], {:#010x}".format(rd, csr_addr, imm))
        t = cpu.csr.load(csr_addr)
        cpu.csr.store(csr_addr, (imm & 0xFFFFFFFF))
        cpu.regs[rd] = to_signed(t, 32)
        return cpu.update_pc()
    
    def execute_csrrsi(self, cpu, inst):
        rd, imm, _ = uppack_inst(inst)
        csr_addr = get_imm(inst, signed=False)
        logging.debug("CSRRSI: x{} = CSR[{:#010x}], {:#010x}".format(rd, csr_addr, imm))
        t = cpu.csr.load(csr_addr)
        cpu.csr.store(csr_addr, t | (imm & 0xFFFFFFFF))
        cpu.regs[rd] = to_signed(t, 32)
        return cpu.update_pc()
    
    def execute_csrrci(self, cpu, inst):
        rd, imm, _ = uppack_inst(inst)
        csr_addr = get_imm(inst, signed=False)
        logging.debug("CSRRCI: x{} = CSR[{:#010x}], {:#010x}".format(rd, csr_addr, imm))
        t = cpu.csr.load(csr_addr)
        cpu.csr.store(csr_addr, t & (~(imm & 0xFFFFFFFF)))
        cpu.regs[rd] = to_signed(t, 32)
        return cpu.update_pc()

    def execute(self, cpu, inst):
        op = inst & 0x7F
        funct3 = (inst >> 12) & 0x7
        funct7 = (inst >> 25) & 0x7F
        cpu.regs[0] = 0  # set x0 to 0
        logging.debug("Executing instruction: {:#010x}, funct3: {:#04x}".format(inst, funct3))
        instruction_map = {
            0x37: self.excute_lui,          # U-type
            0x17: self.execute_auipc,       # U-type
            0x6F: self.execute_jal,         # J-type
            0x67: self.execute_jalr,        # I-type
            0x63:{
                0x0: self.execute_beq,
                0x1: self.execute_bne,
                0x4: self.execute_blt,
                0x5: self.execute_bge,
                0x6: self.execute_bltu,
                0x7: self.execute_bgeu,
            },
            0x03:{
                0x0: self.execute_lb,
                0x1: self.execute_lh,
                0x2: self.execute_lw,
                0x4: self.execute_lbu,
                0x5: self.execute_lhu,
            },
            0x23:{
                0x0: self.execute_sb,
                0x1: self.execute_sh,
                0x2: self.execute_sw,
            },
            0x13:{
                0x00: self.execute_addi,
                0x01: self.execute_slli,
                0x02: self.execute_slti,
                0x03: self.execute_sltiu,
                0x04: self.execute_xori,
                0x05: {
                    0x00: self.execute_srli,
                    0x20: self.execute_srai,
                },
                0x06: self.execute_ori,
                0x07: self.execute_andi,
            },
            0x33:{ # opcode 0x33
                0x00:{  # funct3 0x00
                    0x00: self.execute_add, # funct7 0x00 ADD
                    0x01: self.execute_mul, # funct7 0x01 MUL
                    0x20: self.execute_sub, # funct7 0x20 SUB
                },
                0x01:{ # funct3 0x01
                    0x00:self.execute_sll, # funct7 0x00 SLL
                    0x01:self.execute_mulh, # funct7 0x01 MULH
                }, 
                0x02:{# funct3 0x02
                    0x00: self.execute_slt,  # funct7 0x00 SLT
                    0x01: self.execute_mulhsu,  # funct7 0x01 MULHSU
                },
                0x03:{# funct3 0x03
                    0x00: self.execute_sltu,  # funct7 0x00 SLTU
                    0x01: self.execute_mulhu,  # funct7 0x01 MULHU
                },
                0x04:{# funct3 0x04
                    0x00: self.execute_xor,  # funct7 0x00 XOR
                    0x01: self.execute_div,  # funct7 0x01 DIV
                },
                0x05:{
                    0x00: self.execute_srl, # funct7 0x00 SRL
                    0x01: self.execute_divu, # funct7 0x01 DIVU
                    0x20: self.execute_sra, # funct7 0x20 SRA
                },
                0x06:{# funct3 0x06
                    0x00: self.execute_or,  # funct7 0x00 OR
                    0x01: self.execute_rem,  # funct7 0x01 REM
                },
                0x07:{# funct3 0x07
                    0x00: self.execute_and,  # funct7 0x00 AND
                    0x01: self.execute_remu,  # funct7 0x01 REMU
                }
            },
            0x0f:{
                0x0: self.execute_fence
            },
            0x73:{ # opcode 0x73
                0x1: self.execute_csrrw,
                0x2: self.execute_csrrs,
                0x3: self.execute_csrrc,
                0x5: self.execute_csrrwi,
                0x6: self.execute_csrrsi,
                0x7: self.execute_csrrci,
                0x0:{  # funct3 0x0
                    0x08: self.execute_sret,  # funct7 0x08 SRET
                    0x18: self.execute_mret,  # funct7 0x18 MRET
                    # 0x20: self.execute_wfi,  # funct7 0x20 WFI
                    0x09: self.execute_sfence_vma,  # funct7 0x09 SFENCE.VMA
                }
            }
        }
        exe = instruction_map.get(op, None)
        if exe is None:
            raise Exception("Invalid opcode: {:#010x}".format(op))
        if isinstance(exe, dict):
            exe = exe.get(funct3, None)
            if exe is None:
                raise Exception("Invalid funct3: {:#04x}".format(funct3))
            if isinstance(exe, dict):
                exe = exe.get(funct7, None)
                if exe is None:
                    raise Exception("Invalid funct7: {:#07x}".format(funct7))

        return exe(cpu, inst)