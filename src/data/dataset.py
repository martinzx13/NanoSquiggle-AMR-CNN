import torch
from torch.utils.data import Dataset 
import panda as pd 
import pod5
import numpy as np 
import random
import os
import sys

sys.append.path('../utils/normalization.py')
from normalization import mad_normalization

class SquiggleDataset(Dataset):
    def __init__(self, pod5_dir, labels_csv, window_size=3000, is_training=True):
        """
            Phase 1.
            Architechture and indexing.
        """
        self.window_size = window_size
        self.is_training = is_training

        # Dictionary to hold the first handles
        self._open_readers = {}

        # The labeling df = panda object.
        df = pd.read_csv(labels_csv)
        labels_dict = dict(zip(df['read_id'], df['label']))

        self.index_map = []

        # Build the spatial map to the data.
        print("Scanning pod5 files and mapping logical indices to physical address")

        for filename in os.listdir(pod5_dir):
            if (filename.endswith(".pod5")):
                filepath = os.path.join(pod5_dir, filename)

                # Scan the metadata.
                with pod5.Reader(filepath) as reader:
                    for read_id in reader.read_ids:
                        if (read_id in labels_dict):
                            label = labels_dict[read_id]
                            self.index_map.append(filepath, read_id, label)
        print(f"Dataset Compiled : {len(self.index_map)} valid label reads.")

    def __len__(self):
        return(len(self.index_map))
    def _mad_normalize(self, signal_window:np.ndarray) ->np.ndarray:
        return mad_normalization(signal_window)
    def __getitem(self, idx):
        """
            Phase 2 : The Loader & Geometry Engine.
        """
        filepath, read_id, label = self.index_map[idx]

        # ___ Context management. 
        if filepath not in self._open_readers:
            # Is the first time seeing the file.
            self._open_readers[filepath] = pod5.Reader(filepath)
        reader = self._open_readers[filepath]

        # Extract the raw signal array numpy.
        read_record = next(reader.reads([read_id]))
        raw_signal = read_record.signal

        # B -> Lenght window engine.
        L = len(raw_signal)

        if (L >= self.window_size):
            if (self.is_training):
            # Stochastic cropping.
                start_idx = random.randint(0, L - self.window_size)
            else :
                start_idx = 0

            windowed_signal = raw_signal[start_idx:start_idx + self.window_size]
        else :
        # Defensive Geometry: if reads shorter thatn 0, 0 pad it.
            pad_size = self.window_size - L
            windowed_signal = np.pad(raw_signal, (0, pad_size), 'constant', constant_values=0)

        # C -> Math normalization
        norm_signal = self._mad_normalize(windowed_signal)

        # Dimension aligment. 
        # 1D CNN demand (channels, Lenght )
        x_tensor = torch.tensor(norm_signal, dtype=torch.float32).unsqueze(0)
        y_tensor = torch.tensor([label], dtype=torch.float32)

        return (x_tensor, y_tensor)
    def __del__(self):
        # Garbahe Collector, and clossing all open files.
        for reader in self._open_readers.values():
            reader.close()
        
