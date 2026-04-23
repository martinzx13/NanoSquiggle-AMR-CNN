#!/bin/bash

# --- CONFIGURAÇÃO DE CAMINHOS ---
BASE_DIR="$HOME/Klebsiella_POD5"
BLAST_BIN_DIR="$BASE_DIR/bin" 

DB_FASTA="$BASE_DIR/db_resitencia.fasta"
DB_INDEX_DIR="$BASE_DIR/db_resistencia_index"
DB_OUT="$DB_INDEX_DIR/db_resistencia"
QUERY_DIR="$BASE_DIR/pod5_data/KP1779/fasta_files"
OUTPUT_CSV="$BASE_DIR/pod5_data/KP1779/KP1779_resultado_final.csv"

# --- 1. VERIFICAÇÃO DE AMBIENTE ---
if [ ! -f "$BLAST_BIN_DIR/makeblastdb" ]; then
    echo "❌ ERRO: Binários do BLAST não encontrados."
    exit 1
fi

# --- 2. CRIAÇÃO DO ÍNDICE ---
echo "🛠️ Criando Index do BLAST..."
mkdir -p "$DB_INDEX_DIR"
"$BLAST_BIN_DIR/makeblastdb" -in "$DB_FASTA" -dbtype nucl -out "$DB_OUT"

# --- 3. PREPARAÇÃO DO CSV COM LEGENDAS ---
echo "📝 Preparando ficheiro CSV com cabeçalhos..."
# Criamos o ficheiro e escrevemos a primeira linha com os nomes das colunas
echo "read_id,gene_id,pident,length,mismatch,gapopen,q_start,q_end,s_start,s_end,evalue,bitscore" > "$OUTPUT_CSV"

# --- 4. EXECUÇÃO DO BLAST ---
echo "🔍 Correndo BLAST (KP1779)..."
cat "$QUERY_DIR"/*.fasta > combined_temp.fasta

# Usamos o operador '>>' para ANEXAR os resultados abaixo do cabeçalho
"$BLAST_BIN_DIR/blastn" -query combined_temp.fasta \
       -db "$DB_OUT" \
       -outfmt "10 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore" \
       -evalue 0.001 >> "$OUTPUT_CSV"

rm combined_temp.fasta

if [ -f "$OUTPUT_CSV" ]; then
    echo "------------------------------------------------"
    echo "✅ ANÁLISE CONCLUÍDA COM SUCESSO!"
    echo "📂 Resultados: $OUTPUT_CSV"
    # Conta as linhas subtraindo 1 (o cabeçalho)
    num_hits=$(($(wc -l < "$OUTPUT_CSV") - 1))
    echo "📈 Total de matches encontrados: $num_hits"
    echo "------------------------------------------------"
fi
