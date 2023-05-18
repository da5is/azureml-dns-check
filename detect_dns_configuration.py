from azure.cli.core import get_default_cli
from urllib.parse import urlparse
import argparse
import socket
import re

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

def check_dns_resolution(dns_list):
    regex = r'(?:(?:192\.)(?:(?:168\.)(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?\.)(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)))|(?:(?:10\.)(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){2}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))|(?:(?:172\.)(?:(?:1[6-9]|2[0-9]|3[0-1])\.)(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.)(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))'
    for host in dns_list:
        ip = repr(socket.gethostbyname(host))
        ip = ip.replace("'", "")
        if re.match(regex, ip):
            print(f'{host} resolves to {ip} and is PRIVATE.')
        else:
            print(f'{host} resolves to {ip} and is PUBLIC.')


def print_nslookup_commands(dns_list):
    print('To check this from a workstation to validate resolution, please copy the following commands to paste into a terminal.\n')
    for host in dns_list:
        print(f'nslookup {host}')

dns_list = []
parser = argparse.ArgumentParser()
parser.add_argument('-s', '--subscription', required=True, help='The subscription GUID the AzureML Instance is in')
parser.add_argument('-g', '--resourcegroup', required=True, help='The resource group the AzureML Instance is in')
parser.add_argument('-n', '--name', required=True, help='The name of the AzureML Instance')
args = parser.parse_args()
existing_subscription = az_cli(f'account show --query id')
az_cli(f'account set --subscription {args.subscription}')

output = az_cli(f'resource show -n {args.name} -g {args.resourcegroup} \
    --resource-type Microsoft.MachineLearningServices/workspaces --query properties.notebookInfo.fqdn')
dns_list = [f'{output}']
output = az_cli(f'resource show -n {args.name} -g {args.resourcegroup} \
    --resource-type Microsoft.MachineLearningServices/workspaces --query properties.discoveryUrl')
dns_list += [f'{urlparse(output).hostname}']

output = az_cli(f'resource show -n {args.name} -g {args.resourcegroup} \
                --resource-type Microsoft.MachineLearningServices/workspaces --query properties.containerRegistry')
dns_list += generate_hostname(args, output, 'acr')
output = az_cli(f'resource show -n {args.name} -g {args.resourcegroup} \
                --resource-type Microsoft.MachineLearningServices/workspaces --query properties.keyVault')
dns_list += generate_hostname(args, output, 'kv')
output = az_cli(f'resource show -n {args.name} -g {args.resourcegroup} \
                --resource-type Microsoft.MachineLearningServices/workspaces --query properties.storageAccount')
dns_list += generate_hostname(args, output, 'sa')
print('------------')
check_dns_resolution(dns_list)
print('------------')
print_nslookup_commands(dns_list)
az_cli(f'account set --subscription {existing_subscription}')

