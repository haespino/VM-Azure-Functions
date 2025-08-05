# VM Azure Functions - Sistema de Gestión de VMs

## 📋 Descripción

Sistema completo de gestión de máquinas virtuales en Azure utilizando Azure Functions, con validación Pydantic corregida y gestión automática de claves SSH.

## ✅ Estado Actual

- **Validación Pydantic:** ✅ Corregida y funcionando
- **Endpoints:** ✅ POST /api/vms y POST /api/kyubo/vms operativos
- **Sistema Operativo:** Rocky Linux 9 (por defecto)
- **Autenticación SSH:** Automática con Azure Key Vault
- **API Key:** Configurada y funcionando

## 🔧 Características Principales

### Endpoints Disponibles

1. **POST /api/vms** - Creación de VMs estándar
2. **POST /api/kyubo/vms** - Creación de VMs Kyubo especializadas
3. **GET /api/vms** - Listar todas las VMs
4. **GET /api/vms/{vm_name}** - Obtener información de una VM específica
5. **POST /api/vms/{vm_name}/start** - Iniciar VM
6. **POST /api/vms/{vm_name}/stop** - Detener VM
7. **POST /api/vms/{vm_name}/restart** - Reiniciar VM
8. **PUT /api/vms/{vm_name}/resize** - Redimensionar VM
9. **PUT /api/vms/{vm_name}** - Actualizar VM
10. **DELETE /api/vms/{vm_name}** - Eliminar VM
11. **GET /api/vms/{vm_name}/ssh-key** - Obtener clave SSH

### Gestión Automática de SSH

- **Generación automática** de pares de claves RSA 2048 bits
- **Almacenamiento seguro** en Azure Key Vault
- **Usuario por defecto:** svcadmin
- **Autenticación:** Solo SSH (sin contraseña)

### Configuración de Discos de Datos

- **Montaje automático** en `/opt/sbc_deploy` (para VMs Kyubo)
- **Configuración SBC** automática
- **Tamaños personalizables** de disco

## 🚀 Inicio Rápido

### Prerrequisitos

- Azure CLI configurado
- Python 3.9+
- Azure Functions Core Tools

### Instalación

```bash
# Clonar repositorio
git clone https://github.com/haespino/VM-Azure-Functions.git
cd VM-Azure-Functions

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp app-settings.json.example app-settings.json
# Editar app-settings.json con tus credenciales

# Iniciar servidor local
func start --host 0.0.0.0 --port 7071
```

### Configuración de Postman

1. Importar `VM_Management_Collection.json`
2. Configurar variables de entorno:
   - `base_url`: http://localhost:7071/api
   - `api_key`: tu-api-key-aquí

## 📝 Ejemplos de Uso

### Crear VM Estándar

```json
POST /api/vms
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

### Crear VM Kyubo

```json
POST /api/kyubo/vms
{
  "tenant": "sbc",
  "region": "eastus",
  "max_concurrent_sessions": 50,
  "request_id": "req-12345",
  "entorno": "dev"
}
```

### Conectar por SSH

```bash
# Obtener clave privada desde Key Vault
az keyvault secret show --vault-name key-haec-vm-functions --name ssh-key-rg-eastus-test-vm-001 --query value -o tsv > private_key.pem

# Configurar permisos
chmod 600 private_key.pem

# Conectar
ssh -i private_key.pem svcadmin@{public_ip}
```

## 📚 Documentación

- [Solución Error Validación Pydantic](SOLUCION_ERROR_VALIDACION_PYDANTIC.md)
- [Estado Actual del Sistema](ESTADO_ACTUAL_SISTEMA_Y_RESPUESTAS.md)
- [Colección Postman](VM_Management_Collection.json)

## 🔐 Seguridad

- **API Key** requerida para todos los endpoints
- **Claves SSH** almacenadas de forma segura en Azure Key Vault
- **RBAC** de Azure para control de acceso
- **Validación** estricta de parámetros con Pydantic

## 🌍 Regiones Soportadas

- eastus
- westus
- westus2
- centralus
- eastus2
- westeurope
- northeurope

## 💻 Tamaños de VM Soportados

- Standard_B1s (1 vCPU, 1 GB RAM)
- Standard_B2s (2 vCPU, 4 GB RAM)
- Standard_B4ms (4 vCPU, 16 GB RAM)
- Standard_D2s_v3 (2 vCPU, 8 GB RAM)
- Standard_D4s_v3 (4 vCPU, 16 GB RAM)

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama de feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 📞 Soporte

Para soporte técnico, crear un issue en este repositorio.

---

**Última actualización:** 5 de Agosto de 2025  
**Estado:** ✅ Operativo y funcionando correctamente