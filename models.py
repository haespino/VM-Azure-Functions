from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field, validator
import config

class DataDiskConfig(BaseModel):
    """Model for data disk configuration"""
    enabled: bool = Field(default=True, description="Whether to create a data disk")
    size_gb: int = Field(default=200, description="Size of the data disk in GB")
    mount_point: str = Field(default="/opt/sbc_deploy", description="Mount point for the data disk")
    auto_setup_sbc: bool = Field(default=True, description="Whether to automatically setup SBC_DEPLOY")
    
    @validator('size_gb')
    def validate_size_gb(cls, v):
        if v < 1 or v > 32767:
            raise ValueError("Disk size must be between 1 and 32767 GB")
        return v

class VMCreateRequest(BaseModel):
    """Model for VM creation request"""
    name: str = Field(..., description="Name of the VM")
    region: str = Field(..., description="Azure region for the VM")
    size: str = Field(..., description="Size of the VM")
    tags: Optional[Dict[str, str]] = Field(default_factory=dict, description="Tags for the VM")
    data_disk: Optional[DataDiskConfig] = Field(default_factory=DataDiskConfig, description="Data disk configuration")
    
    @validator('region')
    def validate_region(cls, v):
        if v not in config.REGIONS:
            valid_regions = list(config.REGIONS.keys())
            raise ValueError(f"Invalid region. Must be one of: {valid_regions}")
        return v
    
    @validator('size')
    def validate_size(cls, v):
        # Accept both keys (small, medium, etc.) and values (Standard_B2s_v2, etc.)
        if v in config.VM_SIZES:
            return config.VM_SIZES[v]  # Convert key to value
        elif v in config.VM_SIZES.values():
            return v  # Already a valid value
        else:
            valid_sizes = list(config.VM_SIZES.keys()) + list(config.VM_SIZES.values())
            raise ValueError(f"Invalid size. Must be one of: {valid_sizes}")
        return v

# Alias for backward compatibility
VMRequest = VMCreateRequest

class VMUpdateRequest(BaseModel):
    """Model for VM update request"""
    tags: Optional[Dict[str, str]] = Field(default=None, description="Tags for the VM")
    
    class Config:
        extra = "forbid"

class VMResizeRequest(BaseModel):
    """Model for VM resize request"""
    size: str = Field(..., description="New size for the VM")
    
    @validator('size')
    def validate_size(cls, v):
        # Accept both keys (small, medium, etc.) and values (Standard_B2s_v2, etc.)
        if v in config.VM_SIZES:
            return config.VM_SIZES[v]  # Convert key to value
        elif v in config.VM_SIZES.values():
            return v  # Already a valid value
        else:
            valid_sizes = list(config.VM_SIZES.keys()) + list(config.VM_SIZES.values())
            raise ValueError(f"Invalid size. Must be one of: {valid_sizes}")
        return v

class VMResponse(BaseModel):
    """Model for VM response"""
    id: str = Field(..., description="VM ID")
    name: str = Field(..., description="VM name")
    region: str = Field(..., description="VM region")
    size: str = Field(..., description="VM size")
    status: str = Field(..., description="VM status")
    private_ip: Optional[str] = Field(None, description="VM private IP address")
    public_ip: Optional[str] = Field(None, description="VM public IP address")
    created_at: str = Field(..., description="VM creation timestamp")
    updated_at: Optional[str] = Field(None, description="VM update timestamp")
    tags: Dict[str, str] = Field(default_factory=dict, description="VM tags")

class ErrorResponse(BaseModel):
    """Model for error response"""
    error: bool = Field(True, description="Error flag")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Union[str, List[str]]]] = Field(None, description="Error details")

class OperationResponse(BaseModel):
    """Model for operation response"""
    success: bool = Field(..., description="Success flag")
    message: str = Field(..., description="Operation message")
    operation_id: Optional[str] = Field(None, description="Operation ID for async operations")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional operation data")

class SSHKeyResponse(BaseModel):
    """Model for SSH key response"""
    vm_id: str = Field(..., description="VM ID")
    vm_name: str = Field(..., description="VM name")
    private_key: str = Field(..., description="Private SSH key")
    public_key: str = Field(..., description="Public SSH key")
    username: str = Field(..., description="Admin username")
    connection_string: str = Field(..., description="SSH connection string")

class SSHCommandRequest(BaseModel):
    """Model for SSH command request"""
    command: Optional[str] = None
    playbook: Optional[str] = None
    extra_vars: Optional[Dict[str, Any]] = Field(default_factory=dict)

class SSHCommandResponse(BaseModel):
    """Model for SSH command response"""
    success: bool
    message: str
    stdout: str
    stderr: str
    exit_code: int

class PlaybookRequest(BaseModel):
    """Model for playbook execution request"""
    playbook: str
    extra_vars: Optional[Dict[str, Any]] = Field(default_factory=dict)

class VMStatusResponse(BaseModel):
    """Model for VM status response"""
    name: str
    power_state: str
    provisioning_state: str
    statuses: List[Dict[str, Any]] = Field(default_factory=list)

class CreateKyuboVMRequest(BaseModel):
    """Model for Kyubo VM creation request"""
    tenant: str = Field(..., description="Tenant identifier")
    region: str = Field(..., description="Azure region for the VM")
    max_concurrent_sessions: int = Field(..., description="Maximum number of concurrent sessions")
    request_id: str = Field(..., description="Unique request identifier")
    entorno: str = Field(..., description="Environment for the VM (e.g., prod, dev)")

    @validator('region')
    def validate_region(cls, v):
        if v not in config.REGIONS:
            valid_regions = list(config.REGIONS.keys())
            raise ValueError(f"Invalid region. Must be one of: {valid_regions}")
        return v
    
    @validator('max_concurrent_sessions')
    def validate_max_concurrent_sessions(cls, v):
        if v <= 0:
            raise ValueError("max_concurrent_sessions must be greater than 0")
        return v

    @validator('entorno')
    def validate_entorno(cls, v):
        if v not in ['lab', 'dev', 'qa', 'prod']:
            raise ValueError("Invalid entorno. Must be one of: lab, dev, qa, prod")
        return v

class CreateSoloVMRequest(BaseModel):
    """Model for solo VM creation request"""
    cliente: str = Field(..., description="Client identifier")
    entorno: str = Field(..., description="Environment for the VM (e.g., prod, dev)")
    criticidad: str = Field(..., description="Criticality of the VM (e.g., alta, baja)")
    size: str = Field(..., description="VM size")
    region: str = Field(..., description="Azure region for the VM")

    @validator('entorno')
    def validate_entorno(cls, v):
        if v not in ['lab', 'dev', 'qa', 'prod']:
            raise ValueError("Invalid entorno. Must be one of: lab, dev, qa, prod")
        return v

    @validator('criticidad')
    def validate_criticidad(cls, v):
        if v not in ['alta', 'baja', 'desarrollo', 'operacional']:
            raise ValueError("Invalid criticidad. Must be one of: alta, baja, desarrollo, operacional")
        return v

    @validator('region')
    def validate_region(cls, v):
        if v not in config.REGIONS:
            valid_regions = list(config.REGIONS.keys())
            raise ValueError(f"Invalid region. Must be one of: {valid_regions}")
        return v

class KyuboVMResponse(BaseModel):
    """Model for Kyubo VM creation response"""
    id: str = Field(..., description="VM ID")
    status: str = Field(..., description="VM status")

class KyuboCommunicationData(BaseModel):
    """Model for Kyubo communication data"""
    ip_communication: str = Field(..., description="IP address for communication")
    request_id: str = Field(..., description="Original request identifier")