import torch
import torch.nn as nn

# num_classes : is the number of classification that the model can do
# 4 classes: 1 background + 3 specific AMR genes

class MambaCNN(nn.Module):
  def __init__(self, in_channels: int =1, d_model:int=128, num_classes:int =4):
    super(MambaCNN, self).__init__()
  # Self Encoder. 3000 -> 750
    self.encoder = nn.Sequential(
      # First Layer : 3000 -> 1500.
      nn.Conv1d(in_channels, 32, kernel_size=3, padding=1),
      nn.BatchNorm1d(32),
      nn.ReLU(),
      nn.MaxPool1d(kernel_size=2),

      # Layer 2 1500 -> 750
      nn.Conv1d(32, 64, kernel_size=3, padding=1),
      nn.BatchNorm1d(64),
      nn.ReLU(),
      nn.MaxPool1d(kernel_size=2),

      # Layer 3: Feature refinement.
      nn.Conv1d(64, d_model, kernel_size=3, padding=1),
      nn.BatchNorm1d(d_model),
      nn.ReLU()
  )
    
    # Global pooling para garantir que o tamanho independentemente do input
    self.pool = nn.AdaptiveAvgPool1d(1)
    
    # Classificador Final para 4 Classes
    self.classifier = nn.Linear(d_model, num_classes)

  def forward(self, x: torch.Tensor) -> torch.Tensor:
      if x.dim() == 2:
          x = x.unsqueeze(1)
      x = self.encoder(x)
      x = self.pool(x).squeeze(-1) # Remove a última dimensão extra
      x = self.classifier(x)
      return x