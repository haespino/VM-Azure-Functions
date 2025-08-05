#!/bin/bash
# Script para montar disco de datos automáticamente
# Uso: ./mount_data_disk.sh <mount_point> <auto_setup_sbc>

MOUNT_POINT="$1"
AUTO_SETUP_SBC="$2"

# Validar parámetros
if [ -z "$MOUNT_POINT" ]; then
    echo "Error: Debe especificar el punto de montaje"
    echo "Uso: $0 <mount_point> [auto_setup_sbc]"
    exit 1
fi

# Configurar punto de montaje por defecto para SBC
if [ -z "$MOUNT_POINT" ]; then
    MOUNT_POINT="/opt/sbc_deploy"
fi

# Configurar auto setup por defecto
if [ -z "$AUTO_SETUP_SBC" ]; then
    AUTO_SETUP_SBC="true"
fi

echo "=== Iniciando montaje automático de disco de datos ==="
echo "Punto de montaje: $MOUNT_POINT"
echo "Auto setup SBC: $AUTO_SETUP_SBC"
echo "Fecha: $(date)"

# Detectar disco de datos (buscar discos sin montar)
echo "Detectando discos disponibles..."
lsblk -f

# Buscar el primer disco sin sistema de archivos (nuevo disco de datos)
DATA_DISK=$(lsblk -rno NAME,FSTYPE | grep -E '^sd[b-z]\s*$' | head -1 | awk '{print $1}')

if [ -z "$DATA_DISK" ]; then
    echo "No se encontró disco de datos para montar"
    echo "Discos disponibles:"
    lsblk
    exit 1
fi

echo "Disco de datos detectado: /dev/$DATA_DISK"

# Verificar si el disco ya tiene sistema de archivos
FSTYPE=$(lsblk -rno FSTYPE /dev/$DATA_DISK)
if [ -n "$FSTYPE" ]; then
    echo "El disco /dev/$DATA_DISK ya tiene sistema de archivos: $FSTYPE"
else
    echo "Formateando disco /dev/$DATA_DISK con ext4..."
    sudo mkfs.ext4 /dev/$DATA_DISK -F
    if [ $? -eq 0 ]; then
        echo "Disco formateado exitosamente"
    else
        echo "Error al formatear el disco"
        exit 1
    fi
fi

# Crear punto de montaje
echo "Creando punto de montaje: $MOUNT_POINT"
sudo mkdir -p $MOUNT_POINT

# Montar disco
echo "Montando disco /dev/$DATA_DISK en $MOUNT_POINT"
sudo mount /dev/$DATA_DISK $MOUNT_POINT
if [ $? -eq 0 ]; then
    echo "Disco montado exitosamente"
else
    echo "Error al montar el disco"
    exit 1
fi

# Obtener UUID del disco para fstab
UUID=$(sudo blkid -s UUID -o value /dev/$DATA_DISK)
echo "UUID del disco: $UUID"

# Añadir a fstab para montaje automático en reinicio
echo "Configurando montaje automático en /etc/fstab"
if ! grep -q "$UUID" /etc/fstab; then
    echo "UUID=$UUID $MOUNT_POINT ext4 defaults,nofail 0 2" | sudo tee -a /etc/fstab
    echo "Entrada añadida a /etc/fstab"
else
    echo "El disco ya está configurado en /etc/fstab"
fi

# Configurar permisos
echo "Configurando permisos para usuario svcadmin"
sudo chown svcadmin:svcadmin $MOUNT_POINT
sudo chmod 755 $MOUNT_POINT

# Configuración específica para SBC si está habilitada
if [ "$AUTO_SETUP_SBC" = "true" ]; then
    echo "Configurando estructura SBC_DEPLOY..."
    
    # Crear directorios SBC
    sudo mkdir -p $MOUNT_POINT/{logs,config,data,temp,scripts,backups}
    sudo chown -R svcadmin:svcadmin $MOUNT_POINT
    sudo chmod -R 755 $MOUNT_POINT
    
    # Crear archivo de información SBC
    cat > $MOUNT_POINT/sbc_info.txt << EOF
SBC Deploy Directory
Created: $(date)
Mount Point: $MOUNT_POINT
Disk: /dev/$DATA_DISK
UUID: $UUID
Host: $(hostname)
User: svcadmin

Directorios creados:
- logs/     : Archivos de log del SBC
- config/   : Archivos de configuración
- data/     : Datos de aplicación
- temp/     : Archivos temporales
- scripts/  : Scripts de mantenimiento
- backups/  : Respaldos
EOF
    
    # Crear script de verificación SBC
    cat > $MOUNT_POINT/scripts/check_sbc_mount.sh << 'EOF'
#!/bin/bash
# Script de verificación del montaje SBC
echo "=== Verificación SBC Mount ==="
echo "Fecha: $(date)"
echo "Punto de montaje: $1"
echo "Espacio disponible:"
df -h $1
echo "Permisos:"
ls -la $1
echo "Estructura de directorios:"
tree $1 2>/dev/null || ls -la $1
EOF
    
    chmod +x $MOUNT_POINT/scripts/check_sbc_mount.sh
    
    echo "Estructura SBC configurada exitosamente"
    echo "Directorios creados en $MOUNT_POINT:"
    ls -la $MOUNT_POINT
fi

# Verificación final
echo "=== Verificación final ==="
echo "Estado del montaje:"
mount | grep $MOUNT_POINT
echo "Espacio disponible:"
df -h $MOUNT_POINT
echo "Permisos del directorio:"
ls -la $MOUNT_POINT

echo "=== Montaje automático completado exitosamente ==="
echo "Disco /dev/$DATA_DISK montado en $MOUNT_POINT"
echo "Configuración SBC: $AUTO_SETUP_SBC"
echo "Fecha de finalización: $(date)"

exit 0