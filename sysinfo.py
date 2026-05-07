#!/usr/bin/python3

# Gathers information about a Windows/macOS/Linux system, including hostname, OS info, CPU, memory usage, disk usage, IP address, MAC address, and uptime.
# Information is outputted to either the terminal (stdout), a CSV file, or a JSON file, based on a command-line argument taken when invoked. Works as a module
# or as a standalone utility.
#
# Licensed under the MIT License (https://opensource.org/license/mit)
# AlecWandy-20260427: Initial version

# Imports
import sys
import os
import subprocess
import platform
import distro
import psutil
import socket
import time
import json
import csv
from datetime import datetime, timedelta

# Constants
DEFAULT_OUTPUT_FILE = "sysinfo"
CLIENT_PLATFORM = sys.platform
# Define platform-specific constants
if CLIENT_PLATFORM == "win32":
    ROOT_DIR = "C:\\"
    GET_CPU_MODEL_CMD = "wmic cpu get name"
elif CLIENT_PLATFORM == "linux":
    ROOT_DIR = "/"
    GET_CPU_MODEL_CMD = "lscpu | grep 'Model name'"
elif CLIENT_PLATFORM == "darwin":
    ROOT_DIR = "/System/Volumes/Data"
    GET_CPU_MODEL_CMD = ["sysctl", "-n", "machdep.cpu.brand_string"]


def main():
    """ Primary script entry point - handles parsed cmd arguments and passes them to information gathering functions before outputting """
    # Check for compatible OS then parse arguments
    check_script_compat()
    output_mode, output_file = parse_args()
    
    # Create a dictionary for storing all retrieved system information
    # Always make sure to get the current date
    sysinfo_dict = { 'date': str(datetime.now()) }

    # Call primary functions for obtaining system info
    get_hostname_uptime(sysinfo_dict)
    get_os_info(sysinfo_dict)
    get_cpu_info(sysinfo_dict)
    get_mem_info(sysinfo_dict)
    get_disk_info(sysinfo_dict)
    get_net_info(sysinfo_dict)

    # Determine output mode based on argument
    if output_mode == "screen":
        export_to_screen(sysinfo_dict)
    elif output_mode == "json":
        export_to_json(sysinfo_dict, output_file)
    elif output_mode == "csv":
        export_to_csv(sysinfo_dict, output_file)

def check_script_compat():
    """ Basic script compatibility check. If the host system is not one of the supported three, immediately quit with an error. """
    if not CLIENT_PLATFORM in ["win32", "darwin", "linux"]:
        if CLIENT_PLATFORM == "darwin" & int(platform.mac_ver()[0].split('.')[0]) < 11:
            print('ERROR: macOS version is not supported. Required: macOS 11.0 or later. Please run this script from a newer version of macOS.')
            sys.exit(1)
        print(f'ERROR: platform {CLIENT_PLATFORM} is not supported by sysinfo. Please run this script from a supported Windows, macOS, or Linux system.')
        sys.exit(1)

def parse_args():
    """ Parses arguments taken from the command line, including exception handling for missing/incorrect arguments """
    try:
        # Attempt to discern output mode from first supplied argument - IndexError is handled if no arg is provided
        output_mode = sys.argv[1].lower()
    except IndexError:
        # Exit with error code and print help message if no args are provided
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
    # Get time of last system boot (in seconds since UNIX epoch)
    boot_timestamp = psutil.boot_time()
    # Turn into timestamp + format into human-readable duration (w/o microseconds)
    uptime_duration = str(timedelta(seconds=time.time() - boot_timestamp)).split('.')[0]
    sysinfo_dict.update({
        'hostname': platform.node(), # Use platform's best guess for system hostname
        'uptime_duration': uptime_duration
    })

