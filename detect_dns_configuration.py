from azure.cli.core import get_default_cli 
from urllib.parse import urlparse
import argparse
import socket
import re
from tabulate import tabulate

def az_cli (args_str):
    args = args_str.split()
    cli = get_default_cli()
    cli.invoke(args)
    if cli.result.result:
        return cli.result.result
    elif cli.result.error:
        raise cli.result.error
    return True 

def generate_hostname(args, property, type):
    resource_name = property.rsplit('/', 1)[-1]
    if type == 'acr':
        endpoints = []
        endpoints = az_cli(f'resource show -n {resource_name} -g {args.resourcegroup} --resource-type Microsoft.ContainerRegistry/registries --query properties.dataEndpointHostNames')
        endpoints += [az_cli(f'resource show -n {resource_name} -g {args.resourcegroup} --resource-type Microsoft.ContainerRegistry/registries --query properties.loginServer')]
        return(endpoints)
    if type == 'kv':
        return([f'{resource_name}.vault.azure.net'])
    if type == 'sa':
        return([f'{resource_name}.blob.core.windows.net', f'{resource_name}.file.core.windows.net'])
    if type == 'nb':
        return([property])
    if type == 'url':
        return([urlparse(property).hostname])
    
def check_dns_resolution(dns_list):
    dns_status = []
    regex = r'(?:(?:192\.)(?:(?:168\.)(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?\.)(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)))|(?:(?:10\.)(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){2}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))|(?:(?:172\.)(?:(?:1[6-9]|2[0-9]|3[0-1])\.)(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.)(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))'
    for host in dns_list:
        try:
            ip = repr(socket.gethostbyname(host))
            ip = ip.replace("'", '')
            if re.match(regex, ip):
                dns_status += [[host, ip, 'private']]
            else:
                dns_status += [[host, ip, 'public']]
        except:
            dns_status += [[host, 'FAIL', 'FAIL']]
    return(dns_status)

def get_aml_properties(name, resourcegroup, property):
    response = az_cli(f'resource show -n {name} -g {resourcegroup} \
        --resource-type Microsoft.MachineLearningServices/workspaces --query properties.{property}')
    return(response)

def print_nslookup_commands(dns_list):
    print('\nTo check this from a machine without python to validate resolution, please copy the following commands to paste into a terminal.\n')
    for host in dns_list:
        print(f'nslookup {host}')

def main(argv):
    dns_list = []
    aml_properties = [
        ('notebookInfo.fqdn', 'nb'),
        ('discoveryUrl', 'url'),
        ('containerRegistry', 'acr'),
        ('keyVault', 'kv'), 
        ('storageAccount', 'sa')
    ]
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--subscription', required=True, help='The subscription GUID the AzureML Instance is in')
    parser.add_argument('-g', '--resourcegroup', required=True, help='The resource group the AzureML Instance is in')
    parser.add_argument('-n', '--name', required=True, help='The name of the AzureML Instance')
    args = parser.parse_args()
    existing_subscription = az_cli(f'account show --query id')
    az_cli(f'account set --subscription {args.subscription}')
    for property, type in aml_properties:
        returned_property = get_aml_properties(args.name, args.resourcegroup, property)
        dns_list += generate_hostname(args, returned_property, type)
    print(tabulate(check_dns_resolution(dns_list), tablefmt="psql"))
    print_nslookup_commands(dns_list)
    az_cli(f'account set --subscription {existing_subscription}')

if __name__ == '__main__':
    import sys
    main(sys.argv)