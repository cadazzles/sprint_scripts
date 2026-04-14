# logparser.py
Created for SEC444: Security Automation as part of the first sprint (sprint1).

## Description
logparser.py parses a Linux auth.log file to extract security data (for the purposes of this assignment: failed login attempts).
Regex pattern matching is performed on a line-by-line basis to isolate three main data points: Access Time/Date, Username, and Source IP Address.
This script, by default, outputs all results to the console *and* to a CSV file for future reference.

## Getting Started
