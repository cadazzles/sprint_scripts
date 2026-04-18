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
from datetime import datetime

# Constants
FAILED_LOGIN_REGEX = r"^([A-Z][a-z]{2}\s+\d+\s\d{2}:\d{2}:\d{2}).*Failed\s+password\s+for\s+(?:invalid\s+user\s+)?(\S+)\s+from\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
DEFAULT_CSV_FILENAME = f'output_{datetime.now():%Y%m%d-%H%M%S%f}.csv'

def main():
    """ Primary script entry point -- takes parsed arguments from the command-line and passes them to the relevant functions, then outputs results """
    log_file, output_csv = parse_args()
    results = extract_data(log_file)

    print_results_to_console(results)
    export_results_to_csv(results, output_csv)

def parse_args():
    """ Exception handling for command-line arguments """
    try:
        # Attempt to use log file from specified path for analysis - IndexError is handled if no argument is provided
        log_file = sys.argv[1]
    except IndexError:
        # Exit with error code 1 and print help message if no arguments are provided
        print("Usage: python3 logparser.py <path_to_log_file> <optional: path_to_output_csv>")
        sys.exit(1)

    # If an argument specifying the path for the output csv is provided, use it - otherwise, use default name in working dir
    output_csv = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_CSV_FILENAME  
    # Run validation checks on the given log file
    validate_log_file(log_file)
    # Make sure the output csv ends with a .csv extension; add it if it doesn't have one
    if not output_csv.endswith(".csv"):
        output_csv = output_csv + ".csv"
    return log_file, output_csv

def validate_log_file(log_file):
    """ Validates that the log file actually exists and contains data to be analyzed - immediately quit if validation fails """
    # Ensure that the path to the log file provided is actually an existing file
    if not os.path.isfile(log_file):
        print(f'Error: {log_file} does not exist. Try another file.')
        sys.exit(1)
    # Ensure that the log file provided is not completely empty (i.e. size = 0 bytes)
    if os.path.getsize(log_file) == 0:
        print(f'Error: auth.log file {log_file} is empty. Try another file.')
        sys.exit(1)
    # Ensure that the log file provided does not only contain whitespace
    with open(log_file, 'r') as log:
        if not log.read().strip():
            print(f'Error: auth.log file ({log_file}) provided is blank (contains only whitespace). Try another file.')
            sys.exit(1)

def extract_data(log_file):
    """ Extract relevant data from supplied auth.log file """
    # Create list to hold every regex-matched failed login
    failed_logins = []

    with open(log_file, 'r') as log:
        for line in log:
            # Only work on lines containing "failed password", as these are the lines we are primarily concerned with
            if "failed password" not in line.lower():
                continue
            # regex matching: isolates date/time, username, and source ip address from each line. accounts for instances of "invalid user"
            matched_string = re.findall(FAILED_LOGIN_REGEX, line) 
            # if the pattern is successfully matched + isolated, add it to our list of failed logins
            if matched_string:
                failed_logins += matched_string
    return failed_logins

def print_results_to_console(results):
    """ Print results to console with indicators for which data corresponds to which relevant field """
    for timestamp, username, ip in results:
        print(f'Attempt Time/Date: {timestamp} | Username: {username:<13} | Source IP Address: {ip}')
    print(f'Total failed attempts: {len(results)}')

def export_results_to_csv(results, output_csv):
    """ Print results to the designated output CSV file in a similar format to the console """
    # Temporary list containing the header/footer information for the CSV. This gets prepended/appended to the results that get exported to CSV.
    csv_header = [('Attempt Time/Date', 'Username', 'Source IP Address')]
    csv_footer = [('Total failed attempts', len(results), '')]
    # This is NOT fast - it's O(n) - but it does the job for smaller logs
    csv_contents = csv_header + results + csv_footer
    # Export results to CSV file
    with open(output_csv, 'w', newline='') as output:
        csv_writer = csv.writer(output)
        csv_writer.writerows(csv_contents)
    # Inform the user that a CSV version of the results was created
    print(f'A CSV version of the results was outputted to {output_csv}.')

# Run main() if called directly from cmd, otherwise function as an import library
if __name__ == '__main__':
    main()