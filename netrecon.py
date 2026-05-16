#!/usr/bin/python3

# Scans a target IP for open ports using python-nmap, and records port number, service name, and port state.
# Additionally runs queries against a public IP geolocation API (ipapi.co, as it doesn't require an API key)
# to get the target IP's country, region, city, and ISP. A summary of the results is printed to the screen *and*
# to a CSV file. Contains built-in SSH client via Paramiko for connecting to open hosts.
#
# Licensed under the MIT License (https://opensource.org/license/mit)
# AlecWandy-20260515: Initial version

# Imports

# Constants

def main():
    """ Primary script entry point - handles parsed cmd arugments and passes them to recon functions before outputting """

# Run main() if called directly from cmd, otherwise function as import library
if __name__ == '__main__':
    main()