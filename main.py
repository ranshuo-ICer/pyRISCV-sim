import argparse
import logging
from pyRISCV import SDB

argparser = argparse.ArgumentParser(description='RISC-V Simulator')
argparser.add_argument('program', type=str, help='Path to the program to be executed')
argparser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
argparser.add_argument('-d', '--debug', action='store_true', help='Enable debug output')
argparser.add_argument('--log', type=str, help="Path to the log file")
argparser.add_argument("--gdb", type=str, help="Path to the GDB server")

args = argparser.parse_args()

def main(args):
    sdb = SDB(args.program)
    sdb.cmdloop()

if __name__ == '__main__':
    logging_fmt = '%(asctime)s %(levelname)s %(message)s'
    if args.verbose or args.debug:
        logging.disable(logging.NOTSET)
    if args.verbose and not args.debug:
        logging.basicConfig(level=logging.INFO, format=logging_fmt)
    if args.debug:
        logging.basicConfig(level=logging.DEBUG, format=logging_fmt)
    if args.log:
        logging.basicConfig(filename=args.log, level=logging.DEBUG, format=logging_fmt)
    main(args)