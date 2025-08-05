# Gestión de Claves SSH - VM Management System

## 📋 Resumen

Este documento describe la gestión automática de claves SSH para las VMs creadas a través del sistema VM Management. El sistema genera automáticamente pares de claves SSH únicos para cada VM y los almacena de forma segura en Azure Key Vault.

## 🔑 Configuración de SSH

### Especificaciones Técnicas

- **Tipo de Clave:** RSA 2048 bits
- **Formato:** OpenSSH/PEM compatible
- **Usuario por defecto:** `svcadmin`
- **Autenticación:** Solo SSH (sin contraseña)
- **Sistema Operativo:** Rocky Linux 9

### Almacenamiento Seguro

**Azure Key Vault:** `key-haec-vm-functions`

**Nomenclatura de secretos:**
```
ssh-key-{resource_group}-{vm_name}
```

**Ejemplos:**
- `ssh-key-rg-eastus-test-vm-001`
- `ssh-key-rg-westus-kyubo-vm-002`
- `ssh-key-rg-centralus-prod-vm-003`

## 🔄 Flujo de Creación de VM

### 1. Generación de Claves

Cuando se crea una nueva VM, el sistema:

1. **Genera** un par de claves SSH único
2. **Almacena** la clave privada en Azure Key Vault
3. **Configura** la clave pública en la VM
4. **Retorna** información de conexión

### 2. Proceso Automático

```python
# Flujo interno del sistema
def create_vm_with_ssh():
    # 1. Generar par de claves
    private_key, public_key = generate_ssh_key_pair()
    
    # 2. Almacenar clave privada
    key_name = f"ssh-key-{resource_group}-{vm_name}"
    store_ssh_key_in_vault(key_name, private_key)
    
    # 3. Configurar VM con clave pública
    vm_config['os_profile']['linux_configuration'] = {
        'ssh': {
            'public_keys': [{
                'path': f'/home/{admin_username}/.ssh/authorized_keys',
                'key_data': public_key
            }]
        }
    }
    
    # 4. Crear VM
    vm_result = compute_client.virtual_machines.begin_create_or_update(...)
    
    return vm_info_with_ssh_details
```

## 🛠️ Funciones Principales

### `generate_ssh_key_pair()`

**Propósito:** Genera un par de claves SSH RSA 2048 bits

**Retorna:**
- `private_key`: Clave privada en formato PEM
- `public_key`: Clave pública en formato OpenSSH

**Implementación:**
```python
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

def generate_ssh_key_pair():
    # Generar clave privada RSA 2048 bits
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    
    # Serializar clave privada
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.OpenSSH,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    # Obtener clave pública
    public_key = private_key.public_key()
    public_ssh = public_key.public_bytes(
        encoding=serialization.Encoding.OpenSSH,
        format=serialization.PublicFormat.OpenSSH
    )
    
    return private_pem.decode(), public_ssh.decode()
```

### `store_ssh_key_in_vault()`

**Propósito:** Almacena la clave privada en Azure Key Vault

**Parámetros:**
- `key_name`: Nombre del secreto en Key Vault
- `private_key`: Clave privada a almacenar

**Implementación:**
```python
from azure.keyvault.secrets import SecretClient

def store_ssh_key_in_vault(key_name, private_key):
    secret_client = SecretClient(
        vault_url=f"https://{key_vault_name}.vault.azure.net/",
        credential=credential
    )
    
    secret_client.set_secret(key_name, private_key)
    return True
```

### `get_ssh_key_from_vault()`

**Propósito:** Recupera la clave privada desde Azure Key Vault

**Parámetros:**
- `key_name`: Nombre del secreto en Key Vault

**Retorna:** Clave privada en formato PEM

**Implementación:**
```python
def get_ssh_key_from_vault(key_name):
    secret_client = SecretClient(
        vault_url=f"https://{key_vault_name}.vault.azure.net/",
        credential=credential
    )
    
    secret = secret_client.get_secret(key_name)
    return secret.value
```

## 📤 Estructura de Respuesta

### Respuesta de Creación de VM

