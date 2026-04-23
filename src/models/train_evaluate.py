import torch
import torch.nn as nn
import torch.optim as optim
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, f1_score

def train_model(model, train_loader, val_loader, epochs=20, lr=0.001, device='cpu'):
    """
    Treina o modelo multiclasse (4 classes) e regista a evolução da Loss.
    """
    model.to(device)
    
    # CrossEntropyLoss é a standard para Multiclasse. 
    # No PyTorch, ela JÁ APLICA o Softmax internamente aos logits brutos!
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    train_losses = []
    val_losses = []

    for epoch in range(epochs):
        # --- MODO DE TREINO ---
        model.train()
        running_train_loss = 0.0
        
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            
            optimizer.zero_grad()
            
            # Outputs será um tensor de tamanho [Batch_size, 4]
            outputs = model(inputs) 
            
            # Labels têm de ser do tipo inteiro/long (0, 1, 2 ou 3)
            loss = criterion(outputs, labels.long())
            
            loss.backward()
            optimizer.step()
            
            running_train_loss += loss.item()
            
        avg_train_loss = running_train_loss / len(train_loader)
        train_losses.append(avg_train_loss)

        # --- MODO DE VALIDAÇÃO ---
        model.eval()
        running_val_loss = 0.0
        
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                
                outputs = model(inputs)
                loss = criterion(outputs, labels.long())
                running_val_loss += loss.item()
                
        avg_val_loss = running_val_loss / len(val_loader)
        val_losses.append(avg_val_loss)

        print(f"Epoch [{epoch+1}/{epochs}] | Train Loss: {avg_train_loss:.4f} | Val Loss: {avg_val_loss:.4f}")

    return train_losses, val_losses

def plot_loss_curve(train_losses, val_losses):
    """
    Gera um gráfico com a avaliação da Loss ao longo do treino.
    """
    plt.figure(figsize=(10, 6))
    plt.plot(train_losses, label='Train Loss', color='blue')
    plt.plot(val_losses, label='Validation Loss', color='red')
    plt.title('Evolução da Loss ao longo do Treino')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)
    plt.show()

def evaluate_metrics(model, test_loader, device='cpu'):
    """
    Calcula Accuracy e F1-Score no dataset de teste para as 4 classes.
    """
    model.to(device)
    model.eval()
    
    all_preds = []
    all_labels = []

    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs = inputs.to(device)
            
            # 1. Obter outputs (logits) -> [Batch, 4]
            outputs = model(inputs)
            
            # 2. Aplicar Softmax para converter logits em probabilidades para cada classe
            probs = torch.softmax(outputs, dim=1)
            
            # 3. Escolher a classe com a probabilidade mais alta (argmax)
            preds = torch.argmax(probs, dim=1)
            
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.numpy())

    # Em multiclasse, temos de usar average='macro' (calcula o F1 para cada classe e faz a média)
    # ou average='weighted' (tem em conta o desbalanceamento das classes).
    acc = accuracy_score(all_labels, all_preds)
    f1 = f1_score(all_labels, all_preds, average='macro')

    print("-" * 40)
    print("Avaliação Final no Test Set (Multiclasse):")
    print(f"Accuracy: {acc * 100:.2f}%")
    print(f"F1-Score (Macro): {f1 * 100:.2f}%")
    print("-" * 40)
    
    return acc, f1