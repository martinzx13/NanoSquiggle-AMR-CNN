#!/bin/bash
# 02_process_reads.sh: Unified Basecalling & Alignment

set -e

# 1. Configuración de Rutas
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
ROOT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
cd "$ROOT_DIR" || exit

# Definición de variables
DORADO_BIN="bin/dorado"
DORADO_LIB="bin/lib"
REFERENCE="data/raw/db_resistencia.fasta"
ESTIRPE="KP1779" # Cambia a KP1055 para la otra estirpe
POD5_DIR="data/raw/${ESTIRPE}"
OUTPUT_SAM="data/processed/${ESTIRPE}/aligned_reads.sam"

# Crear carpetas necesarias (sin tocar la carpeta bin si ya existe)
mkdir -p data/processed/${ESTIRPE}

# 2. Validación de archivos
if [ ! -f "$DORADO_BIN" ]; then
    echo "❌ Error: Dorado binary not found in bin/."
    exit 1
fi

# 3. CONFIGURACIÓN CRUCIAL: Cargar librerías compartidas
# Esto soluciona el error "libdorado_torch_lib.so: cannot open shared object file"
export LD_LIBRARY_PATH="$ROOT_DIR/bin/lib:$LD_LIBRARY_PATH"

echo "🧬 Starting Unified Basecalling & Alignment..."
echo "🎯 Reference: $REFERENCE"
echo "📁 Source: $POD5_DIR"

# 4. Ejecución
# Usamos la variable $DORADO_BIN y nos aseguramos de que el sistema vea las libs

# 3. Ejecución de Dorado
# --emit-moves: Crucial for signal-to-base mapping (Geometry Engine)
# --emit-sam: Standard alignment format
# -r: Recursive POD5 directory scanning
# Se asume modelo 'hac' (High Accuracy).
# Si no tienes GPU NVIDIA, añade '--device cpu' al final.

$DORADO_BIN basecaller hac "$POD5_DIR" \
    --reference "$REFERENCE" \
    --emit-moves \
    --emit-sam > "$OUTPUT_SAM"

if [ $? -eq 0 ]; then
    echo "✅ Processed output saved to $OUTPUT_SAM"
else
    echo "❌ Error during Dorado execution."
    exit 1
fi