def get_os_info(sysinfo_dict):
    """ Retrieves a selection of pertintent OS information, including platform-specific values (i.e. kernel versions, editions, product versions)"""
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
        # macOS, macOS version (i.e. "26.4.1"), macOS version codename (i.e. "Tahoe"), Darwin version (i.e. "25.4"), OS architecture (i.e. arm64)
            # Get base macOS version (prior to quality updates/security updates)
        current_macOS_edition = platform.mac_ver()[0].split('.')[0]
        # Dict of supported major macOS versions
        macOS_editions = {
            '26': 'Tahoe',
            '15': 'Sequoia',
            '14': 'Sonoma',
            '13': 'Ventura',
            '12': 'Monterey',
            '11': 'Big Sur',
        }
        sysinfo_dict.update({
            'os_type': 'macOS',
            'os_version': platform.mac_ver()[0],
            'os_edition': macOS_editions[current_macOS_edition] if macOS_editions.get(current_macOS_edition) else '',
            'os_kernel_version': platform.release(),
            'os_arch': platform.machine()
        })
    elif CLIENT_PLATFORM == "linux":
        # Retrieves the following information for Linux-based systems
        # Distribution name (i.e. Ubuntu), Distribution version (i.e. 24.04.1 (noble)), Linux kernel version (i.e. 6.6.89-ubuntu-1-1), OS architecture (i.e. AMD64)
        sysinfo_dict.update({
            'os_type': distro.name(),
            'os_version': distro.version(pretty=True, best=True),
            'os_edition': '',
            'os_kernel_version': platform.release(),
            'os_arch': platform.machine()
        })

def get_cpu_info(sysinfo_dict):
    """ Retrieves a basic list of CPU information, including SKU name, cores/threads, and usage metrics. """
    try:
        # Get CPU model name (i.e. AMD Ryzen 7 5800X3D 8-Core Processor, Apple M2, etc.) using platform-specific commands
        # Command output is stripped of extraneous information and whitespace to ensure only relevant sections are shown
        if CLIENT_PLATFORM == "win32":
            sysinfo_dict['cpu_model'] = subprocess.check_output(GET_CPU_MODEL_CMD, shell=True).decode().strip().split('\n')[1].strip()
        elif CLIENT_PLATFORM == "linux":
            sysinfo_dict['cpu_model'] = subprocess.check_output(GET_CPU_MODEL_CMD, shell=True).decode().split(':')[1].strip()
        elif CLIENT_PLATFORM == "darwin":
            sysinfo_dict['cpu_model'] = subprocess.check_output(GET_CPU_MODEL_CMD).decode().strip()
        sysinfo_dict.update({
            # Get amount of physical cores, logical cores, and system-wide CPU usage (as a percentage recorded over a 1 second interval)
            'cpu_physical_cores': psutil.cpu_count(logical=False),
            'cpu_logical_cores': psutil.cpu_count(),
            'cpu_usage_percent': psutil.cpu_percent(interval=1),
            'cpu_freq': round(psutil.cpu_freq().current / 1000, 2)
        })
    # Print a nice error message in the potential case command doesn't exist
    except FileNotFoundError:
        print(f'CRITICAL: Failed to obtain CPU model information, as the command \"{GET_CPU_MODEL_CMD}\" does not exist on your system.')
        print("Exiting...")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f'CRITICAL: Failed to obtain CPU model information, as the command \"{GET_CPU_MODEL_CMD}\" failed with return code {e.returncode}.')
        print(f'Error message: {e.output.decode()}')
        print('Exiting...')
        sys.exit(1)

def get_mem_info(sysinfo_dict):
    """ Retrieves information on memory usage statistics. """
    # Get used virtual memory, available virtual memory, total virtual memory, and percentage utilization
    # Get used swap, available swap, total swap, and percentage utilization
    # All byte-based values are multiplied by 1.049e+6 to convert from bytes to MiB.
    sysinfo_dict.update({
        'virtual_memory_used_MiB': round((psutil.virtual_memory().total - psutil.virtual_memory().available) / 1.049e+6),
        'virtual_memory_available_MiB': round(psutil.virtual_memory().available / 1.049e+6),
        'virtual_memory_total_MiB': round(psutil.virtual_memory().total / 1.049e+6),
        'virtual_memory_util_percent': psutil.virtual_memory().percent,
        'swap_memory_used_MiB': round(psutil.swap_memory().used / 1.049e+6),
        'swap_memory_available_MiB': round(psutil.swap_memory().free / 1.049e+6),
        'swap_memory_total_MiB': round(psutil.swap_memory().total / 1.049e+6),
        'swap_memory_util_percent': psutil.swap_memory().percent
    })

