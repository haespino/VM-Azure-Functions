# Documentación de Endpoints - VM Management System

## 📋 Información General

**Base URL:** `http://localhost:7071/api`  
**Autenticación:** API Key (Header: `x-api-key`)  
**Formato:** JSON  
**Sistema Operativo por defecto:** Rocky Linux 9  
**Usuario SSH:** svcadmin

## 🔐 Autenticación

Todos los endpoints requieren autenticación mediante API Key:

```http
Headers:
x-api-key: your-api-key-here
Content-Type: application/json
```

## 📡 Endpoints Disponibles

### 1. Health Check

**Endpoint:** `GET /HealthCheck`  
**Descripción:** Verifica el estado del servicio

**Request:**
```http
GET /api/HealthCheck
Headers:
  x-api-key: your-api-key-here
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-05T20:23:00Z",
  "version": "1.0.0"
}
```

### 2. Crear VM Estándar

**Endpoint:** `POST /vms`  
**Descripción:** Crea una nueva máquina virtual estándar

**Request:**
```http
POST /api/vms
Headers:
  Content-Type: application/json
  x-api-key: your-api-key-here

Body:
{
  "name": "test-vm-001",
  "region": "eastus",
  "size": "Standard_B2s",
  "tags": {
    "Environment": "Development",
    "Project": "VM-Management"
  },
  "data_disk": {
    "enabled": true,
    "size_gb": 100,
    "mount_point": "/opt/data",
    "auto_setup_sbc": false
  }
}
```

**Response:**
```json
{
  "status": "success",
  "vm_name": "test-vm-001",
  "resource_group": "rg-eastus",
  "public_ip": "20.123.45.67",
  "admin_username": "svcadmin",
  "ssh_key_info": {
    "ssh_key_generated": true,
    "ssh_key_stored_in_vault": true,
    "vm_id_for_key_retrieval": "rg-eastus-test-vm-001"
  },
  "connection_info": {
    "ssh_command": "ssh -i <private_key_file> svcadmin@20.123.45.67"
  }
}
```

### 3. Crear VM Kyubo

**Endpoint:** `POST /kyubo/vms`  
**Descripción:** Crea una VM especializada para Kyubo SBC

**Request:**
```http
POST /api/kyubo/vms
Headers:
  Content-Type: application/json
  x-api-key: your-api-key-here

Body:
{
  "tenant": "sbc",
  "region": "eastus",
  "max_concurrent_sessions": 50,
  "request_id": "req-12345",
  "entorno": "dev"
}
```

**Response:**
```json
{
  "status": "success",
  "vm_name": "dc-kyubo-test-351-sbc-dev-operacional-2025-req-12345",
  "resource_group": "rg-eastus",
  "public_ip": "20.234.56.78",
  "admin_username": "svcadmin",
  "ssh_key_info": {
    "ssh_key_generated": true,
    "ssh_key_stored_in_vault": true,
    "vm_id_for_key_retrieval": "rg-eastus-dc-kyubo-test-351-sbc-dev-operacional-2025-req-12345"
  },
  "sbc_config": {
    "mount_point": "/opt/sbc_deploy",
    "max_sessions": 50,
    "auto_setup_completed": true
  }
}
```

### 4. Listar VMs

**Endpoint:** `GET /vms`  
**Descripción:** Lista todas las máquinas virtuales

**Request:**
```http
GET /api/vms
Headers:
  x-api-key: your-api-key-here
```

**Response:**
```json
{
  "status": "success",
  "vms": [
    {
      "name": "test-vm-001",
      "resource_group": "rg-eastus",
      "status": "running",
      "public_ip": "20.123.45.67",
      "size": "Standard_B2s",
      "region": "eastus"
    },
    {
      "name": "dc-kyubo-test-351",
      "resource_group": "rg-eastus",
      "status": "running",
      "public_ip": "20.234.56.78",
      "size": "Standard_B4ms",
      "region": "eastus"
    }
  ],
  "total_count": 2
}
```

### 5. Obtener VM Específica

