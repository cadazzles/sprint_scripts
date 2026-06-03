#!/usr/bin/python3

# Uses threshold and service definitions in a config.json file to watch and alert for anomalies in CPU/memory/disk usage load and service health.
# All output is written to log files via the Python logging module, and alerts (i.e. exceeded thresholds) are also outputted to /var/log/syslog.
# System information is retrieved using sysinfo.py (Sprint 2), included as a snapshotted/modified version in the repository. This script is
# designed to be run on a schedule via cron or another scheduled run utility.
#
# Licensed under the MIT License (https://opensource.org/license/mit)
# AlecWandy-20260602: Initial version

# Imports
import json
import argparse
import sys
import subprocess
import logging
from logging.handlers import SysLogHandler
from sysinfo import get_cpu_info, get_mem_info, get_disk_info

# Constants

# Define logger object
logger = logging.getLogger("healthmon")
logger.setLevel(logging.INFO)
# Format for logging lines (ex: 2026-06-02 17:24:03 [WARNING] healthmon: Disk usage is at 85% (threshold: 80%))
log_format = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')

def main():
    """ Primary script entry point - handles parsed cmd arguments and runs necessary functions prior to logging. """
    check_if_os_supported()
    config, is_verbose_mode = parse_args()
    create_log_handlers(config, is_verbose_mode)
    health_stats = collect_all(config)
    log_health_events(config, health_stats)


def check_if_os_supported():
    """ Check if the current OS is Linux-based & using systemd, as this script only supports Linux + systemd systems for logging. """
    if not sys.platform in ["linux"]:
        logger.error(f'ERROR: platform {sys.platform} is not supported by healthmon. Please run this script from a Linux system.')
        sys.exit(1)
    else:
        try:
            subprocess.run(['systemctl', 'is-system-running'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        except FileNotFoundError:
            logger.error(f'ERROR: This system is not using systemd for init and is not supported. Please run this script from a Linux system with systemd.')
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

def get_cpu_health(config):
    current_cpu_stats = get_cpu_info()
    cpu_load = current_cpu_stats['load_1_min']
    if cpu_load > config['checks']['cpu_load_1min']:
        is_cpu_usage_above_threshold = True
    else:
        is_cpu_usage_above_threshold = False
    
    return {
        'cpu_load': cpu_load,
        'above_threshold': is_cpu_usage_above_threshold
    }

def get_mem_health(config):
    current_mem_stats = get_mem_info()
    mem_load = current_mem_stats['virtual_memory_util_percent']
    if mem_load > config['checks']['memory_usage_percent']:
        is_mem_usage_above_threshold = True
    else:
        is_mem_usage_above_threshold = False
    
    return {
        'mem_load': mem_load,
        'above_threshold': is_mem_usage_above_threshold
    }

def get_disk_health(config):
    current_disk_stats = get_disk_info()
    disk_load = current_disk_stats['usage_percent']
    if disk_load > config['checks']['disk_usage_percent']:
        is_disk_usage_above_threshold = True
    else:
        is_disk_usage_above_threshold = False
    
    return {
        'disk_load': disk_load,
        'above_threshold': is_disk_usage_above_threshold
    }

def get_service_health(service):
    try:
        systemctl_result = subprocess.run(['systemctl', 'is-active', service], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        systemctl_status = systemctl_result.stdout.strip()
        if systemctl_status == "active":
            return {
                'available': True
            }
        else:
            return {
                'available': False
            }
    except FileNotFoundError:
        logger.error('ERROR: Failed to run systemctl on this system. Please make sure systemd is working properly.')
        sys.exit(1)

def create_log_handlers(config, is_verbose_mode):
    if is_verbose_mode == True:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(log_format)
        logger.addHandler(console_handler)
    generic_log_handler = logging.FileHandler(config['log_file'])
    generic_log_handler.setLevel(logging.INFO)
    generic_log_handler.setFormatter(log_format)
    logger.addHandler(generic_log_handler)
    alert_log_handler = logging.FileHandler(config['alert_log'])
    alert_log_handler.setLevel(logging.WARNING)
    alert_log_handler.setFormatter(log_format)
    logger.addHandler(alert_log_handler)
    syslog_handler = SysLogHandler(address='/dev/log')
    syslog_handler.setLevel(logging.WARNING)
    syslog_handler.setFormatter(log_format)
    logger.addHandler(syslog_handler)

def collect_all(config):
    health_stats = {}
    health_stats['cpu'] = get_cpu_health(config)
    health_stats['mem'] = get_mem_health(config)
    health_stats['disk'] = get_disk_health(config)
    health_stats['services'] = {}
    for service in config['checks']['services']:
        health_stats['services'][service] = get_service_health(service)
    
    return health_stats

def log_health_events(config, health_stats):
    if health_stats['cpu']['above_threshold'] == True:
        logger.warning(f'CPU 1 minute load average at {health_stats['cpu']['cpu_load']}, expected {config['checks']['cpu_load_1min']}')
    if health_stats['mem']['above_threshold'] == True:
        logger.warning(f'Memory usage at {health_stats['mem']['mem_load']}%, expected {config['checks']['memory_usage_percent']}%')
    if health_stats['disk']['above_threshold'] == True:
        logger.warning(f'Disk usage at {health_stats['disk']['disk_load']}%, expected {config['checks']['disk_usage_percent']}%')
    for service in health_stats['services']:
        if health_stats['services'][service]['available'] == False:
            logger.error(f'System service {service} is not available!!!')


if __name__ == '__main__':
    main()