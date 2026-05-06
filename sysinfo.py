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
import time
from datetime import timedelta
import json
import csv

# Constants
DEFAULT_OUTPUT_FILE = "sysinfo"
CLIENT_PLATFORM = sys.platform
# Define platform-specific constants
if CLIENT_PLATFORM == "win32":
    ROOT_DIR = "C:"
    GET_CPU_MODEL_CMD = "wmic cpu get name"
elif CLIENT_PLATFORM == "linux":
    ROOT_DIR = "/"
    GET_CPU_MODEL_CMD = "lscpu | grep 'Model name'"
elif CLIENT_PLATFORM == "darwin":
    ROOT_DIR = "/System/Volumes/Data"
    GET_CPU_MODEL_CMD = ["sysctl", "-n", "machdep.cpu.brand_string"]


def main():
    """ Primary script entry point - handles parsed cmd arguments and passes them to information gathering functions before outputting """
    check_script_compat()
    output_mode, output_file = parse_args()
    
    # Create a dictionary for storing all retrieved system information
    sysinfo_dict = {}

    get_hostname_uptime(sysinfo_dict)
    get_os_info(sysinfo_dict)
    get_cpu_info(sysinfo_dict)
    get_mem_info(sysinfo_dict)
    get_disk_info(sysinfo_dict)
    print(sysinfo_dict)

    if output_mode == "screen":
        print("stubbed")
    elif output_mode == "json":
        export_to_json(sysinfo_dict, output_file)
    elif output_mode == "csv":
        export_to_csv(sysinfo_dict, output_file)

def check_script_compat():
    """ Basic script compatibility check. If the host system is not one of the supported three, immediately quit with an error. """
    if not CLIENT_PLATFORM in ["win32", "darwin", "linux"]:
        print(f'ERROR: platform {CLIENT_PLATFORM} is not supported by sysinfo. Please run this script from a supported Windows, macOS, or Linux system.')
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

def get_hostname_uptime(sysinfo_dict):
    """ Retrieves hostname and uptime of the client machine in a platform-agnostic way. """
    # Get time of last system boot (seconds since UNIX epoch)
    boot_timestamp = psutil.boot_time()
    # Turn into timestamp, format into human-readable duration (no microseconds)
    uptime_duration = str(timedelta(seconds=time.time() - boot_timestamp)).split('.')[0]
    sysinfo_dict.update({
        'hostname': platform.node(), # Use platform's best guess for system hostname
        'uptime_duration': uptime_duration
    })

def get_os_info(sysinfo_dict):
    """ Retrieves a selection of pertintent OS information, including platform-specific values (i.e. kernel vs. product versions)"""
    try:
        # Gather OS information based on current platform (Windows/macOS/Linux)
        if CLIENT_PLATFORM == "win32":
            # Retrieves the following information for Windows-based systems
            # Windows name (i.e. Windows), marketing version (i.e "11"), feature edition (i.e. Professional), build version (i.e. 26200), and OS architecture (i.e. AMD64)
            sysinfo_dict.update({
                'os_type': platform.system(),
                'os_version': platform.release(),
                'os_edition': platform.win32_edition(),
                'os_kernel_version': platform.version(),
                'os_arch': platform.machine()
            })
        elif CLIENT_PLATFORM == "darwin":
            # Retrieves the following information for macOS-based systems
            # macOS, macOS version (i.e. "26.4.1"), Darwin version (i.e. "25.4"), OS architecture (i.e. arm64)
            sysinfo_dict.update({
                'os_type': 'macOS',
                'os_version': platform.mac_ver()[0],
                'os_edition': '',
                'os_kernel_version': platform.release(),
                'os_arch': platform.machine()
            })
        elif CLIENT_PLATFORM == "linux":
            # Retrieves the following information for Linux-based systems
            # Distribution name (i.e. Ubuntu Server), Distribution version (i.e. 24.04.1 Noble Numbat), Linux kernel version (i.e. 6.6.89-ubuntu-1-1), OS architecture (i.e. AMD64)
            sysinfo_dict.update({
                'os_type': distro.name(pretty=True),
                'os_version': distro.version(pretty=True, best=True),
                'os_edition': '',
                'os_kernel_version': platform.release(),
                'os_arch': platform.machine()
            })
    except Exception as e:
        # Exit w/ error if we run into any snags (most of the time, this process should succeed)
        print(f'ERROR: Critical error occurred while attempting to gather OS information: {e}')
        print("Exiting...")
        sys.exit(1)

