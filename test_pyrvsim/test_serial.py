from utils import rv_helper
from pyRISCV import params 
import logging

logging.basicConfig(level=logging.INFO)
logging.disable(logging.CRITICAL)

import os
def setup_module():
    if not os.path.exists("tmp"):
        os.mkdir("tmp")

def teardown_module():
    if os.path.exists("tmp"):
        os.system("rm -rf tmp/*")  

def test_serial():
    code = f"""
.global _start
_start:
    li x1, {params.SERIAL_BASE}
    li x3, {ord('H')}
    sb x3, 0(x1)
    li x3, {ord('e')}
    sb x3, 0(x1)
    li x3, {ord('l')}
    sb x3, 0(x1)
    li x3, {ord('l')}
    sb x3, 0(x1)
    li x3, {ord('o')}
    sb x3, 0(x1)
    li x3, {ord(' ')}
    sb x3, 0(x1)
    li x3, {ord('W')}
    sb x3, 0(x1)
    li x3, {ord('o')}
    sb x3, 0(x1)
    li x3, {ord('r')}
    sb x3, 0(x1)
    li x3, {ord('l')}
    sb x3, 0(x1)
    li x3, {ord('d')}
    sb x3, 0(x1)
    li x3, {ord('!')}
    sb x3, 0(x1)
    li x3, {ord('\n')}
    sb x3, 0(x1)
    li x3, {ord('S')}
    sb x3, 0(x1)
    li x3, {ord('i')}
    sb x3, 0(x1)
    li x3, {ord('m')}
    sb x3, 0(x1)
    li x3, {ord('u')}
    sb x3, 0(x1)
    li x3, {ord('l')}
    sb x3, 0(x1)
    li x3, {ord('a')}
    sb x3, 0(x1)
    li x3, {ord('t')}
    sb x3, 0(x1)
    li x3, {ord('i')}
    sb x3, 0(x1)
    li x3, {ord('o')}
    sb x3, 0(x1)
    li x3, {ord('n')}
    sb x3, 0(x1)
    li x3, {ord('!')}
    sb x3, 0(x1)
    li x3, {ord('\n')}
    sb x3, 0(x1)
    j loop
loop:
    j loop
"""
    cpu = rv_helper(code, "test_serial", n_clocks=len(code.split("\n")))



if __name__ == '__main__':
    test_serial()