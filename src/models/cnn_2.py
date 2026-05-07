import torch
import torch.nn as nn

class BinaryDetectorCNN(nn.Module):
    """
    Fase 1: Classificação Binária.
    Identifica se a read contém algum gene de resistência ou se é apenas background/ruído.
    Classes: 0 -> Ruído/Background | 1 -> Presença de Gene
    """
    def __init__(self, sequence_length: int):
        super(BinaryDetectorCNN, self).__init__()

        self.feature_extractor = nn.Sequential(
            nn.Conv1d(in_channels=1, out_channels=16, kernel_size=5, stride=1, padding=2),
            nn.BatchNorm1d(16),
            nn.ReLU(),
            nn.MaxPool1d(kernel_size=2),

            nn.Conv1d(in_channels=16, out_channels=32, kernel_size=5, stride=1, padding=2),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.MaxPool1d(kernel_size=2)
        )

        dummy_input = torch.zeros(1, 1, sequence_length)
        with torch.no_grad():
            dummy_output = self.feature_extractor(dummy_input)
        self.flattened_dim = dummy_output.numel()

        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(self.flattened_dim, 64),
            nn.ReLU(),
            nn.Dropout(p=0.5),
            nn.Linear(64, 2)  # Saída para 2 classes (Ruído vs Gene)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if x.dim() == 2:
            x = x.unsqueeze(1)
        x = self.feature_extractor(x)
        return self.classifier(x)


class GeneClassifierCNN(nn.Module):
    """
    Fase 2: Classificação Multiclasse Exclusiva.
    Apenas recebe reads que foram identificadas como POSITIVAS pela Fase 1.
    Classes: 0 -> Gene A | 1 -> Gene B | 2 -> Gene C
    """
    def __init__(self, sequence_length: int):
        super(GeneClassifierCNN, self).__init__()

        self.feature_extractor = nn.Sequential(
            nn.Conv1d(in_channels=1, out_channels=32, kernel_size=5, stride=1, padding=2),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.MaxPool1d(kernel_size=2),

            # Para as diferenças subtis entre genes, podemos usar mais filtros na 2ª camada
            nn.Conv1d(in_channels=32, out_channels=64, kernel_size=5, stride=1, padding=2),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.MaxPool1d(kernel_size=2)
        )

        dummy_input = torch.zeros(1, 1, sequence_length)
        with torch.no_grad():
            dummy_output = self.feature_extractor(dummy_input)
        self.flattened_dim = dummy_output.numel()

        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(self.flattened_dim, 64),
            nn.ReLU(),
            nn.Dropout(p=0.5),
            nn.Linear(64, 3)  # Saída para 3 classes (Os 3 Genes AMR)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if x.dim() == 2:
            x = x.unsqueeze(1)
        x = self.feature_extractor(x)
        return self.classifier(x)