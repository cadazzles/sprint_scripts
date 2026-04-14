#!/usr/bin/python3

# Parses a Linux auth.log file to extract relevant security data (failed logins), then performs regex ops on the extracted data to obtain
# a structured set of req'd information (timestamp, username, IP address). Commandline arguments are taken to specify log filepath and output CSV path.
# Final output is returned to terminal and outputted to a CSV for future reference.
#
# Licensed under the MIT License (https://opensource.org/license/mit)
# AlecWandy-20260413: Initial version

# Imports
import sys
import os
import re
import csv

def main():
    # Exception handling for command-line arguments
    try:
        # Attempt to set log file for analysis as first argument, otherwise error out if no argument is given
        log_file = sys.argv[1]
        # If a name for the output csv is provided, use it - otherwise, use a default name of "output.csv"
        output_csv = sys.argv[2] if len(sys.argv) > 2 else 'output.csv'

        # Ensure that the path to the log file provided is actually an existing file
        if not os.path.isfile(log_file):
            print(log_file + " does not exist. Try another file.")
        
    except IndexError:
        # Exit with error code 1 and print help message if no log file is provided
        print("Usage: python3 logparser.py <path_to_log_file> <optional: output_csv>")
        sys.exit(1)

if __name__ == '__main__':
    main()