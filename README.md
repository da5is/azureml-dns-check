# AzureML DNS Check

## Synopsis

This Python script queries an AzureML resource to determine the storage account, the KeyVault, and the Azure Container Registry associated to the resource.  It then generates the DNS names associated with each of the resources and resolves them via DNS to determine if they are being resolved as public addresses (Internet-facing) or private addresses (Private Endpoint implementations).  Finally, it will output a series of nslookup commands that can be copied and pasted into terminals on machines that may be having trouble accesses the AzureML resource.

## Requirements

This has been tested on Python 3.9.13 with the following modules:
* azure-cli
* tabulate
* argparse

## Example Usage

`python check-dns-configuration.py -s SUBSCRIPTIONGUID -g RESOURCEGROUPNAME -n AZUREMLRESOURCENAME`

## Screenshots

### Public Deployment

<img width="1089" alt="image" src="https://github.com/da5is/azureml-dns-check/assets/5679212/f2e7524e-7d3f-4f81-a856-74fd66977765">

### Private Deployment

<img width="696" alt="image" src="https://github.com/da5is/azureml-dns-check/assets/5679212/e9231f59-d2d9-4fcf-b5d0-885b75d97417">
