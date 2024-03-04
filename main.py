import sys
import pyRISCV

if __name__ == "__main__":
    argc = len(sys.argv)
    if argc != 2:
        print("Usage: python main.py program.bin")
        exit(0)
    cpu = pyRISCV.CPU(open(sys.argv[1], "rb").read())
    try:
        while True:
            inst = cpu.fetch()
            new_pc = cpu.execute(inst)
            if new_pc is None:
                break
            cpu.pc = new_pc
    except Exception as e:
        print(e)
    cpu.dump_regs()
    cpu.dump_pc()