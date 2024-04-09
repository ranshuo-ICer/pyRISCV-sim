import sys
sys.path.append("..")
import os
import logging
import pytest
from utils import rv_helper
from pyRISCV import params


logging.basicConfig(level=logging.DEBUG)

def setup_module():
    if not os.path.exists("tmp"):
        os.mkdir("tmp")

def teardown_module():
    if os.path.exists("tmp"):
        os.system("rm -rf tmp/*")  # remove tmp directory and all its contents    

def setup_function(function):
    print("----------------------------")
    print(f"Running {function.__name__}")

def teardown_function(function):
    print(f"Finished {function.__name__}")
    print("")


def test_addi():
    code = """
.global _start
_start:
    addi x31, x0, 10  # 将 10 加载到 x31 中
"""
    cpu = rv_helper(code, "test_addi", 1)
    assert cpu.regs[31] == 10, "test_addi failed"

def test_slli():
    code = """
.global _start
_start:
    addi x1, x0, 10  # 将 1 加载到 x2 中
    slli x2, x1, 2  # 将 x1 左移 2 位，结果放入 x2 中
"""
    cpu = rv_helper(code, "test_slli", 2)
    assert cpu.regs[2] == 10<<2, "test_slli failed"

def test_slti():
    code = """
.global _start
_start:
    addi x1, x0, -3  # 将 -3 加载到 x1 中
    slti x2, x1, 8  # x2 = (x1 < 8) ? 1 : 0
    slti x3, x1, 0  # x3 = (x1 < 0) ? 1 : 0
    slti x4, x1, -10 # x4 = (x1 < -10)? 1 : 0
"""
    cpu = rv_helper(code, "test_slti", 4)
    assert cpu.regs[2] == 1, "test_slti failed"
    assert cpu.regs[3] == 1, "test_slti failed"
    assert cpu.regs[4] == 0, "test_slti failed"

def test_sltiu():
    code = """
.global _start
_start:
    addi x1, x0, 10  # 将 10 加载到 x1 中
    sltiu x2, x1, 10  # x2 = (x1 < 10) ? 1 : 0
    sltiu x3, x1, 11  # x3 = (x1 < 11) ? 1 : 0
    sltiu x4, x1, 0   # x4 = (x1 < 0)  ? 1 : 0
"""
    cpu = rv_helper(code, "test_sltiu", 3)
    assert cpu.regs[2] == 0, "test_sltiu failed"
    assert cpu.regs[3] == 1, "test_sltiu failed"
    assert cpu.regs[4] == 0, "test_sltiu failed"

def test_xori():
    code = """
.global _start
_start:
    addi x1, x0, 10  # 将 10 加载到 x1 中
    xori x2, x1, 5  # x2 = x1 ^ 5
    xori x3, x1, -5 # x3 = x1 ^ -5
"""
    cpu = rv_helper(code, "test_xori", 3)
    assert cpu.regs[2] == 15, "test_xori failed"
    assert cpu.regs[3] == -15, "test_xori failed"

def test_srli():
    code = """
.global _start
_start:
    addi x1, x0, 10  # 将 10 加载到 x1 中
    srli x2, x1, 2  # 将 x1 右移 2 位，结果放入 x2 中
    addi x1, x0, -10  # 将 -10 加载到 x1 中
    srli x3, x1, 2  # 将 x1 右移 2 位，结果放入 x3 中
"""
    cpu = rv_helper(code, "test_srli", 4)
    assert cpu.regs[2] == 10>>2, "test_srli failed"
    assert cpu.regs[3] == 1073741821, "test_srli failed"

def test_srai():
    code = """
.global _start
_start:
    addi x1, x0, 10  # 将 10 加载到 x1 中
    srai x2, x1, 2  # 将 x1 右移 2 位，结果放入 x2 中
    addi x1, x0, -10  # 将 -10 加载到 x1 中
    srai x3, x1, 2  # 将 x1 右移 2 位，结果放入 x3 中
"""
    cpu = rv_helper(code, "test_srai", 4)
    assert cpu.regs[2] == 10>>2, "test_srai failed"
    assert cpu.regs[3] == -10>>2, "test_srai failed"