def get_disk_info(sysinfo_dict):
    """ Retrieves information on root disk filesystem and usage statistics, with proper handling of APFS disk overprovisioning. """
    try:
        # Get file system, used space, available space, total space, and percentage used
        # All byte-based values are multiplied by 1.049e+6 to convert from bytes to MiB.
        sysinfo_dict.update({
            'root_dir': ROOT_DIR,
            'root_fs': get_filesystem_type(ROOT_DIR),
            'disk_used_MiB': round(psutil.disk_usage(ROOT_DIR).used / 1.049e+6),
            'disk_available_MiB': round((psutil.disk_usage(ROOT_DIR).total - psutil.disk_usage(ROOT_DIR).used) / 1.049e+6),
            'disk_total_MiB': round(psutil.disk_usage(ROOT_DIR).total / 1.049e+6),
            'disk_usage_percent': psutil.disk_usage(ROOT_DIR).percent
        })
    except Exception as e:
        print(f'ERROR: Critical error occurred while attempting to obtain Disk Usage information: {e}')
        print("Exiting...")
        sys.exit(1)

def get_filesystem_type(root_path):
    """ Gets the current file system for the root directory/root disk. """
    try:
        path = os.path.abspath(root_path)
        for partition in psutil.disk_partitions(all=True):
            if path.startswith(partition.mountpoint):
                return partition.fstype
    except FileNotFoundError:
        print('CRITICAL: Could not find the root directory!')
        print('Exiting...')
        sys.exit(1)
    except Exception as e:
        print(f'ERROR: Critical error occurred while attempting to identify filesystem type: {e}')
        print('Exiting...')
        sys.exit(1)

def get_net_info(sysinfo_dict):
    """ Retrieves information on network interfaces, including IPv4/IPv6 addresses and MAC addresses. """
    # Create nested dictionary for information on network interfaces - this looks nicer in JSON
    sysinfo_dict['network_interfaces'] = {}
    try:
        # Retrieve complete list of network interfaces from platform
        network_interfaces = psutil.net_if_addrs()
        # For each interface in the list, retrieve name/ipv4/ipv6/MAC and add it to a dict unique to that interface
        for interface_name, addresses in network_interfaces.items():
            # Create dictionary for current interface
            current_interface = {}
            for addr in addresses:
                if addr.family == socket.AF_INET:
                    current_interface['ipv4_address'] = addr.address
                elif addr.family == socket.AF_INET6:
                    current_interface['ipv6_address'] = addr.address
                elif addr.family == psutil.AF_LINK:
                    current_interface['mac_address'] = addr.address
            # Append nested dict with the dict for this specific interface
            sysinfo_dict['network_interfaces'].update({
                interface_name: current_interface
            })
    except Exception as e:
        print(f'ERROR: Critical error occurred while attempting to obtain Network Interface information: {e}')
        print("Exiting...")
        sys.exit(1)

def flatten_sysinfo_dict(sysinfo_dict, parent_key='', sep='_'):
    """ Flattens dictionary holding system information to facilitate transfer to human-readable CSV. """
    # Create a list to hold our complete flattened data structure
    flat_list = []
    for k,v in sysinfo_dict.items():
        # For each original key/value pair, generate a new flattened key (i.e. new key is key1_key2)
        flat_key = f'{parent_key}{sep}{k}' if parent_key else k
        if isinstance(v, dict):
            # if the current value is a dictionary itself, flatten that dictionary as well (key becomes key1_key2_key3, etc.)
            flat_list.extend(flatten_sysinfo_dict(v, flat_key, sep=sep).items())
        else:
            # otherwise append value to our list corresponding to the current flattened key
            flat_list.append((flat_key, v))
    # Convert our flattened list to a dictionary
    return dict(flat_list)

