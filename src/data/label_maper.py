import pysam
import pandas as pd
import random
from pathlib import Path

def generate_production_dataset(bam_path, output_csv, neg_ratio=3, coverage_threshold=95.0):
    print(f"🧬 Opening Sorted BAM file: {bam_path}")
    
    # "rb" stands for Read Binary (Required for BAM files)
    samfile = pysam.AlignmentFile(bam_path, "rb") 
    
    pos_records = []
    neg_records = []
    discarded_weak = 0

    print("🧐 Scanning for High-Quality Positives and Hard Negatives...")

    for read in samfile.fetch(until_eof=True):
        tags = dict(read.tags)
        
        # 1. QUALITY CHECKER: Must have Move Table and Trim Start
        if 'mv' not in tags or 'ts' not in tags:
            continue
            
        stride = tags['mv'][0]      # The dynamic stride (e.g., 6)
        moves = tags['mv'][1:]      # The 1s and 0s array
        trim_start = tags['ts']     # Skipped electrical samples
        pod5_filename = tags.get('fn', 'unknown.pod5')

        # --- CLASS 1: High-Quality Mapped Reads (The Positives) ---
        if not read.is_unmapped and not read.is_secondary:
            
            # 2. FILTER FOR WEAKS: Calculate actual coverage percentage
            gene_length = samfile.get_reference_length(read.reference_name)
            alignment_length = read.reference_length # How many bases actually matched
            
            coverage_pct = (alignment_length / gene_length) * 100
            
            if coverage_pct < coverage_threshold:
                discarded_weak += 1
                continue # Skip this read, it's too fragmented
            
            # 3. SPATIAL GEOMETRY: Calculate exact signal coordinates
            base_start = read.query_alignment_start
            base_end = read.query_alignment_end
            
            moves_to_start = 0
            base_count = 0
            for step in moves:
                base_count += step
                moves_to_start += 1
                if base_count == base_start:
                    break
                    
            moves_to_end = moves_to_start
            for step in moves[moves_to_start:]:
                base_count += step
                moves_to_end += 1
                if base_count == base_end:
                    break

            signal_start = trim_start + (moves_to_start * stride)
            signal_end = trim_start + (moves_to_end * stride)

            pos_records.append({
                "read_id": read.query_name,
                "pod5_file": pod5_filename,
                "target_gene": read.reference_name,
                "signal_start": signal_start, 
                "signal_end": signal_end,
                "label": 1,
                "coverage_pct": round(coverage_pct, 2)
            })

        # --- CLASS 0: Unmapped Reads (The Hard Negatives) ---
        elif read.is_unmapped:
            # Standard 30,000 sample window of pure Klebsiella background
            neg_records.append({
                "read_id": read.query_name,
                "pod5_file": pod5_filename,
                "target_gene": "NONE_BACKGROUND",
                "signal_start": 10000, 
                "signal_end": 40000,
                "label": 0,
                "coverage_pct": 0.0
            })

    samfile.close()

    # --- DATASET BALANCING ---
    print(f"\n📊 Extracted {len(pos_records)} High-Quality Positives (>95% Coverage).")
    print(f"🗑️  Discarded {discarded_weak} weak/fragmented alignments.")
    
    # We enforce a strict Negative:Positive ratio so the model doesn't get biased
    num_neg_to_keep = len(pos_records) * neg_ratio
    
    if len(neg_records) > num_neg_to_keep:
        neg_records = random.sample(neg_records, num_neg_to_keep)
        
    print(f"⚖️  Kept {len(neg_records)} Hard Negatives to maintain a {neg_ratio}:1 ratio.")

    # Combine, Shuffle randomly, and Save
    final_df = pd.DataFrame(pos_records + neg_records)
    
    # If the dataframe is not empty, shuffle and save
    if not final_df.empty:
        final_df = final_df.sample(frac=1, random_state=42).reset_index(drop=True)
        final_df.to_csv(output_csv, index=False)
        print(f"\n✅ SUCCESS: Master CSV written to '{output_csv}' with {len(final_df)} total rows.")
    else:
        print("\n❌ ERROR: No valid data found to write to CSV.")

if __name__ == "__main__":
    # Use Pathlib to ensure it works from the project root
    ROOT_DIR = Path(__file__).resolve().parent.parent.parent
    
    # Notice we are now using the _sorted.bam file!
    ESTIRPE= "KP1055"
    BAM_FILE = ROOT_DIR / "data" / "processed" / ESTIRPE / f"aligned_sorted_{ESTIRPE}.bam"
    OUT_CSV = ROOT_DIR / "data" / "master.csv"
    
    generate_production_dataset(str(BAM_FILE), str(OUT_CSV))