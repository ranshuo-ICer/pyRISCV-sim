from pyRISCV.rv_exception import RVException, ExceptionType

import os
def setup_module():
    if not os.path.exists("tmp"):
        os.mkdir("tmp")

def teardown_module():
    if os.path.exists("tmp"):
        os.system("rm -rf tmp/*")  

def test_exception():
    try:
        raise RVException(ExceptionType.ILLEGAL_INSTRUCTION, 0x12345678)
    except RVException as e:
        print(e)
        assert e.get_type() == ExceptionType.ILLEGAL_INSTRUCTION
        assert e.get_value() == 0x12345678