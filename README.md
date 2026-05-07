![sysinfo.py](./media/ascii-logo.png)

Quick and dirty system information grabber written in Python featuring multiple-format output and comprehensive multiplatform support.
Created for SEC444: Security Automation as part of the second sprint (sprint2).

## Description
sysinfo.py gathers a selection of crucial information about a Windows/macOS/Linux system, including:

- Hostname
- System uptime
- Operating system info:
    - OS type (Windows, macOS, Linux)
    - Windows edition (Core, Professional, etc.)
    - macOS version codename (Sequoia, Tahoe, etc.)
    - Linux distribution name
    - OS release version (i.e. Windows 11, macOS 26.4)
    - OS kernel version
- CPU info:
    - Pretty-printed model name (i.e. AMD Ryzen 7 5800X3D 8-Core Processor, Apple M2)
    - Physical CPU cores
    - Logical CPU cores (threads)
    - CPU frequency
    - CPU utilization percentage snapshot
- Virtual memory & swap memory info:
    - Amount utilized (MiB)
    - Total amount (MiB)
    - Percent utilized (MiB)
    - Amount free (MiB)
- Disk info:
    - Current root directory and filesystem
    - Amount utilized on root device (MiB)
    - Total amount on root device (MiB)
    - Percent utilized on root device (MiB)
    - Amount free on root device (MiB)
- Network interface info (per interface):
    - IPv4 address
    - IPv6 address
    - MAC address

Information is outputted to either the terminal (stdout), a CSV file, or a JSON file, based on a command-line argument taken when invoked. Works as a module or as a standalone utility.

## Getting Started
### Dependencies
- A supported client operating system (Windows, Linux, macOS 11 "Big Sur" or later)
- Python 3.9 or later

#### Additional dependencies
- [distro 1.9.0](https://pypi.org/project/distro/)
- [psutil 7.2.2](https://pypi.org/project/psutil/)

All dependencies are included in the `requirements.txt` file in the project root.

### Installation
1. Navigate to the `sprint2-sysinfo` branch. You can see this, so you're already here. (Yay!)
2. Clone the repository via Git by running `git clone -b sprint2-sysinfo https://github.com/cadazzles/sprint_scripts.git` in a terminal, or by downloading a ZIP copy of the current repo state by pressing the **Code** button. Navigate to the repo directory once cloned or unzipped.
3. **[RECOMMENDED]** Create a virtual environment for installing the required dependencies by running `python3 -m venv .venv/`. (Note: Some Linux distributions omit python3-virtualenv from their default Python install. Use your package manager to install it.)
4. Activate the virtual environment using the platform specific command: `.\.venv\Scripts\Activate.ps1` for Windows, `source .venv/bin/activate` for macOS/Linux.
5. Install the required dependencies by using `pip install -r requirements.txt`.
6. Run the script using `python3 sysinfo.py.` - see usage instructions below for more information.

### Usage instructions
```
$ python3 sysinfo.py <screen | csv | json> <output_file>
```
#### Arguments
`screen`: Outputs all gathered information to the terminal (standard output).\
`csv`: Outputs all gathered information to a CSV file.\
`json`: Outputs all gathered information to a JSON file.

`output_file`: Absolute or relative path to the desired output file when operating in CSV or JSON mode. Defaults to `sysinfo.csv` or `sysinfo.json` in the current working directory.

### Example usage/output
![Example screen mode output](./media/example_screen_output.png)

### Known Issues
None so far.

**NOTE:** This script was developed and tested using the following operating systems:
- Windows 11 (25H2)
- macOS 26.4 (Tahoe)
- Ubuntu 24.04 LTS

Outside of versions not covered by the requirements, other versions should work; but please keep this in mind.

## Authors
Alec Wandy - [@cadazzles](https://github.com/cadazzles)\
This script was largely written without assistance from generative AI tools.

## License
This project is licensed under the MIT License - see the LICENSE.md file for details.
