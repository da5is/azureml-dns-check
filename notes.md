## Notes on Azure ML Configuration

- Azure Container Registry: `az resource show -n aml-private -g rg-azureml-private --resource-type Microsoft.MachineLearningServices/workspaces --query properties.containerRegistry`
    - `az resource show -n acrowamlprivate -g rg-azureml-private --resource-type Microsoft.ContainerRegistry/registries`
        -   "properties": {
        "adminUserEnabled": false,
        "anonymousPullEnabled": false,
        "creationDate": "2023-02-19T15:34:03.3962603Z",
        "dataEndpointEnabled": false,
        "dataEndpointHostNames": [
        "acrowamlprivate.eastus.data.azurecr.io"
        ],
        "encryption": {
        "status": "disabled"
        },
        "loginServer": "acrowamlprivate.azurecr.io",
        "networkRuleBypassOptions": "AzureServices",
        "networkRuleSet": {
        "defaultAction": "Allow",
        "ipRules": []
        }, 





- Keyvault `az resource show -n aml-private -g rg-azureml-private --resource-type Microsoft.MachineLearningServices/workspaces --query properties.keyVault`
- Storage Account:  `az resource show -n aml-private -g rg-azureml-private --resource-type Microsoft.MachineLearningServices/workspaces --query properties.storageAccount`