def test_andi():
    code = """
.global _start
_start:
    addi x1, x0, 11  # 将 10 加载到 x1 中
    andi x2, x1, 5  # x2 = x1 & 5
    andi x3, x1, -5 # x3 = x1 & -5
"""
    cpu = rv_helper(code, "test_andi", 3)
    assert cpu.regs[2] == 1, "test_andi failed"
    assert cpu.regs[3] == 11, "test_andi failed"

def test_lui():
    code = """
.global _start
_start:
    lui x1, 524288  # 将 0x1234 加载到 x1 中
    lui x2, 0x5678  # 将 0x5678 加载到 x2 中
"""
    cpu = rv_helper(code, "test_lui", 2)
    assert cpu.regs[1] == -2147483648, "test_lui failed"
    assert cpu.regs[2] == 0x05678000, "test_lui failed"

def test_auipc():
    code = """
.global _start
_start:
    auipc x1, 524288  # 将 524288 加载到 x1 中
    auipc x2, 0x5678  # 将 0x56780000 加载到 x2 中
"""
    cpu = rv_helper(code, "test_auipc", 2)
    assert cpu.regs[1] == params.DRAM_BASE + -2147483648, "test_auipc failed"
    assert cpu.regs[2] == params.DRAM_BASE + 0x05678000 + 4, "test_auipc failed"

def test_jal():
    code = """
.global _start
_start:
    jal x1, _func  # 跳转到 _func 处执行
    addi x2, x0, 1  # 这条指令不会被执行
    addi x3, x0, 2  # 这条指令不会被执行
_func:
    addi x2, x0, 3  # 这条指令会被执行
    addi x3, x0, 4  # 这条指令会被执行
    jal x4, 0x1200
"""
    cpu = rv_helper(code, "test_jal", 4)
    assert cpu.regs[1] == params.DRAM_BASE + 4, "test_jal failed"
    assert cpu.regs[2] == 3, "test_jal failed"
    assert cpu.regs[3] == 4, "test_jal failed"
    assert cpu.regs[4] == params.DRAM_BASE + 5*4 + 4, "test_jal failed"
    assert cpu.pc == params.DRAM_BASE + 0x1200, "test_jal failed"

def test_jalr():
    code = """
.global _start
_start:
    addi x1, x0, 16  # 将 16 加载到 x1 中
    addi x3, x0, 2  # 这条指令会被执行
    jalr x2, -4(x1)  # 跳转到 x1 处偏移 -4 的位置执行
    addi x3, x0, 1  # 这条指令不会被执行
"""
    cpu = rv_helper(code, "test_jalr", 3)
    assert cpu.regs[1] == 16, "test_jalr failed"
    assert cpu.regs[2] == params.DRAM_BASE + 12, "test_jalr failed"
    assert cpu.regs[3] == 2, "test_jalr failed"
    assert cpu.pc == 16 - 4, "test_jalr failed"

def test_fence():
    code = """
.global _start
_start:
    addi x1, x0, 1  # 这条指令会被执行
    fence  # 这条指令会被执行
    addi x1, x0, 2  # 这条指令会被执行
"""
    cpu = rv_helper(code, "test_fence", 2)
    assert cpu.regs[1] == 1, "test_fence failed"
    assert cpu.pc == params.DRAM_BASE + 4 + 4, "test_fence failed"

