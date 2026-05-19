#!/usr/bin/python3

# Scans a target IP for open ports using python-nmap, and records port number, service name, and port state.
# Additionally runs queries against a public IP geolocation API (ip-api.com, as it doesn't require an API key)
# to get the target IP's country, region, city, and ISP. A summary of the results is printed to the screen *and*
# to a CSV file. Contains built-in SSH client via Paramiko for connecting to open hosts.
#
# Licensed under the MIT License (https://opensource.org/license/mit)
# AlecWandy-20260515: Initial version

# Imports
import sys
import requests
import ipaddress
import nmap
from rich import print
from rich.console import Console

# Constants
DEFAULT_OUTPUT_FILE = "output.csv"

def main():
    """ Primary script entry point - handles parsed cmd arugments and passes them to recon functions before outputting """
    target_ip, output_file, is_public_ip = parse_args()
    target_geolocation, target_scan_data = collect_all(target_ip, is_public_ip)
    export_to_screen(target_geolocation, target_scan_data)

def parse_args():
    """ Parses arguments taken from the command line, including exception handling for missing/incorrect arguments"""
    try:
        target_ip = sys.argv[1]
    except IndexError:
        # Exit with error code and print help message if no args are provided
        print("Usage: python3 netrecon.py <target_ip> <optional: outfile.csv>")
        sys.exit(1)
    # Validate that the IP address supplied is a "real" IP address
    try:
        check_ip = ipaddress.ip_address(target_ip)
    except ValueError:
        # Exit with error code if IP address is not valid
        print("ERROR: Supplied IP address is not a valid IPv4/IPv6 address.")
        sys.exit(1)
    # Use default output filename if there is no replacement
    output_file = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUTPUT_FILE
    # Add CSV extension if not present in custom filename
    if not output_file.endswith(".csv"):
        output_file += ".csv"
    # Check if target IP address resides within private address space (this affects geolocation)
    if check_ip.is_private:
        is_public_ip = False
    else:
        is_public_ip = True
    return target_ip, output_file, is_public_ip

def get_ip_geolocation(target_ip, is_public_ip):
    """ Uses ip-api.com's public API via requests to retrieve JSON-encoded geolocation info on the target IP. Returns a dict with info. """
    # Uses requests to send HTTP GET to ip-api's endpoint if we have a public IP
    if is_public_ip:
        try:
            api_response = requests.get(f'http://ip-api.com/json/{target_ip}')
        except Exception as e:
            # Handle errors: inaccessible api endpoint, response taking too long due to network issues, etc
            print(f'ERROR: Failed to retrieve a result from ip-api.com endpoint - Reason: {e}.')
            print(f'Exiting...')
            sys.exit(1)
        # Encode response as JSON; JSON is naturally a dict, which is what we want
        target_geolocation = api_response.json()
    else:
        # only return the target ip address (for export) if the IP address is private
        target_geolocation = { 'query': target_ip }
    return target_geolocation

def get_open_ports(target_ip):
    """ Uses python-nmap (and nmap as installed on the system) to scan the target IP for open ports. Results are returned as a dictionary."""
    # Initialize port scanner object
    nm = nmap.PortScanner()
    # Scan target IP address for most common open ports + retrieve service information
    try:
        nm.scan(target_ip, arguments='-sV')
    except nmap.PortScannerError:
        # Catch error if nmap is not installed on the system, as we don't install it via pip
        print('ERROR: Couldn\'t find Nmap on your system. Try installing it via your package manager or by browsing to https://nmap.org.')
        print('Exiting...')
        sys.exit(1)
    return nm

def collect_all(target_ip, is_public_ip):
    """ Passes target IP and IP public/private status into collector functions to retrieve information. Displays a helpful spinner and progress text."""
    # Create rich console object (only used for spinner)
    console = Console()
    # Create progress spinner with helper text
    with console.status(f'[bold]Performing reconnaisance on target IP {target_ip} - this may take a while...[/bold]') as status:
        target_geolocation = get_ip_geolocation(target_ip, is_public_ip)
        console.log("Successfully retrieved geolocation information.")
        target_scan_data = get_open_ports(target_ip)
        console.log("Successfully retrieved Nmap scan data.")
    return target_geolocation, target_scan_data

def export_to_screen(target_geolocation, target_scan_data):
    """ Exports collected geolocation and port scanning data to the screen in a human-readable manner. """
    print(f'\n[bold]Target IP Address:[/bold] {target_geolocation['query']}')
    print(f'======[Geolocation Info]==================')
    # If dealing with a public IP...
    if 'country' in target_geolocation:
        print(f'[bold]Country:[/bold] {target_geolocation['country']} ({target_geolocation['countryCode']})')
        print(f'[bold]City & State/Region:[/bold] {target_geolocation['city']}, {target_geolocation['regionName']} ({target_geolocation['region']})')
        print(f'[bold]ISP:[/bold] {target_geolocation['isp']}')
    else:
        print(f'Local/Private IP (no geolocation data)')
    print(f'======[Nmap Port Scan (top 1000 ports)]===')
    # Cycle through the massive Nmap results dictionary to get port, service, and state of each port, since that's all we want
    for host in target_scan_data.all_hosts():
        for proto in target_scan_data[host].all_protocols():
            # Print header text, alongside differentiation between tcp and udp
            print(f'[[bold]Protocol:[/bold] {proto}]')
            print(f'{"Port":<5} {"Service":<12} {"State":<10}')
            # Sort results in numerical order
            sorted_ports = sorted(target_scan_data[host][proto].keys())
            # Print results per port
            for port in sorted_ports:
                service = target_scan_data[host][proto][port]['name']
                state = target_scan_data[host][proto][port]['state']
                print(f'{port:<5} {service:<12} {state:<10}')

# Run main() if called directly from cmd, otherwise function as import library
if __name__ == '__main__':
    main()