def get_cpu_info(sysinfo_dict):
    """ Retrieves a basic list of CPU information, including SKU name, cores/threads, and usage metrics. """
    # Generate list for CPU information
    # Format: [pretty_model, physical_cores, logical_cores, usage_percent]
    try:
        # Get CPU model name (i.e. AMD Ryzen 7 5800X3D 8-Core Processor, Apple M2, etc.)
        if CLIENT_PLATFORM == "win32":
            sysinfo_dict['cpu_model'] = subprocess.check_output(GET_CPU_MODEL_CMD, shell=True).decode().strip().split('\n')[1].strip()
        elif CLIENT_PLATFORM == "linux":
            sysinfo_dict['cpu_model'] = subprocess.check_output(GET_CPU_MODEL_CMD, shell=True).decode().split(':')[1].strip()
        elif CLIENT_PLATFORM == "darwin":
            sysinfo_dict['cpu_model'] = subprocess.check_output(GET_CPU_MODEL_CMD).decode().strip()
        # Get amount of physical cores, logical cores, and system-wide CPU usage (as a percentage over a .5 second interval)
        sysinfo_dict.update({
            'cpu_physical_cores': psutil.cpu_count(logical=False),
            'cpu_logical_cores': psutil.cpu_count(),
            'cpu_usage_percent': psutil.cpu_percent(interval=1),
        })
    except Exception as e:
        print(f'ERROR: Critical error occurred while attempting to obtain CPU information: {e}')
        print("Exiting...")
        sys.exit(1)

def get_mem_info(sysinfo_dict):
    """ Retrieves information on memory usage statistics. """
    try:
        # Get available virtual memory, total virtual memory, and percentage utilization
        sysinfo_dict.update({
            'virtual_memory_used_MiB': round((psutil.virtual_memory().total - psutil.virtual_memory().available) / 1.049e+6),
            'virtual_memory_available_MiB': round(psutil.virtual_memory().available / 1.049e+6),
            'virtual_memory_total_MiB': round(psutil.virtual_memory().total / 1.049e+6),
            'virtual_memory_util_percent': psutil.virtual_memory().percent
        })
    except Exception as e:
        print(f'ERROR: Critical error occurred while attempting to obtain Memory information: {e}')
        print("Exiting...")
        sys.exit(1)

def get_disk_info(sysinfo_dict):
    """ Retrieves information on disk usage statistics, with proper handling of APFS disk overprovisioning. """
    try:
        # Get used space, total available space, and percentage used
        sysinfo_dict.update({
            'disk_used_MiB': round(psutil.disk_usage(ROOT_DIR).used / 1.049e+6),
            'disk_available_MiB': round((psutil.disk_usage(ROOT_DIR).total - psutil.disk_usage(ROOT_DIR).used) / 1.049e+6),
            'disk_total_MiB': round(psutil.disk_usage(ROOT_DIR).total / 1.049e+6),
            'disk_usage_percent': psutil.disk_usage(ROOT_DIR).percent
        })
    except Exception as e:
        print(f'ERROR: Critical error occurred while attempting to obtain Disk Usage information: {e}')
        print("Exiting...")
        sys.exit(1)
    
def export_to_json(sysinfo_dict, output_file):
    """ Exports all retrieved system information to a JSON file for ease-of-access. """
    with open(output_file, "w") as json_outfile:
        json.dump(sysinfo_dict, json_outfile, indent=4)

def export_to_csv(sysinfo_dict, output_file):
    """ Exports all retrieved system information to a CSV file for ease-of-access. """
    with open(output_file, "w", newline="") as csv_outfile:
        out = csv.writer(csv_outfile)
        out.writerows(sysinfo_dict.items())


# Run main() if called directly from cmd, otherwise function as an importable library
if __name__ == '__main__':
    main()