def test_sb_lb():
    code = """
.global _start
_start:
    addi x1, x0, 16  # 将 16 加载到 x1 中
    sb x1, 0(x2)  # 将 x1 存入 x2 处偏移 0 处
    lb x3, 0(x2)  # 从 x2 处偏移 0 处读取一个字节，结果放入 x3 中
    addi x1, x0, -19  # 将 -19 加载到 x1 中
    sb x1, -16(x2)  # 将 x1 存入 x2 处偏移 -16 处
    lb x4, -16(x2)  # 从 x2 处偏移 -16 处读取一个字节，结果放入 x4 中
"""
    cpu = rv_helper(code, "test_sb", 6)
    assert cpu.regs[1] == -19, "test_sb failed"
    assert cpu.regs[3] == 16, "test_sb failed"
    assert cpu.regs[4] == -19, "test_sb failed"

def test_sh_lh():
    code = """
.global _start
_start:    
    addi x1, x0, 16  # 将 16 加载到 x1 中
    sh x1, -16(x2)  # 将 x1 存入 x2 处偏移 0 处
    lh x3, -16(x2)  # 从 x2 处偏移 0 处读取两个字节，结果放入 x3 中
    addi x1, x0, -19  # 将 -19 加载到 x1 中
    sh x1, -32(x2)  # 将 x1 存入 x2 处偏移 -16 处
    lh x4, -32(x2)  # 从 x2 处偏移 -16 处读取两个字节，结果放入 x4 中
"""
    cpu = rv_helper(code, "test_sh", 6)
    assert cpu.regs[1] == -19, "test_sh failed"
    assert cpu.regs[3] == 16, "test_sh failed"
    assert cpu.regs[4] == -19, "test_sh failed"

def test_sw_lw():
    code = """
.global _start
_start:
    addi x1, x0, 16  # 将 16 加载到 x1 中
    sw x1, -32(x2)  # 将 x1 存入 x2 处偏移 0 处
    lw x3, -32(x2)  # 从 x2 处偏移 0 处读取四个字节，结果放入 x3 中
    addi x1, x0, -19  # 将 -19 加载到 x1 中
    sw x1, -64(x2)  # 将 x1 存入 x2 处偏移 -16 处
    lw x4, -64(x2)  # 从 x2 处偏移 -16 处读取四个字节，结果放入 x4 中
"""
    cpu = rv_helper(code, "test_sw", 6)
    assert cpu.regs[1] == -19, "test_sw failed"
    assert cpu.regs[3] == 16, "test_sw failed"
    assert cpu.regs[4] == -19, "test_sw failed"

def test_beq():
    code = """
.global _start
_start:
    addi x1, x0, 10  # 将 10 加载到 x1 中    
    addi x2, x0, 10  # 将 20 加载到 x2 中
    beq x1, x2, _end  # 跳转到 _end 处执行
    addi x3, x0, 1  # 这条指令会被执行
    j _end2  # 跳转到 _end2 处执行
_end:
    addi x3, x0, 2  # 这条指令会被执行
    addi x4, x0, 3  # 这条指令会被执行
_end2:
    addi x0, x0, 0  # 这条指令会被执行
"""
    cpu = rv_helper(code, "test_beq", 6)
    assert cpu.regs[3] == 2, "test_beq failed"
    assert cpu.regs[4] == 3, "test_beq failed"

def test_bne():
    code = """
.global _start
_start:    
    addi x1, x0, 10  # 将 10 加载到 x1 中
    addi x2, x0, 20  # 将 20 加载到 x2 中
    bne x1, x2, _end  # 跳转到 _end 处执行
    addi x3, x0, 1  # 这条指令不会被执行
    addi x4, x0, 2  # 这条指令不会被执行
    j _end2  # 跳转到 _end2 处执行
_end:
    addi x3, x0, 2  # 这条指令会被执行
    addi x4, x0, 3  # 这条指令会被执行
_end2:
    addi x0, x0, 0  # 这条指令会被执行
"""
    cpu = rv_helper(code, "test_bne", 6)
    assert cpu.regs[3] == 2, "test_bne failed"
    assert cpu.regs[4] == 3, "test_bne failed"

