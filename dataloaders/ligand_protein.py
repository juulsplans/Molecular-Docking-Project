import torch 
import pandas as pd 
import json
import numpy as np 
import os 
import re
import torch
from torch.utils.data import DataLoader, TensorDataset, Dataset 
from concurrent.futures import ThreadPoolExecutor 
from torch.nn.utils.rnn import pad_sequence 
from sklearn.preprocessing import LabelEncoder 
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed
from concurrent.futures import ProcessPoolExecutor

class Preprocessament_LP:
    def process_pdb_file(self, file_path):
        data = []
        with open(file_path, 'r') as file:
            for line in file:
                if line.startswith('HETATM'):
                    columns = [
                        line[12:16].strip(),  # Atom name
                        line[17:20].strip(),  # Residue name
                        line[21].strip(),  # Chain identifier
                        line[22:26].strip(),  # Residue sequence number
                        float(line[30:38].strip()),  # X coordinate
                        float(line[38:46].strip()),  # Y coordinate
                        float(line[46:54].strip()),  # Z coordinate
                        float(line[54:60].strip()),  # Occupancy
                        float(line[60:66].strip()),  # Temperature factor
                        line[76:78].strip(),  # Element symbol
                        self.extract_protein_name(file_path)
                    ]

                    if columns[0] != 'O' and columns[1] != 'HOH':
                        data.append(columns)

        # Crear DataFrame per a les dades
        df = pd.DataFrame(data, columns=['Atom', 'Residue', 'Chain', 'ResidueSeq', 'X', 'Y', 'Z', 'Occupancy', 'TempFactor', 'Element', 'Protein'])
        return df

    def extract_protein_name(self, file_path):
        return os.path.basename(file_path).split('_')[0]

    def encode_categorical_columns(self, df, columns):
        """Codifica columnes categòriques a numèriques."""
        for col in columns:
            df[col] = pd.factorize(df[col])[0]
        return df

    def main_function(self, file_path):
        # Primer carreguem el pdb com un dataframe
        dataframe = self.process_pdb_file(file_path)
        # Transformem les columnes categòriques a numèriques per així poder fer tensors
        categorical_columns = ['Atom', 'Residue', 'Chain', 'ResidueSeq', 'Protein', 'Element']
        df_encoded = self.encode_categorical_columns(dataframe.copy(), categorical_columns)
        return df_encoded

class SimpleDataset(Dataset):
    def __init__(self, file_paths):
        self.file_paths = file_paths
        self.pdb_processor = Preprocessament_LP()
        # Processar fitxers en paral·lel utilitzant ThreadPoolExecutor
        self.processed_data = self._preprocess_files(file_paths)

    def _preprocess_files(self, file_paths):
        """ Processa els fitxers en paral·lel utilitzant ThreadPoolExecutor """
        results = []
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_file = {executor.submit(self.pdb_processor.main_function, file_path): file_path for file_path in file_paths}
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as exc:
                    print(f'{file_path} generated an exception: {exc}')
        return results

    def __len__(self):
        return len(self.file_paths)

    def __getitem__(self, idx):
        df_encoded = self.processed_data[idx]
        
        data = torch.tensor(df_encoded.iloc[:, :-1].values, dtype=torch.float32)
        labels = torch.tensor(df_encoded.iloc[:, -1].values, dtype=torch.float32)

        sample = {'features': data, 'label': labels}
        return sample

# Directori de fitxers PDB
directory_path = 'def_trajectories/pdb_files/'

# Llistem tots els fitxers dins de la carpeta especificada
files_paths = [os.path.join(directory_path, f) for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]

# Crear el dataset i DataLoader
dataset = SimpleDataset(files_paths[:600])
dataloader = DataLoader(dataset, batch_size=1, shuffle=True, num_workers=2)  # num_workers > 0 per paral·lelitzar la càrrega de dades

# Exemple d'ús del DataLoader
for i, batch in enumerate(dataloader):
    X = batch['features'][0]  # [1, 100, 10]
    y = batch['label'][0]
    print(f'Batch {i} - Features: {X}')
    print(f'Batch {i} - Labels: {y}')

