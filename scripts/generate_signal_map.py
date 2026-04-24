import pysam
import os
import pandas as pd

# Configuración de rutas
BAM_DIR = os.path.expanduser("~/Klebsiella_POD5/pod5_data/KP1779/bam_files")
POD5_DIR = os.path.expanduser("~/Klebsiella_POD5/pod5_data/KP1779/pod5_pass")
OUTPUT_CSV = "signal_segments_metadata.csv"

def get_signal_mapping():
    if not os.path.exists(BAM_DIR):
        print(f"❌ Error: El directorio de BAMs no existe: {BAM_DIR}")
        return

    segments = []
    for bam_file in [f for f in os.listdir(BAM_DIR) if f.endswith('.bam')]:
        bam_path = os.path.join(BAM_DIR, bam_file)
        pod5_path = os.path.join(POD5_DIR, bam_file.replace('.bam', '.pod5'))
        
        try:
            with pysam.AlignmentFile(bam_path, "rb") as sam:
                for read in sam.fetch():
                    if read.is_unmapped:
                        continue

                    read_id = read.query_name
                    start_base = read.query_alignment_start
                    end_base = read.query_alignment_end
                    
                    # Factor de conversión (estimado: 10 muestras por base)
                    start_sample = start_base * 10
                    end_sample = end_base * 10
                    gene_len = end_sample - start_sample

                    # --- ZONA POSITIVA (Aquí está el gen de resistencia) ---
                    segments.append({
                        'read_id': read_id,
                        'pod5_path': pod5_path,
                        'start': start_sample,
                        'end': end_sample,
                        'label': 1  # RESISTENTE
                    })

                    # --- ZONA NEGATIVA (Exclusión: tomamos un pedazo de la misma read SIN el gen) ---
                    segments.append({
                        'read_id': read_id,
                        'pod5_path': pod5_path,
                        'start': end_sample + 100, # Pequeño margen
                        'end': end_sample + 100 + gene_len,
                        'label': 0  # SENSIBLE (Control Negativo)
                    })
        except Exception as e:
            print(f"⚠️ Error procesando {bam_file}: {e}")

    if segments:
        df = pd.DataFrame(segments)
        df.to_csv(OUTPUT_CSV, index=False)
        print(f"✅ Mapa de señales creado con {len(df)} segmentos en {OUTPUT_CSV}")
    else:
        print("❌ No se encontraron alineamientos válidos.")

if __name__ == "__main__":
    get_signal_mapping()