def test_blt():
    code = """
.global _start
_start:
    addi x1, x0, -29  # 将 10 加载到 x1 中
    addi x2, x0, 20  # 将 20 加载到 x2 中
    blt x1, x2, _end  # 跳转到 _end 处执行
    addi x3, x0, 1  # 这条指令不会被执行
    addi x4, x0, 2  # 这条指令不会被执行
    j _end2  # 跳转到 _end2 处执行
_end:
    addi x3, x0, 2  # 这条指令会被执行
    addi x4, x0, 3  # 这条指令会被执行
_end2:
    addi x0, x0, 0  # 这条指令会被执行
"""
    cpu = rv_helper(code, "test_blt", 6)
    assert cpu.regs[3] == 2, "test_blt failed"
    assert cpu.regs[4] == 3, "test_blt failed"


def test_bge():
    code = """
.global _start
_start:
    addi x1, x0, 9  # 将 10 加载到 x1 中
    addi x2, x0, 10  # 将 10 加载到 x2 中
    bge x1, x2, _end  # 跳转到 _end 处执行
    addi x3, x0, 1  # 这条指令不会被执行
    addi x4, x0, 2  # 这条指令不会被执行
    j _end2  # 跳转到 _end2 处执行
_end:
    addi x3, x0, 2  # 这条指令会被执行
    addi x4, x0, 3  # 这条指令会被执行
_end2:    
    addi x0, x0, 0  # 这条指令会被执行
"""
    cpu = rv_helper(code, "test_bge", 6)
    assert cpu.regs[3] == 1, "test_bge failed"
    assert cpu.regs[4] == 2, "test_bge failed"

def test_add():
    code = """
.global _start
_start:
    addi x1, x0, -10  # 将 10 加载到 x1 中
    addi x2, x0, 20  # 将 20 加载到 x2 中
    add x3, x1, x2  # x3 = x1 + x2
    addi x4, x0, 30  # 将 30 加载到 x4 中
    add x5, x3, x4  # x5 = x3 + x4
    addi x6, x0, 40  # 将 40 加载到 x6 中
    add x7, x5, x6  # x7 = x5 + x6
"""
    cpu = rv_helper(code, "test_add", 7)
    assert cpu.regs[3] == 10, "test_add failed"
    assert cpu.regs[5] == 40, "test_add failed"
    assert cpu.regs[7] == 80, "test_add failed"

def test_sub():
    code = """
.global _start
_start:
    addi x1, x0, 10  # 将 10 加载到 x1 中
    addi x2, x0, 20  # 将 20 加载到 x2 中
    sub x3, x1, x2  # x3 = x1 - x2
    addi x4, x0, 30  # 将 30 加载到 x4 中
    sub x5, x3, x4  # x5 = x3 - x4
    addi x6, x0, 40  # 将 40 加载到 x6 中
    sub x7, x5, x6  # x7 = x5 - x6
"""
    cpu = rv_helper(code, "test_sub", 7)
    assert cpu.regs[3] == -10, "test_sub failed"
    assert cpu.regs[5] == -40, "test_sub failed"
    assert cpu.regs[7] == -80, "test_sub failed"

def test_sll():
    code = """
.global _start
_start:
    addi x1, x0, 10  # 将 10 加载到 x1 中
    addi x2, x0, 2  # 将 2 加载到 x2 中
    sll x4, x1, x2  # x2 = x1 << 2
    addi x3, x0, 30  # 将 30 加载到 x3 中
    sll x5, x3, x2  # x4 = x3 << 2
"""
    cpu = rv_helper(code, "test_sll", 5)
    assert cpu.regs[4] == 40, "test_sll failed"
    assert cpu.regs[5] == 120, "test_sll failed"

