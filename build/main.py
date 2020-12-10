#!/usr/bin/env python3

import sys
import argparse
from GodotBuilder import GodotBuilder

################################################################################
### Functions ##################################################################
################################################################################

def parse_args():
    parser = argparse.ArgumentParser(description='Builds Godot Editor and Export Templates')

    parser.add_argument('-update', help='Update Godot repositories', action='store_true')
    parser.add_argument('-editor', help='Build Godot Editor for current platform', action='store_true')
    parser.add_argument('-export', help='Build export templates for all supported platforms', action='store_true')
    parser.add_argument('-mono', help='Include C# support', action='store_true')

    return parser.parse_args(sys.argv[1:])

################################################################################
### MAIN #######################################################################
################################################################################

if __name__ == '__main__':
    GodotBuilder().run(parse_args())
