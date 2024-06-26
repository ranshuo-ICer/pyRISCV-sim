import subprocess
import os
import logging
from pyRISCV import CPU
from pyRISCV.rv_exception import RVException, ExceptionType

def generate_rv_assembly(c_src):
    commands = f"cd tmp && riscv64-unknown-elf-gcc -S {c_src} -o"
    process = subprocess.Popen(commands, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode!= 0:
        raise Exception(f"Failed to generate RV assembly. Command: {commands} -> \n{stderr.decode()}")

def generate_rv_obj(assembly):
    base_name = os.path.basename(assembly).split('.')[0]
    commands = f"cd tmp && riscv64-unknown-elf-gcc -Wl,-Ttext=0x80000000 -march=rv32im -mabi=ilp32 -nostdlib -o {base_name} {assembly}"
    process = subprocess.Popen(commands, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode!= 0:
        raise Exception(f"Failed to generate RV object. Command: {commands} -> \n{stderr.decode()}")

def generate_rv_biniary(obj):
    commands = f"cd tmp && riscv64-unknown-elf-objcopy -O binary {obj} {obj}.bin"
    process = subprocess.Popen(commands, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode!= 0:
        raise Exception(f"Failed to generate RV binary. Command: {commands} -> \n{stderr.decode()}")

def rv_helper(code, test_name, n_clocks=1000000):
    file_name = f"{test_name}.s"
    with open("./tmp/"+file_name, 'w') as f:
        f.write(code)
    generate_rv_obj(file_name)
    generate_rv_biniary(test_name)
    cpu = CPU(open(f"./tmp/{test_name}.bin", 'rb').read())
    for i in range(n_clocks):
        try:
            inst = cpu.fetch()
            new_pc = cpu.execute(inst)
            if new_pc is None:
                break
            cpu.pc = new_pc
        except RVException as e:
            print(f"Exception: {e}")
            if e.get_type() in [ExceptionType.INSTRUCTION_ACCESS_FAULT,
                                 ExceptionType.ILLEGAL_INSTRUCTION,]:
                logging.warning(f"Illegal instruction at PC: {hex(cpu.pc)}, exiting simulation")
                break
            cpu.handle_exception(e)
    return cpu