def test_slt():
    code = """
.global _start
_start:
    addi x1, x0, 10  # 将 10 加载到 x1 中
    addi x2, x0, 20  # 将 20 加载到 x2 中
    slt x3, x1, x2  # x3 = (x1 < x2)
    addi x4, x0, 30  # 将 30 加载到 x4 中
    slt x5, x4, x1  # x5 = (x4 < x1)
"""
    cpu = rv_helper(code, "test_slt", 5)
    assert cpu.regs[3] == 1, "test_slt failed"
    assert cpu.regs[5] == 0, "test_slt failed"

def test_sltu():
    code = """
.global _start
_start:
    addi x1, x0, -10  # 将 10 加载到 x1 中
    addi x2, x0, 20  # 将 20 加载到 x2 中
    sltu x3, x1, x2  # x3 = (x1 < x2)
    addi x4, x0, 30  # 将 30 加载到 x4 中
    sltu x5, x4, x1  # x5 = (x4 < x1)
"""
    cpu = rv_helper(code, "test_sltu", 5)
    assert cpu.regs[3] == 0, "test_sltu failed"
    assert cpu.regs[5] == 1, "test_sltu failed"

def test_xor():
    code = """
.global _start
_start:
    addi x1, x0, 0b11111111  # 将 255 加载到 x1 中
    addi x2, x0, 0b10101010  # 将 170 加载到 x2 中
    xor x3, x1, x2  # x3 = x1 ^ x2
    addi x4, x0, 0b01010101  # 将 85 加载到 x4 中
    xor x5, x3, x4  # x5 = x3 ^ x4
"""
    cpu = rv_helper(code, "test_xor", 5)
    assert cpu.regs[3] == 255 ^ 170, "test_xor failed"
    assert cpu.regs[5] == 255 ^ 170 ^ 85, "test_xor failed"

def test_srl():
    code = """
.global _start
_start:
    addi x1, x0, 10  # 将 10 加载到 x1 中
    addi x2, x0, 2  # 将 2 加载到 x2 中
    srl x4, x1, x2  # x2 = x1 >> 2
    addi x3, x0, 30  # 将 30 加载到 x3 中
    addi x2, x0, 3  # 将 3 加载到 x2 中
    srl x5, x3, x2  # x4 = x3 >> 3
"""
    cpu = rv_helper(code, "test_srl", 6)
    assert cpu.regs[4] == 10 >> 2, "test_srl failed"
    assert cpu.regs[5] == 30 >> 3, "test_srl failed"

def test_sra():
    code = """
.global _start
_start:
    addi x1, x0, -10  # 将 -10 加载到 x1 中
    addi x2, x0, 2  # 将 2 加载到 x2 中
    sra x4, x1, x2  # x2 = x1 >> 2
    addi x3, x0, -30  # 将 -30 加载到 x3 中
    addi x2, x0, 3  # 将 3 加载到 x2 中
    sra x5, x3, x2  # x4 = x3 >> 3
"""
    cpu = rv_helper(code, "test_sra", 6)
    assert cpu.regs[4] == -10 >> 2, "test_sra failed"
    assert cpu.regs[5] == -30 >> 3, "test_sra failed"

def test_or():
    code = """
.global _start
_start:
    addi x1, x0, 0b11111111  # 将 255 加载到 x1 中
    addi x2, x0, 0b10101010  # 将 170 加载到 x2 中
    or x3, x1, x2  # x3 = x1 | x2
    addi x4, x0, 0b01010101  # 将 85 加载到 x4 中
    or x5, x3, x4  # x5 = x3 | x4
"""
    cpu = rv_helper(code, "test_or", 5)
    assert cpu.regs[3] == 255 | 170, "test_or failed"
    assert cpu.regs[5] == 255 | 170 | 85, "test_or failed"

def test_and():
    code = """
.global _start
_start:
    addi x1, x0, 0b11111111  # 将 255 加载到 x1 中
    addi x2, x0, 0b10101010  # 将 170 加载到 x2 中
    and x3, x1, x2  # x3 = x1 & x2
    addi x4, x0, 0b01010101  # 将 85 加载到 x4 中
    and x5, x3, x4  # x5 = x3 & x4
"""
    cpu = rv_helper(code, "test_and", 5)
    assert cpu.regs[3] == 255 & 170, "test_and failed"
    assert cpu.regs[5] == 255 & 170 & 85, "test_and failed"