Cuando se crea una VM exitosamente, la respuesta incluye información sobre las claves SSH:

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
    "vm_id_for_key_retrieval": "rg-eastus-test-vm-001",
    "key_vault_secret_name": "ssh-key-rg-eastus-test-vm-001"
  },
  "connection_info": {
    "ssh_command": "ssh -i <private_key_file> svcadmin@20.123.45.67",
    "key_retrieval_command": "az keyvault secret show --vault-name key-haec-vm-functions --name ssh-key-rg-eastus-test-vm-001 --query value -o tsv"
  }
}
```

## 🔐 Conexión SSH

### Paso 1: Recuperar Clave Privada

```bash
# Usando Azure CLI
az keyvault secret show \
  --vault-name key-haec-vm-functions \
  --name ssh-key-rg-eastus-test-vm-001 \
  --query value -o tsv > private_key.pem

# Configurar permisos
chmod 600 private_key.pem
```

### Paso 2: Conectar a la VM

```bash
# Conexión SSH
ssh -i private_key.pem svcadmin@20.123.45.67

# Con opciones adicionales
ssh -i private_key.pem -o StrictHostKeyChecking=no svcadmin@20.123.45.67
```

### Script de Conexión Automática

```bash
#!/bin/bash
# connect_vm.sh - Script para conexión automática

VM_ID="$1"
PUBLIC_IP="$2"
KEY_VAULT="key-haec-vm-functions"

if [ -z "$VM_ID" ] || [ -z "$PUBLIC_IP" ]; then
    echo "Uso: $0 <vm_id> <public_ip>"
    echo "Ejemplo: $0 rg-eastus-test-vm-001 20.123.45.67"
    exit 1
fi

echo "🔑 Recuperando clave SSH..."
az keyvault secret show \
  --vault-name $KEY_VAULT \
  --name ssh-key-$VM_ID \
  --query value -o tsv > /tmp/vm_key.pem

chmod 600 /tmp/vm_key.pem

echo "🚀 Conectando a VM $VM_ID..."
ssh -i /tmp/vm_key.pem -o StrictHostKeyChecking=no svcadmin@$PUBLIC_IP

# Limpiar clave temporal
rm -f /tmp/vm_key.pem
echo "🧹 Clave temporal eliminada"
```

## 🔒 Seguridad

### Mejores Prácticas

1. **Rotación de Claves**
   - Las claves se generan únicamente para cada VM
   - No se reutilizan claves entre VMs
   - Eliminación automática al eliminar la VM

2. **Acceso Controlado**
   - Solo usuarios autorizados pueden acceder a Key Vault
   - Logs de auditoría para acceso a claves
   - Políticas de acceso basadas en RBAC

3. **Almacenamiento Seguro**
   - Claves privadas nunca se exponen en logs
   - Almacenamiento cifrado en Key Vault
   - Acceso solo a través de Azure SDK

### Permisos Requeridos

**Para el sistema:**
- `Key Vault Secrets Officer` en Key Vault
- `Virtual Machine Contributor` en Resource Group

**Para usuarios:**
- `Key Vault Secrets User` para recuperar claves
- `Reader` en Resource Group para ver VMs

## 🔧 Troubleshooting

### Problemas Comunes

#### 1. Error al recuperar clave
```bash
# Verificar permisos
az keyvault show --name key-haec-vm-functions

# Listar secretos
az keyvault secret list --vault-name key-haec-vm-functions
```

#### 2. Conexión SSH rechazada
```bash
# Verificar permisos de archivo
ls -la private_key.pem
# Debe mostrar: -rw------- (600)

# Verificar formato de clave
file private_key.pem
# Debe mostrar: PEM RSA private key
```

#### 3. VM no accesible
```bash
# Verificar estado de VM
az vm show --name test-vm-001 --resource-group rg-eastus --query powerState

# Verificar IP pública
az vm show --name test-vm-001 --resource-group rg-eastus --show-details --query publicIps
```

## 📊 Monitoreo

### Métricas Importantes

- **Claves generadas:** Contador de pares de claves creados
- **Accesos a Key Vault:** Logs de recuperación de claves
- **Conexiones SSH:** Logs de autenticación exitosa
- **Errores de conexión:** Fallos de autenticación SSH

### Logs de Auditoría

```bash
# Ver logs de Key Vault
az monitor activity-log list \
  --resource-group rg-eastus \
  --resource-type Microsoft.KeyVault/vaults

# Ver logs de VM
az monitor activity-log list \
  --resource-group rg-eastus \
  --resource-type Microsoft.Compute/virtualMachines
```

---

**Última actualización:** 5 de Agosto de 2025  
**Estado:** ✅ Implementado y funcionando  
**Versión:** 1.0