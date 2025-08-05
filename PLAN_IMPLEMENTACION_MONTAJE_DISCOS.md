# Plan de Implementación - Montaje Automático de Discos de Datos

**Fecha:** 5 de Agosto de 2025  
**Estado:** 📋 Planificado - Listo para implementación  
**Prioridad:** Alta  
**Tiempo estimado:** 2-3 horas

## 🎯 Objetivo

Implementar el montaje automático de discos de datos en las VMs creadas, especialmente para VMs Kyubo que requieren el directorio `/opt/sbc_deploy` configurado automáticamente.

## 📋 Estado Actual

### ✅ Ya Implementado
- Modelo de datos `DataDiskConfig` en `models.py`
- Validación de parámetros de disco
- Configuración de disco en payload de creación
- Documentación de la funcionalidad

### ⚠️ Pendiente de Implementación
- Script de montaje automático
- Integración con cloud-init
- Modificación de `create_vm_logic()` para incluir discos de datos
- Configuración automática SBC

## 🔧 Plan de Implementación

### Fase 1: Crear Script de Montaje (30 min)

**Archivo:** `/scripts/mount_data_disk.sh`

```bash
#!/bin/bash
# Script para montaje automático de disco de datos
# Parámetros: $1=mount_point, $2=auto_setup_sbc

MOUNT_POINT="$1"
AUTO_SETUP_SBC="$2"
LOG_FILE="/var/log/mount_data_disk.log"

echo "[$(date)] Iniciando montaje de disco de datos" >> $LOG_FILE
echo "[$(date)] Mount point: $MOUNT_POINT" >> $LOG_FILE
echo "[$(date)] Auto setup SBC: $AUTO_SETUP_SBC" >> $LOG_FILE

# Detectar disco de datos (primer disco sin formato)
DATA_DISK=$(lsblk -f | grep -v SWAP | grep -v '/' | awk '/sd[b-z]/ && $2=="" {print $1; exit}')

if [ -n "$DATA_DISK" ]; then
    echo "[$(date)] Disco detectado: /dev/$DATA_DISK" >> $LOG_FILE
    
    # Formatear disco con ext4
    echo "[$(date)] Formateando disco..." >> $LOG_FILE
    sudo mkfs.ext4 -F /dev/$DATA_DISK >> $LOG_FILE 2>&1
    
    # Crear punto de montaje
    echo "[$(date)] Creando punto de montaje: $MOUNT_POINT" >> $LOG_FILE
    sudo mkdir -p $MOUNT_POINT
    
    # Obtener UUID del disco
    UUID=$(sudo blkid -s UUID -o value /dev/$DATA_DISK)
    echo "[$(date)] UUID del disco: $UUID" >> $LOG_FILE
    
    # Montar disco
    echo "[$(date)] Montando disco..." >> $LOG_FILE
    sudo mount /dev/$DATA_DISK $MOUNT_POINT
    
    # Añadir a fstab para montaje automático
    echo "[$(date)] Añadiendo entrada a fstab..." >> $LOG_FILE
    echo "UUID=$UUID $MOUNT_POINT ext4 defaults,nofail 0 2" | sudo tee -a /etc/fstab
    
    # Configurar permisos
    sudo chown svcadmin:svcadmin $MOUNT_POINT
    sudo chmod 755 $MOUNT_POINT
    
    echo "[$(date)] Disco montado exitosamente en $MOUNT_POINT" >> $LOG_FILE
    
    # Configuración específica para SBC si está habilitada
    if [ "$AUTO_SETUP_SBC" = "true" ]; then
        echo "[$(date)] Configurando estructura SBC..." >> $LOG_FILE
        
        # Crear estructura de directorios SBC
        sudo mkdir -p $MOUNT_POINT/{logs,config,data,temp,scripts,backup}
        sudo chown -R svcadmin:svcadmin $MOUNT_POINT
        
        # Crear archivo de información SBC
        cat > $MOUNT_POINT/sbc_info.txt << EOF
SBC Deploy Directory
Created: $(date)
Mount Point: $MOUNT_POINT
Disk: /dev/$DATA_DISK
UUID: $UUID
Auto Setup: $AUTO_SETUP_SBC
Version: 1.0
EOF
        
        # Crear script de verificación
        cat > $MOUNT_POINT/scripts/verify_sbc.sh << 'EOF'
#!/bin/bash
echo "=== SBC Deploy Directory Verification ==="
echo "Mount Point: $(pwd)"
echo "Disk Usage: $(df -h . | tail -1)"
echo "Directories:"
ls -la
echo "=== End Verification ==="
EOF
        chmod +x $MOUNT_POINT/scripts/verify_sbc.sh
        
        echo "[$(date)] Configuración SBC completada" >> $LOG_FILE
    fi
    
    echo "[$(date)] Montaje completado exitosamente" >> $LOG_FILE
    exit 0
else
    echo "[$(date)] ERROR: No se encontró disco de datos para montar" >> $LOG_FILE
    exit 1
fi
```

### Fase 2: Modificar create_vm_logic() (45 min)

**Archivo:** `utils.py` - Función `create_vm_logic()`

**Cambios necesarios:**

1. **Añadir configuración de disco de datos:**
```python
# Configurar disco de datos si está habilitado
if data_disk_config and data_disk_config.enabled:
    data_disks = [{
        'lun': 0,
        'create_option': 'Empty',
        'disk_size_gb': data_disk_config.size_gb,
        'managed_disk': {
            'storage_account_type': 'Standard_LRS'
        },
        'caching': 'ReadWrite'
    }]
    vm_config['storage_profile']['data_disks'] = data_disks
```

