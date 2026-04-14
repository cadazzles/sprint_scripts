# logparser.py
Quick and dirty auth.log parser written in Python featuring human-readable output and automatic CSV export.
Created for SEC444: Security Automation as part of the first sprint (sprint1).

## Description
logparser.py parses a Linux auth.log file to extract security data (for the purposes of this assignment: failed login attempts).
Regex pattern matching is performed on a line-by-line basis to isolate three main data points: 

- Access Time/Date
- Username
- Source IP Address

This script, by default, outputs all results to the console *and* to a CSV file for future reference.

## Getting Started
### Dependencies
This script uses no external dependencies; all functions are performed using Python's built-ins.

### Installation
1. Navigate to the `sprint1-logparser` branch. If you can see these instructions, you're already here.
2. Clone the repository via Git by running `git clone https://github.com/cadazzles/sprint_scripts.git` in a terminal, or download a ZIP copy of the current repository state by pressing the **Code** button.
3. Run the script using `python3 logparser.py`. See usage instructions below.

### Usage instructions
```
python3 logparser.py <path_to_log_file> <optional: output_csv>
```
#### Arguments
`path_to_log_file`: An absolute or relative path leading to a valid Linux auth.log file.\
`output_csv`: **[OPTIONAL]** An absolute or relative path denoting where the CSV version of the results should be outputted to. Defaults to `output.csv` in the current working directory.

## Known Issues
No known issues so far. Comprehensive testing on this script has yet to be done.

**NOTE:** This script was developed and tested using Ubuntu 24.04 LTS. While there is nothing here preventing compatibility with Windows and macOS, please keep this in mind.

## Authors
Alec Wandy - [@cadazzles](https://github.com/cadazzles)\
This script was largely written without assistance from generative AI tools (outside of regex! I hate regex).

## License
This project is licensed under the MIT License - see the LICENSE.md file for details.