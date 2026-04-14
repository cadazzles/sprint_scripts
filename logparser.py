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
    log_file, output_csv = parse_args()
    results = extract_data(log_file)

    print_results_to_console(results)
    export_results_to_csv(results, output_csv)


# Exception handling for command-line arguments
def parse_args():
    try:
        # Attempt to set log file for analysis as first argument, otherwise error out if no argument is given
        log_file = sys.argv[1]
        # If a name for the output csv is provided, use it - otherwise, use a default name of "output.csv"
        output_csv = sys.argv[2] if len(sys.argv) > 2 else 'output.csv'

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
                print(f'Error: auth.log file ({log_file}) provided is blank (contains only whitespace)')
                sys.exit(1)
        
        # Make sure the output csv ends with a .csv extension; add it if it doesn't have one
        if not output_csv.endswith(".csv"):
            output_csv = output_csv + ".csv"

        return log_file, output_csv
    except IndexError:
        # Exit with error code 1 and print help message if no log file is provided
        print("Usage: python3 logparser.py <path_to_log_file> <optional: output_csv>")
        sys.exit(1)

# Extract relevant data from supplied auth.log file
def extract_data(log_file):
    # Create list to hold every regex-matched failed login
    failed_logins = []

    with open(log_file, 'r') as log:
        for line in log:
            # Only work on lines containing "failed password", as these are the lines we are primarily concerned with
            if "failed password" in line.lower():
                # regex matching: isolates date/time, username, and source ip address from each line. accounts for instances of "invalid user"
                matched_string = re.findall(r"^([A-Z][a-z]{2}\s+\d+\s\d{2}:\d{2}:\d{2}).*Failed\s+password\s+for\s+(?:invalid\s+user\s+)?(\S+)\s+from\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", line)
                
                # if the pattern is successfully matched + isolated, add it to our list of failed logins
                if matched_string:
                    failed_logins += matched_string
    
    return failed_logins

# Print results to console with indicators for which data corresponds to which relevant field
def print_results_to_console(results):
    total_failed_attempts = len(results)
    for timestamp, username, ip in results:
        print(f'Access Time/Date: {timestamp}, Username: {username}, Source IP Address: {ip}')
    print(f'Total failed attempts: {total_failed_attempts}')

# Print results to the designated output CSV file in a similar format to the console
def export_results_to_csv(results, output_csv):
    # Temporary list containing the header/footer information for the CSV. This gets prepended/appended to the results that get exported to CSV.
    csv_header = [('Access Time/Date', 'Username', 'Source IP Address')]
    csv_footer = [('Total failed attempts', len(results), '')]
    # This is NOT fast - it's O(n) - but it does the job on modern CPUs because our list of results has less than 1000 entries
    csv_contents = csv_header + results + csv_footer

    # Export results to CSV file
    with open(output_csv, 'w', newline='') as output:
        csv_writer = csv.writer(output)
        csv_writer.writerows(csv_contents)

if __name__ == '__main__':
    main()