#!/bin/bash
BASE_DIR="$HOME/Klebsiella_POD5"
DORADO="$BASE_DIR/dorado-1.4.0-linux-x64/bin/dorado"
DATA_DIR="$BASE_DIR/pod5_data/KP1779"
FASTA_DIR="$DATA_DIR/fasta_files"

mkdir -p "$FASTA_DIR"

echo "🧬 Iniciando Basecalling (Dorado)..."
# Loop pelos POD5 renomeados
for pod5 in "$DATA_DIR/pod5_pass"/*.pod5; do
    name=$(basename "$pod5" .pod5)
    echo "🚀 Processando: $name"
    
    # Basecalling -> FASTQ -> Conversão direta para FASTA (via sed)
    $DORADO basecaller hac "$pod5" --emit-fastq | \
    sed -n '1~4s/^@/>/p;2~4p' > "$FASTA_DIR/${name}.fasta"
done

echo "✅ Reads convertidas para FASTA em $FASTA_DIR"
