import pysam
import os

# Configurações

input_dir = "data/processed/KP1779_BAM"
output_dir = "data/processed/KP1779_FILTERED"
min_length = 500  # Filtro de 500bp para evitar fragmentos curtos
min_mapq = 60     # Mapping Quality máximo (alinhamento único e fiável)

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

for file in os.listdir(input_dir):
    if file.endswith(".bam"):
        input_path = os.path.join(input_dir, file)
        output_path = os.path.join(output_dir, file.replace(".bam", "_filtered.bam"))

        print(f"🔍 Filtrando {file}...")

        with pysam.AlignmentFile(input_path, "rb") as infile:
            with pysam.AlignmentFile(output_path, "wb", template=infile) as outfile:
                count = 0
                for read in infile:
                    # FILTROS CRÍTICOS:
                    # 1. Deve estar mapeado (!read.is_unmapped)
                    # 2. Comprimento do alinhamento >= 500bp
                    # 3. Qualidade de mapeamento >= 60
                    if not read.is_unmapped and read.query_alignment_length >= min_length and read.mapping_quality >= min_mapq:
                        outfile.write(read)
                        count += 1

        print(f"✅ {count} reads de alta confiança extraídas para {output_path}")