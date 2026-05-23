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
import csv
from rich import print
from rich.console import Console

# Constants
DEFAULT_OUTPUT_FILE = "output.csv"

# Create console object for pretty-printing via rich
console = Console(log_time=False, log_path=False)

def main():
    """ Primary script entry point - handles parsed cmd arugments and passes them to recon functions before outputting """
    target_ip, output_file, is_public_ip = parse_args()
    target_geolocation, target_scan_data = collect_all(target_ip, is_public_ip)
    export_to_screen(target_geolocation, target_scan_data, is_public_ip)
    export_to_csv(target_geolocation, target_scan_data, is_public_ip, output_file)

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
            api_response = requests.get(f'http://ip-api.com/json/{target_ip}', timeout=10)
        except Exception as e:
            # Handle errors: inaccessible api endpoint, response taking too long due to network issues, etc
            print(f'ERROR: Failed to retrieve a result from ip-api.com endpoint - Reason: {e}.')
            target_geolocation = { 'query': target_ip }
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
    # Create progress spinner with helper text
    with console.status(f'[bold]Performing reconnaisance on target IP {target_ip}...[/bold]') as status:
        status.update(f'[bold]Obtaining IP geolocation information for target IP {target_ip}...[/bold]')
        target_geolocation = get_ip_geolocation(target_ip, is_public_ip)
        console.log("Successfully retrieved geolocation information.")
        status.update(f'[bold]Scanning top 1000 ports on {target_ip} via Nmap - this may take a while...[/bold]')
        target_scan_data = get_open_ports(target_ip)
        console.log("Successfully retrieved Nmap scan data.")
    return target_geolocation, target_scan_data

def export_to_screen(target_geolocation, target_scan_data, is_public_ip):
    """ Exports collected geolocation and port scanning data to the screen in a human-readable manner. """
    print(f'\n[bold]Target IP Address:[/bold] {target_geolocation['query']}')
    console.print(f'[magenta]===[Geolocation Info]===[/magenta]', highlight=False)
    # If dealing with a public IP...
    if is_public_ip == True and 'country' in target_geolocation:
        print(f'[bold]Country:[/bold] {target_geolocation['country']} ({target_geolocation['countryCode']})')
        print(f'[bold]City & State/Region:[/bold] {target_geolocation['city']}, {target_geolocation['regionName']} ({target_geolocation['region']})')
        print(f'[bold]ISP:[/bold] {target_geolocation['isp']}')        
    elif is_public_ip == False:
        console.print(f'[bold]Local/Private IP [red](no geolocation data)[/red][/bold]')
    else:
        console.print(f'[bold red]API Error:[/bold red] Failed to obtain geolocation data.')
    console.print(f'\n[magenta]===[Nmap Port Scan (top 1000 ports)]===[/magenta]', highlight=False)
    # Cycle through the massive Nmap results dictionary to get port, service, and state of each port, since that's all we want
    for host in target_scan_data.all_hosts():
        for proto in target_scan_data[host].all_protocols():
            # Print header text, alongside differentiation between tcp and udp
            console.print(f'[[bold]Protocol:[/bold] {proto}]', highlight=False)
            print(f'{"Port":<5} {"Service":<12} {"State":<10}')
            # Sort results in numerical order
            sorted_ports = sorted(target_scan_data[host][proto].keys())
            # Print results per port
            for port in sorted_ports:
                service = target_scan_data[host][proto][port]['name']
                state = target_scan_data[host][proto][port]['state']
                print(f'{port:<5} {service:<12} {state:<10}')

def export_to_csv(target_geolocation, target_scan_data, is_public_ip, output_file):
    """ Exports collected geolocation and port scanning data to CSV so they can be retrieved and viewed later. """
    try:
        with console.status(f'[bold]Exporting results in CSV-format to {output_file}...') as status:
            with open(output_file, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Target IP:', target_geolocation['query']])
                if is_public_ip == True and 'country' in target_geolocation:
                    writer.writerow(['Country:', target_geolocation['country']])
                    writer.writerow(['Country Code:', target_geolocation['countryCode']])
                    writer.writerow(['City:', target_geolocation['city']])
                    writer.writerow(['State/Region:', target_geolocation['regionName']])
                    writer.writerow(['State/Region Code:', target_geolocation['region']])
                    writer.writerow(['ISP:', target_geolocation['isp']])
                elif is_public_ip == False:
                    writer.writerow(['Local/Private IP (no geolocation data)'])
                else:
                    writer.writerow(['API Error: failed to obtain geolocation data'])
                writer.writerow(['Protocol', 'Port', 'Service', 'State'])
                for host in target_scan_data.all_hosts():
                    for proto in target_scan_data[host].all_protocols():
                        sorted_ports = sorted(target_scan_data[host][proto].keys())
                        for port in sorted_ports:
                            service = target_scan_data[host][proto][port]['name']
                            state = target_scan_data[host][proto][port]['state']
                            writer.writerow([proto, port, service, state])
            console.log(f'\nSuccessfully exported results to CSV at {output_file}.')
    except Exception as e:
        print(f'ERROR: Failed to write CSV file to chosen path/filename (Reason: {e})')
        print('Exiting...')
        sys.exit(1)
        
# Run main() if called directly from cmd, otherwise function as import library
if __name__ == '__main__':
    main()