#!/bin/bash
# ----------------------------------------------------------------              
# Script 02b: Generación de Alineamientos BAM para Entrenamiento
# Objetivo: Crear el "mapa" (.bam) que conecta la señal con los genes.
# ----------------------------------------------------------------

# 1. Configuración de Rutas
BASE_DIR="$HOME/Klebsiella_POD5"
DORADO="$BASE_DIR/dorado-1.4.0-linux-x64/bin/dorado"
DATA_DIR="$BASE_DIR/pod5_data/KP1779"
POD5_DIR="$DATA_DIR/pod5_pass"
DB_RESISTENCIA="$BASE_DIR/db_resitencia.fasta"
BAM_DIR="$DATA_DIR/bam_files"

# Crear carpeta para los archivos BAM si no existe
mkdir -p "$BAM_DIR"

echo "🚀 Iniciando Dorado Alignment (Generando archivos .BAM)..."
echo "Usando referencia: $DB_RESISTENCIA"

# 2. Ejecución de Dorado con Alineamiento Activo
for pod5 in "$POD5_DIR"/*.pod5; do
    name=$(basename "$pod5" .pod5)
    echo "📦 Procesando señal de: $name"
    
    $DORADO basecaller hac "$pod5" \
        --reference "$DB_RESISTENCIA" \
        --emit-moves > "$BAM_DIR/${name}.bam"
done

echo "✅ Proceso completado. Los mapas .bam están en: $BAM_DIR"