**Endpoint:** `GET /vms/{vm_name}`  
**Descripción:** Obtiene información detallada de una VM específica

**Request:**
```http
GET /api/vms/test-vm-001
Headers:
  x-api-key: your-api-key-here
```

**Response:**
```json
{
  "status": "success",
  "vm_info": {
    "name": "test-vm-001",
    "resource_group": "rg-eastus",
    "status": "running",
    "public_ip": "20.123.45.67",
    "private_ip": "10.0.0.4",
    "size": "Standard_B2s",
    "region": "eastus",
    "os_type": "Linux",
    "os_version": "Rocky Linux 9",
    "admin_username": "svcadmin",
    "created_time": "2025-08-05T20:15:00Z",
    "tags": {
      "Environment": "Development",
      "Project": "VM-Management"
    }
  }
}
```

### 6. Iniciar VM

**Endpoint:** `POST /vms/{vm_name}/start`  
**Descripción:** Inicia una máquina virtual detenida

**Request:**
```http
POST /api/vms/test-vm-001/start
Headers:
  x-api-key: your-api-key-here
```

**Response:**
```json
{
  "status": "success",
  "message": "VM test-vm-001 iniciada exitosamente",
  "vm_status": "starting"
}
```

### 7. Detener VM

**Endpoint:** `POST /vms/{vm_name}/stop`  
**Descripción:** Detiene una máquina virtual en ejecución

**Request:**
```http
POST /api/vms/test-vm-001/stop
Headers:
  x-api-key: your-api-key-here
```

**Response:**
```json
{
  "status": "success",
  "message": "VM test-vm-001 detenida exitosamente",
  "vm_status": "stopping"
}
```

### 8. Reiniciar VM

**Endpoint:** `POST /vms/{vm_name}/restart`  
**Descripción:** Reinicia una máquina virtual

**Request:**
```http
POST /api/vms/test-vm-001/restart
Headers:
  x-api-key: your-api-key-here
```

**Response:**
```json
{
  "status": "success",
  "message": "VM test-vm-001 reiniciada exitosamente",
  "vm_status": "restarting"
}
```

### 9. Redimensionar VM

**Endpoint:** `PUT /vms/{vm_name}/resize`  
**Descripción:** Cambia el tamaño de una máquina virtual

**Request:**
```http
PUT /api/vms/test-vm-001/resize
Headers:
  Content-Type: application/json
  x-api-key: your-api-key-here

Body:
{
  "new_size": "Standard_B4ms"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "VM test-vm-001 redimensionada exitosamente",
  "old_size": "Standard_B2s",
  "new_size": "Standard_B4ms"
}
```

### 10. Actualizar VM

**Endpoint:** `PUT /vms/{vm_name}`  
**Descripción:** Actualiza las etiquetas de una máquina virtual

**Request:**
```http
PUT /api/vms/test-vm-001
Headers:
  Content-Type: application/json
  x-api-key: your-api-key-here

Body:
{
  "tags": {
    "Environment": "Production",
    "Project": "VM-Management",
    "Owner": "DevOps"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "VM test-vm-001 actualizada exitosamente",
  "updated_tags": {
    "Environment": "Production",
    "Project": "VM-Management",
    "Owner": "DevOps"
  }
}
```

### 11. Eliminar VM

**Endpoint:** `DELETE /vms/{vm_name}`  
**Descripción:** Elimina una máquina virtual y todos sus recursos asociados

**Request:**
```http
DELETE /api/vms/test-vm-001
Headers:
  x-api-key: your-api-key-here
```

**Response:**
```json
{
  "status": "success",
  "message": "VM test-vm-001 eliminada exitosamente",
  "deleted_resources": [
    "Virtual Machine",
    "Network Interface",
    "Public IP",
    "OS Disk",
    "SSH Key from Key Vault"
  ]
}
```

### 12. Obtener Clave SSH

**Endpoint:** `GET /vms/{vm_name}/ssh-key`  
**Descripción:** Recupera la clave SSH privada para conexión a la VM

