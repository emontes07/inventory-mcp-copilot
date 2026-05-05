@description('Base name for Azure resources')
param appName string = 'inventory-iq-mcp'

@description('Azure location for the deployment')
param location string = resourceGroup().location

@description('Container image to deploy')
param containerImage string = 'REPLACE_WITH_IMAGE'

@description('Target port for the MCP container')
param targetPort int = 8000

resource environment 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: '${appName}-env'
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: 'REPLACE_ME'
        sharedKey: 'REPLACE_ME'
      }
    }
  }
}

resource containerApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: appName
  location: location
  properties: {
    managedEnvironmentId: environment.id
    configuration: {
      ingress: {
        external: true
        targetPort: targetPort
        transport: 'http'
      }
      activeRevisionsMode: 'Single'
    }
    template: {
      containers: [
        {
          name: 'inventory-mcp'
          image: containerImage
          env: [
            {
              name: 'MCP_TRANSPORT'
              value: 'streamable-http'
            }
            {
              name: 'PORT'
              value: string(targetPort)
            }
          ]
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 2
      }
    }
  }
}

output containerAppUrl string = 'https://${containerApp.properties.configuration.ingress.fqdn}'
