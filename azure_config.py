# azure_config.py
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication

class AzureConfig:
    org_url = 'https://dev.azure.com/Defects'
    token = '6gjcv6otnnav3nmxz5tzacn3boefw65aacnzpk5yelanxkth4b5a'
    project_id = 'DefectsDoubtsAgile'


def get_azure_devops_connection():
    personal_access_token = AzureConfig.token
    organization_url = AzureConfig.org_url
    credentials = BasicAuthentication('', personal_access_token)
    connection = Connection(base_url=organization_url, creds=credentials)
    return connection
class OpenIA:
    api_key = "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"