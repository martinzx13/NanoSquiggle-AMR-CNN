import torch
from torch.utils.data import Dataset 
import pandas as pd 
import pod5
import numpy as np 
import random
from collections import OrderedDict
import os
import sys

sys.path.append('../utils/')
from normalization import mad_normalization

class Pod5ReaderCache:
    """ 
    An Least recently used method, to ensure that the system will not be overload
    explicity close file handles.
    """
    def __init__(self, max_size=5):
        self.cache = OrderedDict()
        self.max_size = max_size

    def get_reader(self, filepath):
        # Move to the end to show it was recently used.
        if (filepath in self.cache):
            self.cache.move_to_end(filepath)
            return (self.cache[filepath])
        
        # If cache is full evit the oldest and close it.
        if (len(self.cache) > self.max_size):
            oldest_filepath, oldest_reader = self.cache.popitem(last=False)
            oldest_reader.close()
        
        new_reader = pod5.Reader(filepath)
        self.cache[filepath] = new_reader
        return (new_reader)
    
    def close_all(self):
        for reader in self.cache.values():
            reader.close()
        self.cache.clear()

class SquiggleDataset(Dataset):
    def __init__(self, master_csv_path, window_size=3000, is_training=True):
        """
            Phase 1.
            Architechture and indexing, Using a master_csv_path, that will conain 
            read_id, filepath, label.
        """
        self.window_size = window_size
        self.is_training = is_training

        print(f"Loading the precomputed index from {master_csv_path}")

        # The labeling df = panda object.
        self.df = pd.read_csv(master_csv_path)

        self.reader_cache = None

    def __len__(self):
        return(len(self.df))

    def _mad_normalize(self, signal_window:np.ndarray) ->np.ndarray:
        return mad_normalization(signal_window)

    def __getitem__(self, idx):
        """
            Phase 2 : The Loader & Geometry Engine.
        """
        # Initialize cache.
        if self.reader_cache is None:
            self.reader_cache = Pod5ReaderCache(max_size=5)

        # Extrac metadata.
        row = self.df.iloc[idx]
        filepath = row['filepath']
        read_id  = row['read_id']
        label    = row['label']
        
        reader = self.reader_cache.get_reader(filepath)
        read_record = next(reader.reads([read_id]))
        raw_signal = read_record.signal

        # ___ Context management. 

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
        x_tensor = torch.tensor(norm_signal, dtype=torch.float32).unsqueeze(0)
        y_tensor = torch.tensor([label], dtype=torch.float32)

        return (x_tensor, y_tensor)

