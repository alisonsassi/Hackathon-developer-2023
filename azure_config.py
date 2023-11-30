# azure_config.py
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication

class AzureConfig:
    org_url = 'YOUR_URL_ORGANIZATION_OF_AZURE'
    token = 'YOUR_TOKEN_OF_AZURE'
    project_id = 'PROJECT_OF_AZURE'

# org_url = 'https://dev.azure.com/Defects'
# project_id = 'DefectsDoubtsAgile'


def get_azure_devops_connection():
    personal_access_token = AzureConfig.token
    organization_url = AzureConfig.org_url
    credentials = BasicAuthentication('', personal_access_token)
    connection = Connection(base_url=organization_url, creds=credentials)
    return connection
class OpenIA:
    api_key = "YOUR_TOKEN_OF_OPENAI"