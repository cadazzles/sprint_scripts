#!/usr/bin/python3

# Gathers information about a Windows/macOS/Linux system, including hostname, OS info, CPU, memory usage, disk usage, IP address, MAC address, and uptime.
# Information is outputted to either the terminal (stdout), a CSV file, or a JSON file, based on a command-line argument taken when invoked. Works as a module
# or as a standalone utility.
#
# Licensed under the MIT License (https://opensource.org/license/mit)
# AlecWandy-20260427: Initial version

# Imports
import sys
import platform
import distro

# Constants
DEFAULT_OUTPUT_FILE = "sysinfo"
CLIENT_PLATFORM = sys.platform

def main():
    """ Primary script entry point - handles parsed cmd arguments and passes them to information gathering functions before outputting """
    check_basic_compat()
    output_mode, output_file = parse_args()
    hostname = get_hostname()
    os_info = get_os_info()

def check_basic_compat():
    """ Basic script compatibility check. If the host system is not one of the supported three, immediately quit with an error. """
    if not CLIENT_PLATFORM in ["win32", "darwin", "linux"]:
        print(f'ERROR: platform {CLIENT_PLATFORM} is not supported by sysinfo. Please run this script from a Windows, macOS, or Linux system.')
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

def get_hostname():
    # Return best-guess for system hostname
    return platform.node()

def get_os_info():
    # Generate list for OS/platform information
    # Format: [os_name, os_version, <win only: windows_release>, kernel_version, os_arch]
    os_info = []
    try:
        # Gather OS information based on current platform (Windows/macOS/Linux)
        if CLIENT_PLATFORM == "win32":
            os_info.append(platform.system()) # Windows name, i.e. "Windows"
            os_info.append(platform.release()) # Windows marketing version, i.e. "11"
            os_info.append(platform.win32_edition()) # Windows feature edition, i.e. "Professional"
            os_info.append(platform.version()) # Windows build version, i.e. "10.0.26200"
            os_info.append(platform.machine()) # OS architecture, i.e. "AMD64"
        if CLIENT_PLATFORM == "darwin":
            os_info.append("macOS") # Use macOS for identifiability instead of Darwin
            os_info.append(platform.mac_ver()[0]) # macOS version, i.e. "26.4.1" - Darwin kernel and macOS versions often don't match
            os_info.append(platform.version()) # Darwin version, i.e. "25.4"
            os_info.append(platform.machine()) # OS architecture, i.e. "arm64"
        if CLIENT_PLATFORM == "linux":
            os_info.append(distro.name(pretty=True)) # Distribution name, i.e. "Ubuntu Server"
            os_info.append(distro.version(pretty=True, best=True)) # Distribution version, i.e. "24.04.1 Noble Numbat"
            os_info.append(platform.version()) # Linux kernel version, i.e. "6.6.89-ubuntu-1-1"
            os_info.append(platform.machine()) # OS architecture, i.e. "AMD64"
    except Exception as e:
        # Exit w/ error if we run into any snags (most of the time, this process should succeed)
        print(f'ERROR: Critical error occurred while attempting to gather OS information: {e}')
        print("Exiting...")
        sys.exit(1)
    return os_info




# Run main() if called directly from cmd, otherwise function as an importable library
if __name__ == '__main__':
    main()