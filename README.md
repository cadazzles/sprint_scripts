![healthmon.py](media/healthmon-ascii.png)

System resource health monitor written in Python featuring output to local logs and syslog, in addition to console output.
Created for SEC444: Security Automation as part of the fourth sprint (sprint4).

## Description
healthmon takes a JSON file as input (see `config.json`), which contains thresholds for the following system statistics:

- Primary disk (`/`) usage percentage
- Memory usage percentage
- CPU 1-minute load average
- `systemd` services that must be alive

While the script runs, if any of these thresholds are exceeded, a `WARNING` message is logged to `log_file`, `alert_log` (both configurable in the config JSON) and the system's syslog. Optional console printing is available via a command line flag.

This script is primarily meant to be run on an automatic schedule (i.e. via `cron`).

## Getting Started
### Dependencies
- A modern **Linux** system with **systemd** as the init system
- Python 3.9 or later
- If running on a schedule, `cron` or other such automation tool

#### Additional dependencies
- [distro 1.9.0](https://pypi.org/project/distro)
- [psutil 7.2.2](https://pypi.org/project/psutil)

All module dependencies are listed in `requirements.txt` in the project root.

## Installation
1. Navigate to the sprint4-healthmon branch. You can see these instructions, so yet again, you're already here. (Yippee!)
2. Clone the repository via Git by running `git clone -b sprint4-healthmon https://github.com/cadazzles/sprint_scripts.git` in a terminal, or by downloading a ZIP copy of the current repo state using the **Code** button.
3. Navigate to the `sprint_scripts` directory once cloned or unzipped.
4. **[RECOMMENDED]** Create a virtual environment to safely install required dependencies by running `python3 -m venv .venv/`. (Note: Some Linux distributions omit python3-virtualenv from their default Python install. Use your distro's package manager to install it.)
5. Activate the virtual environment by using `source .venv/bin/activate`.
6. Install all required dependencies by using `pip install -r requirements.txt`.
7. Run the script using `python3 healthmon.py --help` to view usage instructions, or alternatively view them below.

### Usage instructions
```
usage: healthmon.py [-h] [--check] [config_file]

Check health of system resources and critical services based on config file.

positional arguments:
    config_file  Path to a .json file containing the script configuration.

options:
    -h, --help   show this help message and exit
    --check      Enable logging to screen
```
By default, config_file will look for a `config.json` file in the current directory. A sample file with absurdly low test thresholds has been provided and can be edited as necessary.

### Example Output
1. sshd is not installed or not available on the current system
```
2026-06-02 19:45:35,735 [ERROR] healthmon: System service sshd is not available!!
```
2. Memory usage above expected threshold
```
2026-06-02 19:45:35,735 [WARNING] healthmon: Memory usage at 43.1%, expected 30%
```

## Known Issues
None so far.

## Authors
Alec Wandy - [@cadazzles](https://github.com/cadazzles)\
This script was largely written without assistance from generative AI tools.

## License
This project is licensed under the MIT License - see the LICENSE.md file for details.