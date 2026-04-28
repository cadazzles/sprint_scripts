#!/usr/bin/python3

# Gathers information about a Windows/macOS/Linux system, including hostname, OS info, CPU, memory usage, disk usage, IP address, MAC address, and uptime.
# Information is outputted to either the terminal (stdout), a CSV file, or a JSON file, based on a command-line argument taken when invoked. Works as a module
# or as a standalone utility.
#
# Licensed under the MIT License (https://opensource.org/license/mit)
# AlecWandy-20260427: Initial version

# Imports
import sys
import subprocess
import platform
import distro
import psutil

# Constants
DEFAULT_OUTPUT_FILE = "sysinfo"
CLIENT_PLATFORM = sys.platform

def main():
    """ Primary script entry point - handles parsed cmd arguments and passes them to information gathering functions before outputting """
    check_basic_compat()
    output_mode, output_file = parse_args()
    hostname = get_hostname()
    os_info = get_os_info()
    cpu_info = get_cpu_info()
    mem_info = get_mem_info()

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
            # Retrieves the following information for Windows-based systems
            # Windows name (i.e. Windows), marketing version (i.e "11"), feature edition (i.e. Professional), build version (i.e. 26200), and OS architecture (i.e. AMD64)
            os_info.extend([platform.system(), platform.release(), platform.win32_edition(), platform.version(), platform.machine()])
        if CLIENT_PLATFORM == "darwin":
            # Retrieves the following information for macOS-based systems
            # macOS, macOS version (i.e. "26.4.1"), Darwin version (i.e. "25.4"), OS architecture (i.e. arm64)
            os_info.extend(["macOS", platform.mac_ver()[0], platform.version(), platform.machine()])
        if CLIENT_PLATFORM == "linux":
            # Retrieves the following information for Linux-based systems
            # Distribution name (i.e. Ubuntu Server), Distribution version (i.e. 24.04.1 Noble Numbat), Linux kernel version (i.e. 6.6.89-ubuntu-1-1), OS architecture (i.e. AMD64)
            os_info.extend([distro.name(pretty=True), distro.version(pretty=True, best=True), platform.version(), platform.machine()])
    except Exception as e:
        # Exit w/ error if we run into any snags (most of the time, this process should succeed)
        print(f'ERROR: Critical error occurred while attempting to gather OS information: {e}')
        print("Exiting...")
        sys.exit(1)
    return os_info

def get_cpu_info():
    # Generate list for CPU information
    # Format: [pretty_model, physical_cores, logical_cores, usage_percent]
    cpu_info = []
    try:
        # Get CPU model name (i.e. AMD Ryzen 7 5800X3D 8-Core Processor, Apple M2, etc.)
        if CLIENT_PLATFORM == "win32":
            cpu_info.append(subprocess.check_output("wmic cpu get name", shell=True).decode().strip().split('\n')[1].strip())
        elif CLIENT_PLATFORM == "linux":
            cpu_info.append(subprocess.check_output("lscpu | grep 'Model name'", shell=True).decode().split(':')[1].strip())
        elif CLIENT_PLATFORM == "darwin":
            cpu_info.append(subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"]).decode().strip())
        
        # Get amount of physical cores, logical cores, and system-wide CPU usage (as a percentage over a .5 second interval)
        cpu_info.extend([psutil.cpu_count(logical=False), psutil.cpu_count(), psutil.cpu_percent(interval=0.5)]) 
    except Exception as e:
        print(f'ERROR: Critical error occurred while attempting to obtain CPU information: {e}')
        print("Exiting...")
        sys.exit(1)
    
    return cpu_info

def get_mem_info():
    # Generate list for Memory information
    # Format: [avail_vmem, total_vmem, percent_util]
    mem_info = []
    try:
        # Get available virtual memory, total virtual memory, and percentage utilization
        mem_info.extend([psutil.virtual_memory().available, psutil.virtual_memory().total, psutil.virtual_memory().percent])
    except Exception as e:
        print(f'ERROR: Critical error occurred while attempting to obtain memory information: {e}')
        print("Exiting...")
        sys.exit(1)
    
    return mem_info
    

# Run main() if called directly from cmd, otherwise function as an importable library
if __name__ == '__main__':
    main()