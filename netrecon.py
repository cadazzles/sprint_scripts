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
    target_ip, output_file = parse_args()
    target_geolocation, target_scan_data = collect_all(target_ip)
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
        ipaddress.ip_address(target_ip)
    except ValueError:
        # Exit with error code if IP address is not valid
        print("ERROR: Supplied IP address is not a valid IPv4/IPv6 address.")
        sys.exit(1)
    output_file = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUTPUT_FILE
    if not output_file.endswith(".csv"):
        output_file += ".csv"
    
    return target_ip, output_file

def get_ip_geolocation(target_ip):
    """ Uses ip-api.com's public API via requests to retrieve JSON-encoded geolocation info on the target IP. Returns a dict with info. """
    # Uses requests to send HTTP GET to ip-api's endpoint
    try:
        api_response = requests.get(f'http://ip-api.com/json/{target_ip}')
    except Exception as e:
        print(f'ERROR: Failed to retrieve a result from ip-api.com endpoint - Reason: {e}.')
        print(f'Exiting...')
        sys.exit(1)
    # Encode response as JSON; JSON is naturally a dict, which is what we want
    target_geolocation = api_response.json()
    return target_geolocation

def get_open_ports(target_ip):
    """ Uses python-nmap (and nmap as installed on the system) to scan the target IP for open ports. Results are returned as a dictionary."""
    # Initialize port scanner object
    nm = nmap.PortScanner()
    # Scan target IP address for most common open ports + retrieve service information
    try:
        nm.scan(target_ip, arguments='-sV')
    except ImportError:
        print('ERROR: python-nmap couldn\'t be initialized. Please check to make sure you installed all prerequisites via pip and try to run the script again.')
        print('Exiting...')
        sys.exit(1)
    except nmap.PortScannerError:
        print('ERROR: Couldn\'t find Nmap on your system. Try installing it via your package manager or by browsing to https://nmap.org.')
        print('Exiting...')
        sys.exit(1)
    return nm

def collect_all(target_ip):
    console = Console()
    with console.status(f'[bold]Performing reconnaisance on target IP {target_ip} - this may take a while...[/bold]') as status:
        target_geolocation = get_ip_geolocation(target_ip)
        console.log("Successfully retrieved geolocation information.")
        target_scan_data = get_open_ports(target_ip)
        console.log("Successfully retrieved Nmap scan data.")
    return target_geolocation, target_scan_data

def export_to_screen(target_geolocation, target_scan_data):
    """ Exports collected geolocation and port scanning data to the screen in a human-readable manner. """
    print(f'\n[bold]Target IP Address:[/bold] {target_geolocation['query']}')
    print(f'======[Geolocation Info]==================')
    print(f'[bold]Country:[/bold] {target_geolocation['country']} ({target_geolocation['countryCode']})')
    print(f'[bold]City & State/Region:[/bold] {target_geolocation['city']}, {target_geolocation['regionName']} ({target_geolocation['region']})')
    print(f'[bold]ISP:[/bold] {target_geolocation['isp']}')
    print(f'======[Nmap Port Scan (top 1000 ports)]===')
    for host in target_scan_data.all_hosts():
        for proto in target_scan_data[host].all_protocols():
            print(f'[[bold]Protocol:[/bold] {proto}]')
            print(f'{"Port":<5} {"Service":<12} {"State":<10}')
            sorted_ports = sorted(target_scan_data[host][proto].keys())

            for port in sorted_ports:
                service = target_scan_data[host][proto][port]['name']
                state = target_scan_data[host][proto][port]['state']
                print(f'{port:<5} {service:<12} {state:<10}')

# Run main() if called directly from cmd, otherwise function as import library
if __name__ == '__main__':
    main()