import pysam
import os
import pandas as pd
import random
import glob
import argparse

# Mapeamento para Multiclass (3 genes de resistência)
# Usamos substrings únicas do cabeçalho FASTA db_resistencia.fasta
GENE_TO_MULTICLASS = {
    "HEE1644226": 0, # APH(6)-I
    "MH733892": 1,   # blaSHV
    "MZ092836": 2    # oqxA
}

def get_multiclass_label(ref_name):
    """Retorna a classe correspondente ao gene baseado na referência do BAM."""
    for key, label in GENE_TO_MULTICLASS.items():
        if key in ref_name:
            return label
    return -1 # Desconhecido (não deverá acontecer se o banco estiver correto)

def generate_datasets(sam_path, pod5_dir, output_binary, output_multiclass, window_size=3000):
    if not os.path.exists(sam_path):
        print(f"❌ Erro: O ficheiro de alinhamento SAM/BAM não existe: {sam_path}")
        return

    pod5_files = glob.glob(f"{pod5_dir}/*.pod5")
    if not pod5_files:
        print(f"⚠️ Aviso: Não foram encontrados ficheiros POD5 em {pod5_dir}")
        default_pod5 = "unknown.pod5"
    else:
        # Simplificação: se houver mais que um pod5, seria necessário mapear o read_id ao ficheiro correto.
        # Estamos a assumir que o fluxo junta tudo ou usa o primeiro disponível, 
        # ou o sam tem uma forma de referenciar.
        default_pod5 = pod5_files[0] 

    binary_records = []
    multiclass_records = []

    print(f"📦 A processar {sam_path} para gerar os CSVs em cascata...")

    # Tenta detetar se é BAM ("rb") ou SAM ("r")
    mode = "rb" if sam_path.endswith(".bam") else "r"
    
    with pysam.AlignmentFile(sam_path, mode) as sam:
        for read in sam.fetch(until_eof=True):
            read_id = read.query_name
            
            # --- ZONA NEGATIVA (BACKGROUND / RUÍDO) ---
            if read.is_unmapped:
                # Gerar janelas aleatórias (simulando que é ruído sem sinal de resistência)
                start = random.randint(0, 5000)
                
                binary_records.append({
                    "pod5_file": default_pod5,
                    "read_id": read_id,
                    "signal_start": start,
                    "signal_end": start + window_size,
                    "label": 0  # 0 = Background
                })
                
            # --- ZONA POSITIVA (GENE ENCONTRADO) ---
            else:
                try:
                    # Tenta obter a 'ts' tag gerada pelo Dorado --emit-moves
                    start = int(read.get_tag('ts'))
                except KeyError:
                    # Conversão por fallback (multiplicando base position por 10 como feito noutros scripts)
                    start = read.query_alignment_start * 10
                
                ref_name = read.reference_name
                
                # Registo Binário (1 = Gene Presente)
                binary_records.append({
                    "pod5_file": default_pod5,
                    "read_id": read_id,
                    "signal_start": start,
                    "signal_end": start + window_size,
                    "label": 1  # 1 = Gene
                })

                # Registo Multiclasse (0, 1, ou 2 dependendo do gene)
                multi_label = get_multiclass_label(ref_name)
                if multi_label != -1:
                    multiclass_records.append({
                        "pod5_file": default_pod5,
                        "read_id": read_id,
                        "signal_start": start,
                        "signal_end": start + window_size,
                        "label": multi_label
                    })

    # Guardar os datasets
    df_binary = pd.DataFrame(binary_records)
    df_binary.to_csv(output_binary, index=False)
    
    df_multi = pd.DataFrame(multiclass_records)
    df_multi.to_csv(output_multiclass, index=False)
    
    print(f"✅ Ficheiro {output_binary} gerado com {len(df_binary)} amostras.")
    if not df_binary.empty:
        print(df_binary['label'].value_counts())
        
    print(f"✅ Ficheiro {output_multiclass} gerado com {len(df_multi)} amostras.")
    if not df_multi.empty:
        print(df_multi['label'].value_counts())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Gerar Datasets em Cascata a partir de um alinhamento Dorado.')
    parser.add_argument('--sam', required=True, help='Caminho para o ficheiro .sam ou .bam.')
    parser.add_argument('--pod5_dir', required=True, help='Caminho para a pasta que contém os .pod5.')
    parser.add_argument('--out_binary', default='cascade_binary_index.csv', help='Caminho do CSV de saída binário.')
    parser.add_argument('--out_multi', default='cascade_multiclass_index.csv', help='Caminho do CSV de saída multiclasse.')
    
    args = parser.parse_args()
    generate_datasets(args.sam, args.pod5_dir, args.out_binary, args.out_multi)
