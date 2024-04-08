from .cpu import CPU
import logging
import cmd
import time

class SDB(cmd.Cmd):
    """
        Simple Debugger
    """

    intro = "Welcome to the Simple Debugger"
    prompt = "sdb> "

    def __init__(self, program):
        super().__init__()
        if type(program) == str:
            print(f"Loading program from file: {program}")
            program = open(program, "rb").read()
        cpu = CPU(program)
        self.cpu = cpu
        self.cmd_dict = {}
        self.watch_points = {}
        self.cmd_dict["help"] = self.do_help
        self.cmd_dict["q"] = self.do_q
        self.cmd_dict["c"] = self.do_c
        self.cmd_dict["si"] = self.do_si
        self.cmd_dict["info"] = self.do_info
        self.cmd_dict["x"] = self.do_x
        self.cmd_dict["w"] = self.do_w
        self.cmd_dict["p"] = self.do_p
        self.cmd_dict["d"] = self.do_d

    def execute_once(self):
        inst = self.cpu.fetch()
        if inst == 0:
            return False
        new_pc = self.cpu.execute(inst)
        self.cpu.pc = new_pc
        return True
    
    def execute(self, n_cycles=1):
        for i in range(n_cycles):
            if not self.execute_once():
                print("Program terminated")
                return
            for address in self.watch_points:
                if self.cpu.load(address, 32)!= self.watch_points[address]:
                    print(f"Watch point triggered at {address:08x}")
                    self.watch_points[address] = self.cpu.load(address, 32)
                    return

    def do_help(self, *args):
        """
            Prints available commands"""
        for cmd in self.cmd_dict:
            print(f"{cmd}: {self.cmd_dict[cmd].__doc__}")

    def do_c(self, *args):
        """
            Continue execution until program terminates"""
        start_time = time.time()
        instructions = 0
        try:
            while self.execute_once():
                instructions += 1
        except KeyboardInterrupt:
            end_time = time.time()
            print("\r--------Execution interrupted---------")
            print(f"Execution time: {end_time - start_time:.2f} seconds")
            print(f"Instructions executed: {instructions}")
            print(f"Performance: {instructions / (end_time - start_time):.2f} instructions/second")

    def do_q(self, *args):
        """
            Quit the debugger"""
        print("Quitting debugger")
        exit()

    def do_si(self, *args):
        """
            Single step execution
            Usage: si [n_cycles]"""
        n_cycles = 1
        args = args[0].strip().split(" ")
        if args[0]:
            try:
                n_cycles = int(args[0])
            except ValueError:
                print("Invalid argument for n_cycles")
                return
        print(f"Single stepping {n_cycles} cycles")
        self.execute(n_cycles)

    def do_info(self, *args):
        """
            Print CPU information
            Usage: info r|w"""
        
        if args[0] == "r":
            self.cpu.dump_regs()
            self.cpu.dump_pc()
        elif args[0] == "w":
            for address in self.watch_points:
                print(f"Watch point at {address:#010x}: {self.watch_points[address]:#010x}")
        else:
            print("Invalid argument for info")

    def do_x(self, *args):
        """
            Print memory contents
            Usage: x [length] [address]"""
        
        length = 1
        address = 0
        args = args[0].strip().split(" ")
        if args[0]:
            try:
                length = int(args[0])
            except ValueError:
                print("Invalid argument for length")
                return
        args = "".join(args[1:]).replace(" ", "")
        if args:
            try:
                address = self.parse_expression(args)
            except ValueError:
                print("Invalid argument for address")
                return
        else:
            print("No address provided for x")
            return
        
        print(f"Printing {length} bytes at address {address:#010x}")
        for i in range(length):
            try:
                print(f"{address+i:#010x}: {self.cpu.load(address+i, 32):#010x}")
            except:
                print(f"{address+i:#010x}: ??????????")

    def do_w(self, *args):
        """
            Set a watch point
            Usage: w [address]"""
        args = args[0]
        if args:
            try:
                args = args.strip().replace(" ", "")
                address = self.parse_expression(args)
            except ValueError:
                print("Invalid argument for address")
                return
            if address in self.watch_points:
                print(f"Watch point already set at {address:#010x}")
            else:
                try:
                    self.watch_points[address] = self.cpu.load(address, 32)
                    print(f"Watch point set at {address:#010x}")
                except:
                    print(f"Invalid address for watch point: {address:#010x}")
        else:
            print("No address provided for watch point")

    def do_p(self, *args):
        """
            Parse and print an expression
            Usage: p [expression]"""
        args = args[0].strip().replace(" ", "")
        if not args:
            print("No expression provided for p")
            return
        try:
            value = self.parse_expression(args)
            print(f"{args} = {value:#010x}")
        except ValueError:
            print(f"Invalid expression: {args}")

    def do_d(self, *args):
        """
            Delete a watch point
            Usage: d N"""
        
        args = args[0].strip().replace(" ", "")
        if not args:
            print("No argument provided for d")
            return
        try:
            index = int(args)
            if index < 0 or index >= len(self.watch_points):
                print(f"Invalid index for watch point: {index}")
                return
            address = list(self.watch_points.keys())[index]
            del self.watch_points[address]
            print(f"Watch point at {address:#010x} deleted")
        except ValueError:
            print(f"Invalid argument for d: {args}")

    def parse_expression(self, expr):
        """
            experssion could be a register name, a constant, or an address
            and add or subtract an offset
        """
        if "+" in expr:
            parts = expr.split("+")
            if len(parts) != 2:
                print(f"Invalid expression: {expr}")
                return None
            base = self.parse_expression(parts[0])
            if base is None:
                return None
            offset = self.parse_expression(parts[1])
            if offset is None:
                return None
            return base + offset
        elif "-" in expr:
            parts = expr.split("-")
            if len(parts) != 2:
                print(f"Invalid expression: {expr}")
                return None
            base = self.parse_expression(parts[0])
            if base is None:
                return None
            offset = self.parse_expression(parts[1])
            if offset is None:
                return None
            return base - offset
        else:
            if expr.startswith("$"):
                expr = expr[1:]
                if expr.startswith("x"):
                    index = int(expr[1:])
                else:
                    index = CPU.RVABI.index(expr)
                return self.cpu.regs[index]
            elif expr.startswith("0x"):
                return eval(expr)
            else:
                return int(expr)