def export_to_screen(sysinfo_dict):
    """ Exports all retrieved system information to the terminal in a human-readable format. """
    print("Gathered the following information about your system:")
    print("=====================================================")
    print(f'Date: {sysinfo_dict['date']}\n')
    print(f'Hostname: {sysinfo_dict['hostname']}')
    print(f'Uptime Duration: {sysinfo_dict['uptime_duration']}')
    print("\n===[Operating System]===================")
    print(f'OS: {sysinfo_dict['os_type']} {sysinfo_dict['os_version']} {sysinfo_dict['os_edition']} ({sysinfo_dict['os_arch']})')
    print(f'Kernel Version: {sysinfo_dict['os_kernel_version']}')
    print("\n===[CPU Information]====================")
    print(f'CPU: {sysinfo_dict['cpu_model']} ({sysinfo_dict['cpu_physical_cores']} cores, {sysinfo_dict['cpu_logical_cores']} threads) @ {sysinfo_dict['cpu_freq']} GHz')
    print(f'CPU Usage: {sysinfo_dict['cpu_usage_percent']}%')
    print("\n===[Memory Information]=================")
    print(f'Virtual Memory: {sysinfo_dict['virtual_memory_used_MiB']} MiB / {sysinfo_dict['virtual_memory_total_MiB']} MiB ({sysinfo_dict['virtual_memory_util_percent']}% used, {sysinfo_dict['virtual_memory_available_MiB']} MiB free)')
    print(f'Swap Memory: {sysinfo_dict['swap_memory_used_MiB']} MiB / {sysinfo_dict['swap_memory_total_MiB']} MiB ({sysinfo_dict['swap_memory_util_percent']}% used, {sysinfo_dict['swap_memory_available_MiB']} MiB free)')
    print("\n===[Disk Usage Information]=============")
    print(f'Root Directory: {sysinfo_dict['root_dir']} [{sysinfo_dict['root_fs']}]')
    print(f'Disk Usage: {sysinfo_dict['disk_used_MiB']} MiB / {sysinfo_dict['disk_total_MiB']} MiB ({sysinfo_dict['disk_usage_percent']}% used, {sysinfo_dict['disk_available_MiB']} MiB free)')
    print("\n===[Network Interfaces]=================")
    # Cycle through nested dict containing network interfaces
    for k,v in sysinfo_dict['network_interfaces'].items():
        # Get the name of each interface
        print(f'{k}')
        # For each key/value pair corresponding to an interface...
        for k2,v2 in v.items():
            # Print the corresponding address
            if k2 == "mac_address":
                print(f'\tMAC Address: {v['mac_address']}')
            elif k2 == "ipv4_address":
                print(f'\tIPv4 Address: {v['ipv4_address']}')
            elif k2 == "ipv6_address":
                print(f'\tIPv6 Address: {v['ipv6_address']}')

def export_to_json(sysinfo_dict, output_file):
    """ Exports all retrieved system information to a JSON file for ease-of-access. """
    try:
        # Dictionaries are already broadly compatible with JSON, just pretty-print out the contents of our dict to a JSON file
        with open(output_file, "w") as json_outfile:
            json.dump(sysinfo_dict, json_outfile, indent=4)
        print(f'Successfully outputted to JSON file \"{output_file}\".')
    except Exception as e:
        print(f'ERROR: Critical error occurred while attempting to output to JSON file: {e}')
        print("Exiting...")
        sys.exit(1)

def export_to_csv(sysinfo_dict, output_file):
    """ Exports all retrieved system information to a CSV file for ease-of-access. """
    try:
        # Flatten sysinfo dictionary for readability (otherwise, network interfaces will get one really long value)
        flattened_sysinfo = flatten_sysinfo_dict(sysinfo_dict)
        # Export flattened sysinfo dict to CSV
        with open(output_file, "w", newline="") as csv_outfile:
            out = csv.writer(csv_outfile)
            out.writerows(flattened_sysinfo.items())
        print(f'Successfully outputted to CSV file \"{output_file}\".')
    except Exception as e:
        print(f'ERROR: Critical error occurred while attempting to output to CSV file: {e}')
        print("Exiting...")
        sys.exit(1)

# Run main() if called directly from cmd, otherwise function as an importable library
if __name__ == '__main__':
    main()