**Request:**
```http
GET /api/vms/test-vm-001/ssh-key
Headers:
  x-api-key: your-api-key-here
```

**Response:**
```json
{
  "status": "success",
  "ssh_key_info": {
    "vm_name": "test-vm-001",
    "key_vault_name": "key-haec-vm-functions",
    "secret_name": "ssh-key-rg-eastus-test-vm-001",
    "public_ip": "20.123.45.67",
    "admin_username": "svcadmin"
  },
  "connection_commands": {
    "retrieve_key": "az keyvault secret show --vault-name key-haec-vm-functions --name ssh-key-rg-eastus-test-vm-001 --query value -o tsv > private_key.pem",
    "set_permissions": "chmod 600 private_key.pem",
    "ssh_connect": "ssh -i private_key.pem svcadmin@20.123.45.67"
  }
}
```

## 📊 Parámetros de Configuración

### Regiones Soportadas

- `eastus` - East US
- `westus` - West US
- `westus2` - West US 2
- `centralus` - Central US
- `eastus2` - East US 2
- `westeurope` - West Europe
- `northeurope` - North Europe

### Tamaños de VM Soportados

| Tamaño | vCPUs | RAM | Uso Recomendado |
|--------|-------|-----|------------------|
| `Standard_B1s` | 1 | 1 GB | Desarrollo/Testing |
| `Standard_B2s` | 2 | 4 GB | Aplicaciones ligeras |
| `Standard_B4ms` | 4 | 16 GB | Aplicaciones medianas |
| `Standard_D2s_v3` | 2 | 8 GB | Propósito general |
| `Standard_D4s_v3` | 4 | 16 GB | Aplicaciones intensivas |

### Configuración de Disco de Datos

```json
{
  "data_disk": {
    "enabled": true,           // Habilitar disco de datos
    "size_gb": 100,           // Tamaño en GB (32-1023)
    "mount_point": "/opt/data", // Punto de montaje
    "auto_setup_sbc": false    // Configuración automática SBC
  }
}
```

## ⚠️ Códigos de Error

### Errores de Autenticación

- **401 Unauthorized:** API Key inválida o faltante
- **403 Forbidden:** Permisos insuficientes

### Errores de Validación

- **400 Bad Request:** Parámetros inválidos o faltantes
- **422 Unprocessable Entity:** Error de validación Pydantic

### Errores de Recursos

- **404 Not Found:** VM no encontrada
- **409 Conflict:** Recurso ya existe
- **429 Too Many Requests:** Límite de rate excedido

### Errores del Servidor

- **500 Internal Server Error:** Error interno del servidor
- **503 Service Unavailable:** Servicio temporalmente no disponible

## 📝 Ejemplos de Uso

### Crear VM de Desarrollo

```bash
curl -X POST http://localhost:7071/api/vms \
  -H "Content-Type: application/json" \
  -H "x-api-key: your-api-key" \
  -d '{
    "name": "dev-vm-001",
    "region": "eastus",
    "size": "Standard_B2s",
    "tags": {
      "Environment": "Development",
      "Project": "MyApp"
    }
  }'
```

### Crear VM Kyubo para Producción

```bash
curl -X POST http://localhost:7071/api/kyubo/vms \
  -H "Content-Type: application/json" \
  -H "x-api-key: your-api-key" \
  -d '{
    "tenant": "sbc",
    "region": "eastus",
    "max_concurrent_sessions": 100,
    "request_id": "prod-req-001",
    "entorno": "prod"
  }'
```

### Conectar por SSH

```bash
# 1. Recuperar clave SSH
az keyvault secret show \
  --vault-name key-haec-vm-functions \
  --name ssh-key-rg-eastus-dev-vm-001 \
  --query value -o tsv > dev_vm_key.pem

# 2. Configurar permisos
chmod 600 dev_vm_key.pem

# 3. Conectar
ssh -i dev_vm_key.pem svcadmin@20.123.45.67
```

---

**Última actualización:** 5 de Agosto de 2025  
**Estado:** ✅ Todos los endpoints operativos  
**Versión API:** 1.0