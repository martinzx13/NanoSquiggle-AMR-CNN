import torch
import pandas as pd
from torch.utils.data import Dataset, DataLoader, random_split
import pod5
import os
import argparse
import sys

# Adicionar src ao path para conseguir importar os modelos
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.models.cnn_2 import BinaryDetectorCNN, GeneClassifierCNN
from src.models.train_evaluate import train_model, evaluate_metrics, plot_loss_curve

class CascadedPod5Dataset(Dataset):
    """Dataset especializado para ler os CSVs gerados para o pipeline em cascata."""
    def __init__(self, csv_file, seq_len=3000):
        self.data = pd.read_csv(csv_file)
        self.seq_len = seq_len

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        row = self.data.iloc[idx]
        start, end = int(row['signal_start']), int(row['signal_end'])
        
        try:
            with pod5.Reader(row['pod5_file']) as reader:
                read = reader.get_read(row['read_id'])
                signal = read.signal[start:end]
        except Exception as e:
            # Em caso de erro na extração, devolve zeros
            signal = [0] * self.seq_len

        tensor = torch.tensor(signal, dtype=torch.float32)
        if len(tensor) < self.seq_len:
            tensor = torch.cat([tensor, torch.zeros(self.seq_len - len(tensor))])
        else:
            tensor = tensor[:self.seq_len]
            
        # Normalização simples (Z-score)
        tensor = (tensor - tensor.mean()) / (tensor.std() + 1e-8)
        return tensor, torch.tensor(int(row['label']), dtype=torch.long)

def get_dataloaders(csv_path, batch_size=32, seq_len=3000):
    dataset = CascadedPod5Dataset(csv_path, seq_len=seq_len)
    total = len(dataset)
    if total == 0:
        return None, None, None
        
    tr_size = int(0.80 * total)
    vl_size = int(0.15 * total)
    ts_size = total - tr_size - vl_size

    train_ds, val_ds, test_ds = random_split(dataset, [tr_size, vl_size, ts_size])
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size)
    test_loader = DataLoader(test_ds, batch_size=batch_size)
    
    return train_loader, val_loader, test_loader

def main():
    parser = argparse.ArgumentParser(description='Treinar Modelos em Cascata (Binário -> Multiclasse).')
    parser.add_argument('--binary_csv', required=True, help='Caminho para o dataset binário.')
    parser.add_argument('--multi_csv', required=True, help='Caminho para o dataset multiclasse.')
    parser.add_argument('--epochs', type=int, default=10, help='Número de épocas.')
    parser.add_argument('--batch_size', type=int, default=32, help='Tamanho do batch.')
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"🖥️ A utilizar dispositivo: {device}")

    # --- FASE 1: Treino do Modelo Binário ---
    print("\n" + "="*50)
    print("🚀 FASE 1: TREINO DO DETETOR BINÁRIO (Ruído vs Gene)")
    print("="*50)
    
    train_loader_bin, val_loader_bin, test_loader_bin = get_dataloaders(args.binary_csv, args.batch_size)
    
    if train_loader_bin:
        binary_model = BinaryDetectorCNN(sequence_length=3000).to(device)
        bin_train_loss, bin_val_loss = train_model(binary_model, train_loader_bin, val_loader_bin, epochs=args.epochs, device=device)
        
        print("\n📊 Avaliação FASE 1 (Binário):")
        evaluate_metrics(binary_model, test_loader_bin, device=device)
        
        # Guardar pesos
        torch.save(binary_model.state_dict(), "binary_detector_weights.pth")
        print("✅ Pesos da Fase 1 guardados em 'binary_detector_weights.pth'")
    else:
        print("⚠️ Dataset Binário vazio ou inválido.")

    # --- FASE 2: Treino do Modelo Multiclasse ---
    print("\n" + "="*50)
    print("🚀 FASE 2: TREINO DO CLASSIFICADOR DE GENES (Gene A vs B vs C)")
    print("="*50)
    
    train_loader_mul, val_loader_mul, test_loader_mul = get_dataloaders(args.multi_csv, args.batch_size)
    
    if train_loader_mul:
        multi_model = GeneClassifierCNN(sequence_length=3000).to(device)
        mul_train_loss, mul_val_loss = train_model(multi_model, train_loader_mul, val_loader_mul, epochs=args.epochs, device=device)
        
        print("\n📊 Avaliação FASE 2 (Multiclasse):")
        evaluate_metrics(multi_model, test_loader_mul, device=device)
        
        # Guardar pesos
        torch.save(multi_model.state_dict(), "gene_classifier_weights.pth")
        print("✅ Pesos da Fase 2 guardados em 'gene_classifier_weights.pth'")
    else:
        print("⚠️ Dataset Multiclasse vazio ou inválido.")

    print("\n🎉 Pipeline de Treino em Cascata concluído!")

if __name__ == "__main__":
    main()
