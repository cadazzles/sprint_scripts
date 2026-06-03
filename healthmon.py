#!/usr/bin/python3

# Uses threshold and service definitions in a config.json file to watch and alert for anomalies in CPU/memory usage load and service health.
# All output is written to log files via the Python logging module, and alerts (i.e. exceeded thresholds) are outputted to /var/log/syslog.
# System information is retrieved using sysinfo.py (Sprint 2), included as a snapshotted/modified version in the repository. This script is
# designed to be run on a schedule via cron or another scheduled run utility.
#
# Licensed under the MIT License (https://opensource.org/license/mit)
# AlecWandy-20260602: Initial version

# Imports
import json
import argparse
import sys
import logging
from sysinfo import get_cpu_info, get_mem_info

# Constants

# Define logger object
logger = logging.getLogger("healthmon")
logger.setLevel(logging.INFO)
# Format for logging lines (ex: 2026-06-02 17:24:03 [WARNING] healthmon: Disk usage is at 85% (threshold: 80%))
log_format = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')

def main():
    """ Primary script entry point - handles parsed cmd arguments and passes them to recon functions before outputting. """
    parse_args()

def check_if_os_linux():
    """ Check if the current OS is Linux-based, as this script only supports Linux systems for logging. """
    if not sys.platform in ["linux"]:
        logger.error(f'ERROR: platform {sys.platform} is not supported by healthmon. Please run this script from a Linux system.')
        sys.exit(1)

def parse_args():
    """ Parses arguments taken from the command line, including exception handling for missing/incorrect arguments. """
    parser = argparse.ArgumentParser(description="Check health of system resources and critical services based on config file.")
    parser.add_argument('config_file', nargs='?', type=str, default='./config.json', help="Path to a .json file containing the script configuration.")
    parser.add_argument('--check', action='store_true', help="Enable logging to screen")
    args = parser.parse_args()
    # Check if specified config.json file exists
    try:
        with open(args.config_file, 'r') as config_file:
            config = json.load(config_file)
    except FileNotFoundError:
        logger.error(f'ERROR: Config file at {args.config_file} couldn\'t be found. Please try again.')
        sys.exit(1)
    except PermissionError:
        logger.error(f'ERROR: Inadequate permissions to access config file at {args.config_file}.')
        sys.exit(1)
    
    return config, args.check





if __name__ == '__main__':
    main()