def test_csrrw():
    code = """
.global _start
_start:
    li x1, 10  # 将 10 加载到 x1 中
    csrrw x2, mstatus, x1  # 将 mstatus 寄存器的值写入 x2
"""
    cpu = rv_helper(code, "test_csrrw", 2)
    assert cpu.regs[2] == 0, "test_csrrw failed"
    assert cpu.csr.load(params.MSTATUS) == 10, "test_csrrw failed"

    code = """
.global _start
_start:
    li x2, -5
    li x3, 10
    csrrw x1, mstatus, x2  # 将 5 写入 mstatus 寄存器
    csrrw x4, mstatus, x3  # 将 10 写入 mstatus 寄存器
"""
    cpu = rv_helper(code, "test_csrrw", 4)
    assert cpu.regs[1] == 0, "test_csrrw failed"
    assert cpu.regs[4] == -5, "test_csrrw failed"
    assert cpu.csr.load(params.MSTATUS) == 10, "test_csrrw failed"

def test_csrrs():
    code = """
.global _start
_start:
    li x2, 5  # 将 10 加载到 x1 中
    csrrs x1, mstatus, x2  # 将 mstatus 寄存器的值写入 x1
    li x3, 10
    csrrs x4, mstatus, x3  # 将 10 写入 mstatus 寄存器
"""
    cpu = rv_helper(code, "test_csrrs", 4)
    assert cpu.regs[1] == 0, "test_csrrs failed"
    assert cpu.regs[4] == 5, "test_csrrs failed"
    assert cpu.csr.load(params.MSTATUS) == 10|5, "test_csrrs failed"

def test_csrrc():
    code = """
.global _start
_start:
    li x2, 5  # 将 10 加载到 x1 中
    csrrc x1, mstatus, x2  # 将 mstatus 寄存器的值写入 x1
    li x3, 10
    csrrc x4, mstatus, x3  # 将 10 写入 mstatus 寄存器
"""
    cpu = rv_helper(code, "test_csrrc", 4)
    assert cpu.regs[1] == 0, "test_csrrc failed"
    assert cpu.regs[4] == 0, "test_csrrc failed"
    assert cpu.csr.load(params.MSTATUS) == 0, "test_csrrc failed"

def test_csrrwi():
    code = """
.global _start
_start:
    csrrwi x1, mstatus, 10  # 将 mstatus 寄存器的值写入 x1
"""
    cpu = rv_helper(code, "test_csrrwi", 1)
    assert cpu.regs[1] == 0, "test_csrrwi failed"
    assert cpu.csr.load(params.MSTATUS) == 10, "test_csrrwi failed"

def test_csrrsi():
    code = """
.global _start
_start:
    li x2, 5  # 5 加载到 x2 中
    csrrsi x1, mstatus, 10  # 将 mstatus 寄存器的值写入 x1
    li x3, 10
    csrrsi x4, mstatus, 5  # 将 10 写入 mstatus 寄存器
"""
    cpu = rv_helper(code, "test_csrrsi", 4)
    assert cpu.regs[1] == 0, "test_csrrsi failed"
    assert cpu.regs[4] == 10, "test_csrrsi failed"
    assert cpu.csr.load(params.MSTATUS) == 10|5, "test_csrrsi failed"

def test_csrrci():
    code = """
.global _start
_start:
    li x2, 5  # 将 10 加载到 x1 中
    csrrci x1, mstatus, 10  # 将 mstatus 寄存器的值写入 x1
    li x3, 10
    csrrci x4, mstatus, 5  # 将 10 写入 mstatus 寄存器
"""
    cpu = rv_helper(code, "test_csrrci", 4)
    assert cpu.regs[1] == 0, "test_csrrci failed"
    assert cpu.regs[4] == 0, "test_csrrci failed"
    assert cpu.csr.load(params.MSTATUS) == 0, "test_csrrci failed"

