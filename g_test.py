from pyRISCV import CPU
from pyRISCV import DRAM_BASE
import os
import logging
import pytest

logging.basicConfig(level=logging.DEBUG)

def setup_module():
    if not os.path.exists("tmp"):
        os.mkdir("tmp")

def teardown_module():
    if os.path.exists("tmp"):
        os.system("rm -rf tmp/*")  # remove tmp directory and all its contents    

def generate_rv_assembly(c_src):
    commands = f"cd tmp && riscv64-unknown-elf-gcc -S {c_src} -o"
    result = os.system(commands)
    if result!= 0:
        raise Exception(f"Failed to generate RV assembly. Command: {commands}")

def generate_rv_obj(assembly):
    base_name = os.path.basename(assembly).split('.')[0]
    commands = f"cd tmp && riscv64-unknown-elf-gcc -Wl,-Ttext=0x0 -march=rv32i -mabi=ilp32 -nostdlib -o {base_name} {assembly}"
    result = os.system(commands)
    if result!= 0:
        raise Exception(f"Failed to generate RV object. Command: {commands}")

def generate_rv_biniary(obj):
    commands = f"cd tmp && riscv64-unknown-elf-objcopy -O binary {obj} {obj}.bin"
    result = os.system(commands)
    if result!= 0:
        raise Exception(f"Failed to generate RV binary. Command: {commands}")

def rv_helper(code, test_name, n_clocks):
    file_name = f"{test_name}.s"
    with open("./tmp/"+file_name, 'w') as f:
        f.write(code)
    generate_rv_obj(file_name)
    generate_rv_biniary(test_name)
    cpu = CPU(open(f"./tmp/{test_name}.bin", 'rb').read())
    for i in range(n_clocks):
        inst = cpu.fetch()
        new_pc = cpu.execute(inst)
        if new_pc is None:
            break
        cpu.pc = new_pc
    return cpu


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

def test_add():
    code = """
.global _start
_start:
    addi x2, x0, -10  # 将 -10 加载到 x2 中
    addi x3, x0, 20  # 将 20 加载到 x3 中
    add x1, x2, x3   # x1 = x2 + x3
"""
    cpu = rv_helper(code, "test_add", 3)
    assert cpu.regs[1] == 10, "test_add failed"

def test_ori():
    code = """
.global _start
_start:
    addi x1, x0, 10  # 将 10 加载到 x1 中
    ori x2, x1, 5  # x2 = x1 | 5
    ori x3, x1, -5 # x3 = x1 | -5
"""
    cpu = rv_helper(code, "test_ori", 3)
    assert cpu.regs[2] == 15, "test_ori failed"
    assert cpu.regs[3] == -5, "test_ori failed"

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
    assert cpu.regs[1] == DRAM_BASE + -2147483648, "test_auipc failed"
    assert cpu.regs[2] == DRAM_BASE + 0x05678000 + 4, "test_auipc failed"

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
    assert cpu.regs[1] == DRAM_BASE + 4, "test_jal failed"
    assert cpu.regs[2] == 3, "test_jal failed"
    assert cpu.regs[3] == 4, "test_jal failed"
    assert cpu.regs[4] == DRAM_BASE + 5*4 + 4, "test_jal failed"
    assert cpu.pc == DRAM_BASE + 0x1200, "test_jal failed"

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
    assert cpu.regs[2] == DRAM_BASE + 12, "test_jalr failed"
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
    assert cpu.pc == DRAM_BASE + 4 + 4, "test_fence failed"

def test_lb():
    code = """
.global _start
_start:
    addi x1, x0, 16  # 将 16 加载到 x1 中
    addi x2, x0, 1  # 将 1 加载到 x2 中
    lb x3, 0(x1)  # 从 x1 处偏移 0 处读取一个字节，结果放入 x3 中
    lb x4, 1(x1)  # 从 x1 处偏移 1 处读取一个字节，结果放入 x4 中
"""
    cpu = rv_helper(code, "test_lb", 4)
    assert cpu.regs[1] == 16, "test_lb failed"
    assert cpu.regs[2] == 1, "test_lb failed"
    assert cpu.regs[3] == 0, "test_lb failed"
    assert cpu.regs[4] == 1, "test_lb failed"

if __name__ == '__main__':
    print("Testing RV32I instructions...")
    print(__file__)
    pytest.main(['-s', __file__])

    # setup_module()
    # test_jalr()
    # teardown_module()