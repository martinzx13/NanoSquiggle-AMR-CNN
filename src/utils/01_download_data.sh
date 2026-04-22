#!/bin/bash
# 01_download_data.sh: Environment Setup and Data Acquisition
# Aligned with README.md structure.
set -e

# Configurações de Caminhos
# Como el script está en src/utils/, subimos dos niveles para llegar a la raíz.
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
ROOT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
cd "$ROOT_DIR" || exit

echo "📁 Initializing project structure in: $(pwd)"
mkdir -p bin data/raw data/processed configs docs notebooks scripts tests

# 2. # 1. Download do Dorado (se não existir) into bin/)

if [ ! -f "bin/dorado" ]; then
    echo "⬇️ Downloading Dorado..."
    # He actualizado el link a una versión real de Linux (0.5.0) para asegurar que funcione.
    curl -L "https://cdn.oxfordnanoportal.com/software/analysis/dorado-0.5.0-linux-x64.tar.gz" -o dorado.tar.gz
    tar -xzf dorado.tar.gz
    echo "📦 Organizando Dorado en bin/..."
    # IMPORTANTE: Ajustamos el mv según el nombre de la carpeta extraída
    mv dorado-0.5.0-linux-x64/bin/dorado bin/
    mv dorado-0.5.0-linux-x64/lib bin/

    echo "✅ Dorado instalado en bin/"
    rm -rf dorado-0.5.0-linux-x64 dorado.tar.gz
    echo "✅ Dorado installed in bin/"
fi

# 3. Download da Estirpe KP1779
# 3. Download da Estirpe KP1055
ESTIRPE="KP1055" # Cambia a KP1055 para la otra estirpe

DATA_URL="https://data.narodni-repozitar.cz/general/datasets/dj8ys-a4r49/files/${ESTIRPE}_pod5.tar.gz"
RAW_DATA_DIR="data/raw/${ESTIRPE}"

if [ ! -d "$RAW_DATA_DIR" ]; then
    echo "⬇️  Descarregando ${ESTIRPE} (1.5GB) ..."
    mkdir -p "$RAW_DATA_DIR"
    wget -q --show-progress -O data/raw/${ESTIRPE}.tar.gz "$DATA_URL"

    # 4. Extração e Limpeza imediata
    echo "📦 Extraindo e organizando POD5..."
    tar -xzf data/raw/${ESTIRPE}.tar.gz -C "$RAW_DATA_DIR"
    rm data/raw/${ESTIRPE}.tar.gz

    # 5. Renomeação Padronizada (${ESTIRPE}_01, 02...)
    # Movemos los archivos de la carpeta extraída a la raíz de RAW_DATA_DIR
    if [ -d "$RAW_DATA_DIR/pod5_pass" ]; then
        mv "$RAW_DATA_DIR/pod5_pass"/* "$RAW_DATA_DIR/"
        rm -rf "$RAW_DATA_DIR/pod5_fail" "$RAW_DATA_DIR/pod5_pass"
    fi
    echo "✅ Dataset prepared in $RAW_DATA_DIR"
fi

# 4. Move Resistance Database to data/raw
# Buscamos el archivo en la raíz del proyecto para moverlo a data/raw
if [ -f "files_tratment/db_resitenica.fasta" ]; then
    mv "files_tratment/db_resitenica.fasta" "data/raw/db_resistencia.fasta"
    echo "✅ Move db_resistencia.fasta to data/raw/"
fi

echo "✅ Setup concluído com sucesso."
echo "🚀 Setup Complete. Use 02_process_reads.sh to begin basecalling."