import sys
sys.path.append('../')
import logging
from utils import rv_helper
import pytest

def test_load_access_fault():
    logging.info("Testing load access fault")
    code = """
.globl start
start:
    # delegete exception to supervisor mode
    addi t0, zero, 1<<5 # cause load access fault
    csrrs a0, medeleg, t0 # set medeleg with load access fault
    # switch to user mode
    lui t0, %hi(usr_mode) # load user mode code address
    addi t0, t0, %lo(usr_mode)
    csrrw t0, mepc, t0 # set mepc with user mode code address
    mret # return from exception

# user mode code
usr_mode:
    addi x1, x0, 0 # load x1 with 0
    lw x2, 0(x1) # load x2 with 0
"""
    cpu = rv_helper(code, "test_load_access_fault", 8)

if __name__ == '__main__':
    pytest.main(['-v', __file__, '--log-cli-level', 'DEBUG', 
                 '--log-cli-format', '%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s'])