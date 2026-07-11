###############################################################################
## Program  : print_functions.py
##
## Purpose  : Functions to assist printing
##
## Requires : pprint - to print a beautified representation of an object
##
## Author   : Ken Rosenberry <ken.rosenberry@gmail.com>
##
## Revised  : 2026-04-23 Initial Version
###############################################################################

import pprint

LINE_SEP = '-' * 133

pp = pprint.PrettyPrinter(width=233, indent=2)

def my_pretty_print(data):
    """
    Pretty print with a separator line.
    """
    print(f"\n{LINE_SEP}")
    pp.pprint(data)
    print(f"{LINE_SEP}")


def print_with_separator_line(data):
    """
    Print with a separator line before.
    """
    print(f"\n{LINE_SEP}")
    print(data)
    # print(f"{LINE_SEP}")