2. **Crear cloud-init script:**
```python
# Generar script cloud-init para montaje automático
if data_disk_config and data_disk_config.enabled:
    cloud_init_script = f"""
#!/bin/bash
# Cloud-init script para montaje automático de disco

# Esperar a que el disco esté disponible
sleep 10

# Descargar script de montaje
wget -O /tmp/mount_data_disk.sh https://raw.githubusercontent.com/haespino/VM-Azure-Functions/main/scripts/mount_data_disk.sh
chmod +x /tmp/mount_data_disk.sh

# Ejecutar montaje
/tmp/mount_data_disk.sh "{data_disk_config.mount_point}" "{str(data_disk_config.auto_setup_sbc).lower()}"

# Limpiar archivo temporal
rm -f /tmp/mount_data_disk.sh
"""
    
    # Codificar en base64 para cloud-init
    import base64
    encoded_script = base64.b64encode(cloud_init_script.encode()).decode()
    
    # Añadir a configuración de VM
    vm_config['os_profile']['custom_data'] = encoded_script
```

### Fase 3: Actualizar Respuesta de Creación (15 min)

**Modificar respuesta para incluir información del disco:**

```python
# Añadir información del disco de datos a la respuesta
if data_disk_config and data_disk_config.enabled:
    response_data['data_disk_info'] = {
        'enabled': True,
        'size_gb': data_disk_config.size_gb,
        'mount_point': data_disk_config.mount_point,
        'auto_setup_sbc': data_disk_config.auto_setup_sbc,
        'disk_type': 'Standard_LRS'
    }
else:
    response_data['data_disk_info'] = {
        'enabled': False
    }
```

### Fase 4: Testing y Validación (60 min)

**Tests a realizar:**

1. **Test básico de montaje:**
```json
{
  "name": "test-disk-mount-001",
  "region": "eastus",
  "size": "Standard_B2s",
  "data_disk": {
    "enabled": true,
    "size_gb": 100,
    "mount_point": "/opt/test",
    "auto_setup_sbc": false
  }
}
```

2. **Test SBC automático:**
```json
{
  "tenant": "sbc",
  "region": "eastus",
  "max_concurrent_sessions": 50,
  "request_id": "test-sbc-mount-001",
  "entorno": "dev"
}
```

3. **Verificaciones post-creación:**
```bash
# Conectar por SSH y verificar
ssh -i key.pem svcadmin@{public_ip}

# Verificar montaje
df -h
lsblk
cat /etc/fstab

# Verificar estructura SBC (si aplica)
ls -la /opt/sbc_deploy/
cat /opt/sbc_deploy/sbc_info.txt
/opt/sbc_deploy/scripts/verify_sbc.sh
```

## 📁 Archivos a Crear/Modificar

### Nuevos Archivos
1. `/scripts/mount_data_disk.sh` - Script de montaje
2. `/scripts/verify_disk_mount.sh` - Script de verificación

### Archivos a Modificar
1. `utils.py` - Función `create_vm_logic()`
2. `models.py` - Posibles ajustes en respuestas

### Archivos de Documentación
1. `MONTAJE_DISCOS_IMPLEMENTADO.md` - Documentación post-implementación
2. `TESTING_MONTAJE_DISCOS.md` - Resultados de testing

## 🔍 Criterios de Aceptación

### Funcionalidad Básica
- ✅ El disco de datos se crea correctamente
- ✅ El disco se formatea automáticamente
- ✅ El disco se monta en el punto especificado
- ✅ La entrada se añade a `/etc/fstab`
- ✅ Los permisos se configuran correctamente

### Funcionalidad SBC
- ✅ Se crea la estructura de directorios SBC
- ✅ Se genera el archivo de información
- ✅ Se crean scripts de verificación
- ✅ Los permisos son correctos para `svcadmin`

### Robustez
- ✅ El script maneja errores correctamente
- ✅ Se genera log de actividades
- ✅ Funciona con diferentes tamaños de disco
- ✅ Compatible con diferentes puntos de montaje

## 🚨 Consideraciones de Seguridad

1. **Permisos de archivos:**
   - Scripts ejecutables solo por root/svcadmin
   - Directorios con permisos apropiados
   - Logs protegidos contra escritura no autorizada

2. **Validación de entrada:**
   - Validar puntos de montaje
   - Verificar disponibilidad de disco
   - Manejo de errores robusto

3. **Logging y auditoría:**
   - Registrar todas las operaciones
   - Timestamps en todas las entradas
   - Información de debugging disponible

## 📊 Métricas de Éxito

- **Tiempo de montaje:** < 30 segundos
- **Tasa de éxito:** > 95%
- **Tiempo total de creación VM:** < 90 segundos
- **Cero errores de permisos**
- **Cero fallos de montaje**

## 🔄 Plan de Rollback

En caso de problemas:

1. **Rollback inmediato:**
   - Comentar código de disco de datos
   - Revertir a versión anterior
   - Mantener funcionalidad básica

2. **Debugging:**
   - Revisar logs de cloud-init
   - Verificar script de montaje
   - Validar configuración de disco

3. **Recuperación:**
   - Corregir problemas identificados
   - Re-testing en ambiente controlado
   - Implementación gradual

---

**Estado:** 📋 Listo para implementación  
**Próximo paso:** Crear script de montaje y comenzar Fase 1  
**Responsable:** Equipo de desarrollo VM Management  
**Fecha objetivo:** 6 de Agosto de 2025