import enum

class ExceptionType(enum.Enum):
    INSTRUCTION_ADDRESS_MISALIGNED = 0
    INSTRUCTION_ACCESS_FAULT = 1
    ILLEGAL_INSTRUCTION = 2
    BREAKPOINT = 3
    LOAD_ADDRESS_MISALIGNED = 4
    LOAD_ACCESS_FAULT = 5
    STORE_AMO_ADDRESS_MISALIGNED = 6
    STORE_AMO_ACCESS_FAULT = 7
    ECALL_FROM_U = 8
    ECALL_FROM_S = 9
    ECALL_FROM_M = 11
    INSTRUCTION_PAGE_FAULT = 12
    LOAD_PAGE_FAULT = 13
    STORE_AMO_PAGE_FAULT = 15

class RVException(Exception):
    def __init__(self, e_type: ExceptionType, e_value):
        super().__init__()
        self.e_type = e_type
        self.e_value = e_value

    def get_type(self):
        return self.e_type

    def get_value(self):
        return self.e_value

    def is_fatal(self):
        if self.e_type in [ExceptionType.ILLEGAL_INSTRUCTION, 
                           ExceptionType.INSTRUCTION_ACCESS_FAULT, 
                           ExceptionType.LOAD_ADDRESS_MISALIGNED, 
                           ExceptionType.LOAD_ACCESS_FAULT, 
                           ExceptionType.STORE_AMO_ADDRESS_MISALIGNED,
                           ExceptionType.STORE_AMO_ACCESS_FAULT]:
            return True
        else:
            return False

    def __str__(self):
        return f"RVException: {ExceptionType(self.e_type).name} - {self.e_value}"