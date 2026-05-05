#!/usr/bin/env bash

set -euo pipefail

RESOURCE_GROUP="${RESOURCE_GROUP:-inventory-iq-rg}"
LOCATION="${LOCATION:-eastus}"
CONTAINER_IMAGE="${CONTAINER_IMAGE:-REPLACE_WITH_IMAGE}"

echo "Creating resource group: ${RESOURCE_GROUP}"
az group create --name "${RESOURCE_GROUP}" --location "${LOCATION}"

echo "Deploying Azure Container Apps scaffold"
az deployment group create \
  --resource-group "${RESOURCE_GROUP}" \
  --template-file infra/azure-container-app.bicep \
  --parameters appName=inventory-iq-mcp location="${LOCATION}" containerImage="${CONTAINER_IMAGE}"

echo "Deployment request submitted. Update placeholders before production use."
