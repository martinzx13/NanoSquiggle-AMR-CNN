import pandas as pd
from sklearn.model_selection import train_test_split
import os

def split_dataset(input_csv):
    if not os.path.exists(input_csv):
        print(f"❌ Error: El archivo {input_csv} no existe.")
        return

    df = pd.read_csv(input_csv)
    # Mezclamos los datos (Shuffling)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    # Primer Split: 80% para ENTRENAMIENTO
    train_df, temp_df = train_test_split(df, test_size=0.20, random_state=42)

    # Segundo Split: 15% para TEST y 5% para VALIDACIÓN
    # (El 25% de temp_df es el 5% del total original)
    test_df, val_df = train_test_split(temp_df, test_size=0.25, random_state=42)

    train_df.to_csv("train_split.csv", index=False)
    test_df.to_csv("test_split.csv", index=False)
    val_df.to_csv("val_split.csv", index=False)

    print(f"📊 Dataset listo:")
    print(f"   - Entrenamiento (80%): {len(train_df)} muestras")
    print(f"   - Test (15%): {len(test_df)} muestras")
    print(f"   - Validación (5%): {len(val_df)} muestras")

if __name__ == "__main__":
    split_dataset("signal_segments_metadata.csv")
