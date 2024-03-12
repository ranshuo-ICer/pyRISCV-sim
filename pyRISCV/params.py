# Dram parameters
DRAM_BASE = 0x80000000  # Base address of DRAM
DRAM_SIZE = 1024 * 1024 * 1  # 128MB
DRAM_END = DRAM_BASE + DRAM_SIZE - 1  # End address of DRAM

# Machine CSR parameters
NUM_CSRS = 4096  # Number of CSRs
# Machine Information Registers (M-mode CSRs)
MHARTID = 0xF14  # MHARTID register value

# Machine trap setup CSRs
MSTATUS = 0x300  # Machine status register
MEDELEG = 0x302  # Machine exception delegation register
MIDELEG = 0x303  # Machine interrupt delegation register
MIE = 0x304  # Machine interrupt-enable register
MTVEC = 0x305  # Machine trap-handler base address register
MCOUNTEREN = 0x306  # Machine counter enable register

# Machine trap handling CSRs
MSCRATCH = 0x340  # Scratch register for machine trap handlers
MEPC = 0x341  # Machine exception program counter register
MCAUSE = 0x342  # Machine trap cause register
MTVAL = 0x343  # Machine bad address or instruction
MIP = 0x344  # Machine interrupt pending register

# Supervisor CSR parameters
SSTATUS = 0x100  # Supervisor status register
SIE = 0x104  # Supervisor interrupt-enable register
STVEC = 0x105  # Supervisor trap-handler base address register
SCOUNTEREN = 0x106  # Supervisor counter enable register                
SSCRATCH = 0x140  # Scratch register for supervisor trap handlers
SEPC = 0x141  # Supervisor exception program counter register
SCAUSE = 0x142  # Supervisor trap cause register
STVAL = 0x143  # Supervisor bad address or instruction
SIP = 0x144  # Supervisor interrupt pending register
SATP = 0x180  # Supervisor address translation and protection register

# Masks for MSTATUS fields
MASK_SIE = 1 << 1  # 监管中断使能掩码
MASK_MIE = 1 << 3  # 机器中断使能掩码
MASK_SPIE = 1 << 5  # 上一次监管中断使能掩码
MASK_UBE = 1 << 6  # 用户模式字节顺序掩码
MASK_MPIE = 1 << 7  # 上一次机器中断使能掩码
MASK_SPP = 1 << 8  # 上一次监管权限模式掩码
MASK_VS = 0b11 << 9  # 虚拟化状态掩码
MASK_MPP = 0b11 << 11  # 上一次机器权限模式掩码
MASK_FS = 0b11 << 13  # 浮点单元状态掩码
MASK_XS = 0b11 << 15  # 用户扩展状态掩码
MASK_MPRV = 1 << 17  # 内存保护寄存器掩码
MASK_SUM = 1 << 18  # 监管用户内存访问掩码
MASK_MXR = 1 << 19  # 内存扩展寄存器掩码
MASK_TVM = 1 << 20  # 虚拟化内存掩码
MASK_TW = 1 << 21  # 虚拟化等待掩码
MASK_TSR = 1 << 22  # 虚拟化SR掩码
MASK_SSTATUS = MASK_SIE | MASK_SPIE | MASK_UBE | MASK_SPP | MASK_FS \
                                | MASK_XS  | MASK_SUM  | MASK_MXR  # 监管状态寄存器掩码

MASK_SSIP = 1 << 1  # 监管软件中断挂起掩码
MASK_MSIP = 1 << 3  # 机器软件中断挂起掩码
MASK_STIP = 1 << 5  # 监管定时器中断挂起掩码
MASK_MTIP = 1 << 7  # 机器定时器中断挂起掩码
MASK_SEIP = 1 << 9  # 监管外部中断挂起掩码
MASK_MEIP = 1 << 11  # 机器外部中断挂起掩码