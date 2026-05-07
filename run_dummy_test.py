#!/usr/bin/env python3
import torch
from torch.utils.data import TensorDataset, DataLoader

# Importa os teus próprios módulos
from src.models.signal_model import Simple1DCNN
from src.models.train_evaluate import train_model, evaluate_metrics, plot_loss_curve

def run_test_with_dummy_data():
    """
    Executa um ciclo completo de treino e avaliação com dados falsos
    para garantir que a pipeline de ML funciona sem erros.
    """
    print("--- 🚀 INICIANDO TESTE COM DADOS SIMULADOS ---")

    # --- 1. Parâmetros da Simulação (o que o Script 1 e 2 fariam) ---
    SEQUENCE_LENGTH = 3000  # O comprimento de cada janela de sinal
    NUM_SAMPLES = 500       # Número total de amostras (genes + background)
    NUM_CLASSES = 4         # 0: background, 1: gene_A, 2: gene_B, 3: gene_C
    BATCH_SIZE = 32
    EPOCHS = 5              # Usamos poucas épocas, o objetivo é só testar o fluxo

    # --- 2. Geração de Dados Falsos (Simula o Script 1) ---
    print(f"📊 Gerando {NUM_SAMPLES} amostras falsas com comprimento {SEQUENCE_LENGTH}...")
    # Sinais elétricos falsos (números aleatórios)
    dummy_signals = torch.randn(NUM_SAMPLES, SEQUENCE_LENGTH)
    # Etiquetas (labels) falsas (números aleatórios entre 0 e 3)
    dummy_labels = torch.randint(0, NUM_CLASSES, (NUM_SAMPLES,))

    # --- 3. Criação do Dataset e DataLoaders (Simula o Script 2) ---
    print("📦 Criando DataLoaders para treino, validação e teste...")
    dataset = TensorDataset(dummy_signals, dummy_labels)

    # Dividir o dataset falso em 80/15/5
    train_size = int(0.8 * len(dataset))
    val_size = int(0.15 * len(dataset))
    test_size = len(dataset) - train_size - val_size
    train_dataset, val_dataset, test_dataset = torch.utils.data.random_split(dataset, [train_size, val_size, test_size])

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE)
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE)

    # --- 4. Instanciação e Treino do Modelo (O teu Script 3 em ação) ---
    print(" Instanciando o modelo Simple1DCNN...")
    model = Simple1DCNN(sequence_length=SEQUENCE_LENGTH)

    print(f"\n Iniciando treino por {EPOCHS} épocas...")
    train_losses, val_losses = train_model(model, train_loader, val_loader, epochs=EPOCHS)

    print("\n Gerando gráfico de Loss...")
    plot_loss_curve(train_losses, val_losses)

    print("\n Avaliando o modelo no conjunto de teste falso...")
    evaluate_metrics(model, test_loader)

    print("\n--- TESTE CONCLUÍDO COM SUCESSO! ---")

if __name__ == '__main__':
    run_test_with_dummy_data()