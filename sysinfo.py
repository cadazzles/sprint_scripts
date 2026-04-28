#!/usr/bin/python3

# Gathers information about a Windows/macOS/Linux system, including hostname, OS info, CPU, memory usage, disk usage, IP address, MAC address, and uptime.
# Information is outputted to either the terminal (stdout), a CSV file, or a JSON file, based on a command-line argument taken when invoked. Works as a module
# or as a standalone utility.
#
# Licensed under the MIT License (https://opensource.org/license/mit)
# AlecWandy-20260427: Initial version

# Imports
import sys

# Constants
DEFAULT_OUTPUT_FILE = "sysinfo"

def main():
    """ Primary script entry point - handles parsed cmd arguments and passes them to information gathering functions before outputting """
    check_basic_compat()
    output_mode, output_file = parse_args()

def check_basic_compat():
    """ Basic script compatibility check. If the host system is not one of the supported three, immediately quit with an error. """
    if not sys.platform in ["win32", "darwin", "linux"]:
        print(f'ERROR: platform {sys.platform} is not supported by sysinfo. Please run this script from a Windows, macOS, or Linux system.')
        sys.exit(1)

def parse_args():
    """ Exception handling for command-line arguments """
    try:
        # Attempt to discern output mode from first supplied argument - IndexError is handled if no arg is provided
        output_mode = sys.argv[1].lower()
    except IndexError:
        # Exit with error code 1 and print help message if no args are provided
        print("Usage: python3 sysinfo.py <screen | csv | json> <optional: output_file>")
        sys.exit(1)
    
    # Validate that supplied output mode is a valid option
    if not output_mode in ["screen", "csv", "json"]:
        print("ERROR: Invalid output mode. Valid options: screen, csv, json")
        sys.exit(1)

    # If no output filename/path is provided, use the default name in current working dir
    output_file = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUTPUT_FILE

    # Make sure the output file ends with the appropriate extension based on the output mode, add it if not present
    if output_mode == "csv":
        if not output_file.endswith(".csv"):
            output_file = output_file + ".csv"
    elif output_mode == "json":
        if not output_file.endswith(".json"):
            output_file = output_file + ".json"

    return output_mode, output_file




# Run main() if called directly from cmd, otherwise function as an importable library
if __name__ == '__main__':
    main()