def test_csr():
    code = """
.global _start
_start:
    addi t0, zero, 1
    addi t1, zero, 2
    addi t2, zero, 3
    csrrw zero, mstatus, t0
    csrrs zero, mtvec, t1
    csrrw zero, mepc, t2
    csrrc t2, mepc, zero
    csrrwi zero, sstatus, 4
    csrrsi zero, stvec, 5
    csrrwi zero, sepc, 6
    csrrci zero, sepc, 0
"""
    cpu = rv_helper(code, "test_csr", len(code.split('\n'))-4)
    assert cpu.csr.load(params.MSTATUS) == 1, "test_csr failed"
    assert cpu.csr.load(params.MTVEC) == 2, "test_csr failed"
    assert cpu.csr.load(params.MEPC) == 3, "test_csr failed"
    assert cpu.csr.load(params.SSTATUS) == 0, "test_csr failed"
    assert cpu.csr.load(params.STVEC) == 5, "test_csr failed"
    assert cpu.csr.load(params.SEPC) == 6, "test_csr failed"

def test_mul():
    code = """
.global _start
_start:
    addi x1, x0, 10  # 将 10 加载到 x1 中
    addi x2, x0, 2  # 将 2 加载到 x2 中
    mul x3, x1, x2  # x3 = x1 * x2
    addi x4, x0, -30  # 将 -30 加载到 x4 中
    addi x2, x0, 3  # 将 3 加载到 x2 中
    mul x5, x4, x2  # x5 = x4 * x2
"""
    cpu = rv_helper(code, "test_mul", 6)
    assert cpu.regs[3] == 10 * 2, "test_mul failed"
    assert cpu.regs[5] == -30 * 3, "test_mul failed"

def test_mulh():
    code = """
.global _start
_start:
    li x1, 0x12345678  # 将 0x12345678 加载到 x1 中
    li x2, 0x87654321  # 将 0x87654321 加载到 x2 中
    mulh x3, x1, x2  # x3 = (x1 * x2) >> 32
    mulh x5, x1, x2  # x5 = (x1 * x2) >> 32
"""
    cpu = rv_helper(code, "test_mulh", 6)
    assert cpu.regs[3] == (0x12345678 * -2023406815) >> 32, "test_mulh failed"
    assert cpu.regs[5] == (0x12345678 * -2023406815) >> 32, "test_mulh failed"

def test_mulhsu():
    code = """
.global _start
_start:
    li x1, 0x12345678  # 将 0x12345678 加载到 x1 中
    li x2, 0x87654321  # 将 0x87654321 加载到 x2 中
    mulhsu x3, x1, x2  # x3 = (x1 * x2) >> 32
    mulhsu x5, x1, x2  # x5 = (x1 * x2) >> 32
"""
    cpu = rv_helper(code, "test_mulhsu", 6)
    assert cpu.regs[3] == (0x12345678 * 0x87654321) >> 32, "test_mulhsu failed"
    assert cpu.regs[5] == (0x12345678 * 0x87654321) >> 32, "test_mulhsu failed"

def test_sret():
    code = """
.global _start
_start:
    addi x2, x0, 8  # 将 8 加载到 x2 中
    csrrw x1, sepc, x2  # 将 8 写入 spec 寄存器
    sret
"""
    cpu = rv_helper(code, "test_sret", 3)
    assert cpu.csr.load(params.SEPC) == 8, "test_sret failed"
    assert cpu.csr.load(params.MSTATUS) & (1 << 1) == 0, "test_sret failed"

if __name__ == '__main__':
    print("Testing RV32I instructions...")
    print(__file__)
    pytest.main(['-s', __file__])

    # setup_module()
    # test_jalr()
    # teardown_module()