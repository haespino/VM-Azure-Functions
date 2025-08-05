# Azure Configuration
import os
from typing import Dict

# Azure Subscription and Resource Configuration
SUBSCRIPTION_ID = os.getenv('AZURE_SUBSCRIPTION_ID')
RESOURCE_GROUP_PREFIX = 'rg'
KEY_VAULT_NAME = 'key-haec-vm-functions'

# VM Configuration
ADMIN_USERNAME = 'svcadmin'
OS_TYPE = 'Linux'

# Default VM Image - Rocky Linux 9
VM_IMAGE = {
    'publisher': 'erockyenterprisesoftwarefoundationinc1653071250513',
    'offer': 'rockylinux-9',
    'sku': 'rockylinux-9',
    'version': 'latest'
}

# Supported Azure Regions
REGIONS = {
    'eastus': 'East US',
    'westus': 'West US',
    'westus2': 'West US 2',
    'centralus': 'Central US',
    'eastus2': 'East US 2',
    'westeurope': 'West Europe',
    'northeurope': 'North Europe'
}

# VM Sizes Configuration
VM_SIZES = {
    'small': 'Standard_B1s',
    'medium': 'Standard_B2s',
    'large': 'Standard_B4ms',
    'xlarge': 'Standard_D2s_v3',
    'xxlarge': 'Standard_D4s_v3',
    # Direct size specifications
    'Standard_B1s': 'Standard_B1s',
    'Standard_B2s': 'Standard_B2s',
    'Standard_B4ms': 'Standard_B4ms',
    'Standard_D2s_v3': 'Standard_D2s_v3',
    'Standard_D4s_v3': 'Standard_D4s_v3'
}

# Network Configuration
VNET_ADDRESS_PREFIX = '10.0.0.0/16'
SUBNET_ADDRESS_PREFIX = '10.0.0.0/24'

# Security Configuration
ALLOWED_SSH_SOURCES = ['*']  # In production, restrict this
ALLOWED_HTTP_SOURCES = ['*']  # In production, restrict this

# Storage Configuration
OS_DISK_SIZE_GB = 30
OS_DISK_TYPE = 'Standard_LRS'
DATA_DISK_TYPE = 'Standard_LRS'

# Kyubo VM Configuration
KYUBO_VM_SIZE_MAPPING = {
    25: 'Standard_B2s',
    50: 'Standard_B4ms',
    75: 'Standard_D2s_v3',
    100: 'Standard_D4s_v3'
}

# Environment Configuration
VALID_ENVIRONMENTS = ['lab', 'dev', 'qa', 'prod']
VALID_CRITICALITY = ['alta', 'baja', 'desarrollo', 'operacional']

# API Configuration
API_VERSION = '1.0.0'
API_TITLE = 'VM Management API'
API_DESCRIPTION = 'Azure VM Management System with SSH Key Management'

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
APPLICATION_INSIGHTS_KEY = os.getenv('APPINSIGHTS_INSTRUMENTATIONKEY')

# Cosmos DB Configuration (if used)
COSMOS_DB_ENDPOINT = os.getenv('COSMOS_DB_ENDPOINT')
COSMOS_DB_KEY = os.getenv('COSMOS_DB_KEY')
COSMOS_DB_DATABASE = 'vm_management'
COSMOS_DB_CONTAINER = 'vms'

# Table Storage Configuration
STORAGE_ACCOUNT_NAME = os.getenv('AZURE_STORAGE_ACCOUNT_NAME')
STORAGE_ACCOUNT_KEY = os.getenv('AZURE_STORAGE_ACCOUNT_KEY')
STORAGE_TABLE_NAME = 'vmmanagement'

# SSH Configuration
SSH_KEY_TYPE = 'rsa'
SSH_KEY_SIZE = 2048
SSH_KEY_FORMAT = 'OpenSSH'

# Default Tags
DEFAULT_TAGS = {
    'CreatedBy': 'VM-Management-System',
    'Environment': 'Development',
    'Project': 'VM-Management'
}

# Timeout Configuration (in seconds)
VM_OPERATION_TIMEOUT = 600  # 10 minutes
SSH_CONNECTION_TIMEOUT = 30
AZURE_OPERATION_TIMEOUT = 300  # 5 minutes

# Rate Limiting
RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_WINDOW = 3600  # 1 hour

# Feature Flags
ENABLE_SSH_KEY_MANAGEMENT = True
ENABLE_DATA_DISK_AUTO_MOUNT = True
ENABLE_MONITORING = True
ENABLE_BACKUP = False

# Monitoring Configuration
MONITORING_METRICS = [
    'vm_creation_count',
    'vm_deletion_count',
    'ssh_key_generation_count',
    'api_request_count',
    'error_count'
]

# Backup Configuration
BACKUP_RETENTION_DAYS = 30
BACKUP_FREQUENCY = 'daily'

# Health Check Configuration
HEALTH_CHECK_ENDPOINTS = [
    'azure_compute',
    'azure_keyvault',
    'azure_storage'
]