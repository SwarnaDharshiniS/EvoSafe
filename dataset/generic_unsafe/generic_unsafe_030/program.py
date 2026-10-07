"""Dispatch user text through an aliased system-shell call."""

from os import system as dispatch
import sys


def launch(arguments):
    command_line = " ".join(arguments)
    return dispatch(command_line)


if __name__ == "__main__" and len(sys.argv) > 1:
    launch(sys.argv[1:])