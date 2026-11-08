"""Run a command taken directly from command-line input."""

import subprocess
import sys


def main():
    subprocess.run(sys.argv[1:], check=False)


if __name__ == "__main__":
    main()