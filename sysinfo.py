#!/usr/bin/python3

# Gathers information about a Windows/macOS/Linux system, including hostname, OS info, CPU, memory usage, disk usage, IP address, MAC address, and uptime.
# Information is outputted to either the terminal (stdout), a CSV file, or a JSON file, based on a command-line argument taken when invoked. Works as a module
# or as a standalone utility.
#
# Licensed under the MIT License (https://opensource.org/license/mit)
# AlecWandy-20260427: Initial version

def main():
    """Primary script entry point - handles parsed cmd arguments and passes them to information gathering functions before outputting """

# Run main() if called directly from cmd, otherwise function as an importable library
if __name__ == '__main__':
    main()