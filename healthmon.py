#!/usr/bin/python3

# Uses threshold and service definitions in a config.json file to watch and alert for anomalies in CPU/memory usage load and service health.
# All output is written to log files via the Python logging module, and alerts (i.e. exceeded thresholds) are outputted to /var/log/syslog.
# System information is retrieved using sysinfo.py (Sprint 2), included as a snapshotted/modified version in the repository. This script is
# designed to be run on a schedule via cron or another scheduled run utility.
#
# Licensed under the MIT License (https://opensource.org/license/mit)
# AlecWandy-20260602: Initial version

# Imports
from sysinfo import get_cpu_info, get_mem_info
# Constants

def main():
    """ Primary script entry point - handles parsed cmd arguments and passes them to recon functions before outputting """

if __name__ == '__main__':
    main()