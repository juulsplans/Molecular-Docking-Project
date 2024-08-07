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

class Preprocessament_LB:
    def process_pdb_file(self, file_path):
        atom_data = []
        hetatm_data = []

        with open(file_path, 'r') as file:
            for line in file:
                if line.startswith('ATOM'):
                    columns = [
                        float(line[30:38].strip()),  # X coordinate
                        float(line[38:46].strip()),  # Y coordinate
                        float(line[46:54].strip()),  # Z coordinate
                    ]
                    if line[12:16].strip() in ['CA', 'N', 'O', 'C']:
                        atom_data.append(columns)

                elif line.startswith('HETATM'):
                    hetatm_data.append([
                        int(line[6:11].strip()),  # Atom serial number
                        line[12:16].strip(),  # Atom name
                        line[17:20].strip(),  # Residue name
                        line[21].strip(),  # Chain identifier
                        int(line[22:26].strip()),  # Residue sequence number
                        float(line[30:38].strip()),  # X coordinate
                        float(line[38:46].strip()),  # Y coordinate
                        float(line[46:54].strip()),  # Z coordinate
                        float(line[54:60].strip()),  # Occupancy
                        float(line[60:66].strip()),  # Temperature factor
                        line[76:78].strip()  # Element symbol
                    ])

        # Crear DataFrames per a les dades
        atom_df = pd.DataFrame(atom_data, columns=['X', 'Y', 'Z'])
        hetatm_df = pd.DataFrame(hetatm_data, columns=[
            'Serial', 'Atom', 'Residue', 'Chain', 'ResidueSeq', 'X', 'Y', 'Z', 'Occupancy', 'TempFactor', 'Element'
        ])

        return atom_df, hetatm_df

    def encode_categorical_columns(self, df, columns):
        """Codifica columnes categòriques a numèriques."""
        for col in columns:
            df[col] = pd.factorize(df[col])[0]
        return df

    def main_function(self, file_path):
        # Processem cada fitxer independentment
        atom_df, hetatm_df = self.process_pdb_file(file_path)

        categorical_columns = ['Atom', 'Residue', 'Chain', 'ResidueSeq', 'Element']
        df_encoded_hetatm = self.encode_categorical_columns(hetatm_df.copy(), categorical_columns)

        return atom_df, df_encoded_hetatm

class SimpleDataset(Dataset):
    def __init__(self, file_paths):
        self.file_paths = file_paths
        self.pdb_processor = Preprocessament_LB()
        # Processar fitxers en paral·lel utilitzant ProcessPoolExecutor
        self.processed_data = self._preprocess_files(file_paths)

    def _preprocess_files(self, file_paths):
        """ Processa els fitxers en paral·lel utilitzant ProcessPoolExecutor """
        results = []
        with ProcessPoolExecutor(max_workers=4) as executor:
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
        atom_df, df_encoded_hetatm = self.processed_data[idx]

        labels = torch.tensor(atom_df.values, dtype=torch.float32)
        data = torch.tensor(df_encoded_hetatm.drop(columns=['X', 'Y', 'Z']).values, dtype=torch.float32)

        sample = {'features': data, 'label': labels}
        return sample

# Directori de fitxers PDB
# modificar segons convingui
directory_path = '/home/jplans/Molecular-Docking-Project/pdb_files/pdb_files'

# Llistem tots els fitxers dins de la carpeta especificada
files_paths = [os.path.join(directory_path, f) for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]

# Crear el dataset i DataLoader
dataset = SimpleDataset(files_paths)
dataloader = DataLoader(dataset, batch_size=1, shuffle=True)  # un fitxer x batch

# Exemple d'ús del DataLoader
for i, batch in enumerate(dataloader):
    X = batch['features'][0]  
    y = batch['label'][0]
    print(f'Batch {i} - Features: {X}')
    print(f'Batch {i} - Labels: {y}')
