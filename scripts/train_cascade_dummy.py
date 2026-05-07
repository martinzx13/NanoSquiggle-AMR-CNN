#!/usr/bin/env python3
import torch
import sys
import os
from torch.utils.data import TensorDataset, DataLoader

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.models.cnn_2 import BinaryDetectorCNN, GeneClassifierCNN
from src.models.train_evaluate import train_model, evaluate_metrics

def run_cascade_dummy_test():
    """
    Executa um ciclo de treino fictício para a Pipeline em Cascata
    garantindo que os modelos Binary e Multiclass funcionam corretamente.
    """
    print("--- 🚀 INICIANDO TESTE COM DADOS FALSOS (CASCATA) ---")

    SEQUENCE_LENGTH = 3000
    NUM_SAMPLES = 400
    BATCH_SIZE = 32
    EPOCHS = 2  # Poucas épocas apenas para validar se o código não "estoira"

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"🖥️ Dispositivo selecionado: {device}")

    # ==========================================
    # 1. TESTE FASE 1: BINÁRIO (0 vs 1)
    # ==========================================
    print("\n" + "="*50)
    print("🧪 FASE 1: A TESTAR O DETETOR BINÁRIO (Ruído vs Gene)")
    print("="*50)

    # Gerar dados falsos para binário (Labels 0 e 1)
    dummy_signals_bin = torch.randn(NUM_SAMPLES, SEQUENCE_LENGTH)
    dummy_labels_bin = torch.randint(0, 2, (NUM_SAMPLES,)) # 0 ou 1

    dataset_bin = TensorDataset(dummy_signals_bin, dummy_labels_bin)
    train_size = int(0.8 * len(dataset_bin))
    val_size = int(0.15 * len(dataset_bin))
    test_size = len(dataset_bin) - train_size - val_size
    
    train_ds_bin, val_ds_bin, test_ds_bin = torch.utils.data.random_split(dataset_bin, [train_size, val_size, test_size])
    
    train_loader_bin = DataLoader(train_ds_bin, batch_size=BATCH_SIZE, shuffle=True)
    val_loader_bin = DataLoader(val_ds_bin, batch_size=BATCH_SIZE)
    test_loader_bin = DataLoader(test_ds_bin, batch_size=BATCH_SIZE)

    model_bin = BinaryDetectorCNN(sequence_length=SEQUENCE_LENGTH).to(device)
    train_model(model_bin, train_loader_bin, val_loader_bin, epochs=EPOCHS, device=device)
    
    print("\n📊 Avaliação Fase 1 Fictícia:")
    evaluate_metrics(model_bin, test_loader_bin, device=device)

    # ==========================================
    # 2. TESTE FASE 2: MULTICLASSE (0 vs 1 vs 2)
    # ==========================================
    print("\n" + "="*50)
    print("🧪 FASE 2: A TESTAR O CLASSIFICADOR MULTICLASSE (3 Genes)")
    print("="*50)

    # Gerar dados falsos para multiclasse (Labels 0, 1 e 2)
    dummy_signals_mul = torch.randn(NUM_SAMPLES, SEQUENCE_LENGTH)
    dummy_labels_mul = torch.randint(0, 3, (NUM_SAMPLES,)) # 0, 1 ou 2

    dataset_mul = TensorDataset(dummy_signals_mul, dummy_labels_mul)
    
    train_ds_mul, val_ds_mul, test_ds_mul = torch.utils.data.random_split(dataset_mul, [train_size, val_size, test_size])
    
    train_loader_mul = DataLoader(train_ds_mul, batch_size=BATCH_SIZE, shuffle=True)
    val_loader_mul = DataLoader(val_ds_mul, batch_size=BATCH_SIZE)
    test_loader_mul = DataLoader(test_ds_mul, batch_size=BATCH_SIZE)

    model_mul = GeneClassifierCNN(sequence_length=SEQUENCE_LENGTH).to(device)
    train_model(model_mul, train_loader_mul, val_loader_mul, epochs=EPOCHS, device=device)
    
    print("\n📊 Avaliação Fase 2 Fictícia:")
    evaluate_metrics(model_mul, test_loader_mul, device=device)

    print("\n✅ TUDO OK! A arquitetura em Cascata não tem erros de código e pode ser usada no Colab com dados reais.")

if __name__ == '__main__':
    run_cascade_dummy_test()
