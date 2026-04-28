# sysinfo.py

Quick and dirty system information grabber written in Python featuring multiple-format output and comprehensive multiplatform support.
Created for SEC444: Security Automation as part of the second sprint (sprint2).

## Description
sysinfo.py gathers a selection of crucial information about a Windows/macOS/Linux system, including 

- Hostname
- OS info (kernel version & product version)
- CPU (CPU model and utilization snapshot)
- memory usage
- disk usage
- IP address
- MAC address
- uptime

Information is outputted to either the terminal (stdout), a CSV file, or a JSON file, based on a command-line argument taken when invoked. Works as a module or as a standalone utility.

## Getting Started
### Dependencies
- A supported client operating system (Windows, Linux, macOS)
- Python 3.3 or later

TODO: Additional module dependencies

### Installation
TODO: installation instructions

### Usage instructions
```
python3 sysinfo.py <screen | csv | json> <output_file>
```
#### Arguments
`screen`: Outputs all gathered information to the terminal (standard output).\
`csv`: Outputs all gathered information to a CSV file.\
`json`: Outputs all gathered information to a JSON file.

`output_file`: Absolute or relative path to the desired output file when operating in CSV or JSON mode. Defaults to `sysinfo.csv` or `sysinfo.json` in the current working directory.

### Example usage/output
TODO: animated GIF with usage example

### Known Issues
No known issues so far.

**NOTE:** This script was developed and tested using the following operating systems:
- Windows 11 (25H2)
- macOS 26.4 (Tahoe)
- Ubuntu 24.04 LTS

Other versions of these operating systems should work, but please keep this in mind.

## Authors
Alec Wandy - [@cadazzles](https://github.com/cadazzles)\
This script was largely written without assistance from generative AI tools.

## License
This project is licensed under the MIT License - see the LICENSE.md file for details.
