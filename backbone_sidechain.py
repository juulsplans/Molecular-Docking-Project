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

class Preprocessament_BS:
    def process_pdb_file(self, file_path):
        backbone_data = []
        current_backbone_group = []
        sidechain_data = []
        current_sidechain_group = []

        def process_group(group, group_type=None):
            if group:
                if group_type == 'backbone_data':
                    backbone_data.append(group)
                elif group_type == 'sidechain_data':
                    sidechain_data.append(group)

        with open(file_path, 'r') as file:
            for line in file:
                if line.startswith('ATOM'):
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
                        self.extract_protein_name(file_path)  # Protein
                    ]
                    atom_name = line[12:16].strip()
                    if atom_name in ['CA', 'N', 'O', 'C']:
                        process_group(current_sidechain_group, group_type='sidechain_data')
                        current_sidechain_group = []
                        current_backbone_group.append(columns)
                    else:
                        process_group(current_backbone_group, group_type='backbone_data')
                        current_backbone_group = []
                        current_sidechain_group.append(columns)

        process_group(current_backbone_group, group_type='backbone_data')
        process_group(current_sidechain_group, group_type='sidechain_data')

        atom_name = []
        residue_name = []
        chain_id = []
        residue_seq = []
        elem_sym = []
        protein = []
        for backbone in backbone_data:
            for atom in backbone:
                atom_name.append(atom[0])
                residue_name.append(atom[1])
                chain_id.append(atom[2])
                residue_seq.append(atom[3])
                elem_sym.append(atom[9])
                protein.append(atom[10])

        le_atom = LabelEncoder()
        le_residue = LabelEncoder()
        le_chain_id = LabelEncoder()
        le_residue_seq = LabelEncoder()
        le_elem_sym = LabelEncoder()
        le_protein = LabelEncoder()

        atom_name_encoded = le_atom.fit_transform(atom_name)
        residue_name_encoded = le_residue.fit_transform(residue_name)
        chain_id_encoded = le_chain_id.fit_transform(chain_id)
        residue_seq_encoded = le_residue_seq.fit_transform(residue_seq)
        elem_sym_encoded = le_elem_sym.fit_transform(elem_sym)
        protein_encoded = le_protein.fit_transform(protein)

        encoded_backbone_data = []
        index = 0
        for backbone in backbone_data:
            encoded_backbone = []
            for atom in backbone:
                encoded_atom = [
                    atom_name_encoded[index],
                    residue_name_encoded[index],
                    chain_id_encoded[index],
                    residue_seq_encoded[index],
                    atom[4],  # X coordinate
                    atom[5],  # Y coordinate
                    atom[6],  # Z coordinate
                    atom[7],  # Occupancy
                    atom[8],  # Temperature factor
                    elem_sym_encoded[index],
                    protein_encoded[index]
                ]
                encoded_backbone.append(encoded_atom)
                index += 1
            encoded_backbone_data.append(encoded_backbone)

        backbone_df = pd.DataFrame({
            'Atom Name': [item[0] for sublist in encoded_backbone_data for item in sublist],
            'Residue Name': [item[1] for sublist in encoded_backbone_data for item in sublist],
            'Chain ID': [item[2] for sublist in encoded_backbone_data for item in sublist],
            'Residue Seq': [item[3] for sublist in encoded_backbone_data for item in sublist],
            'X': [item[4] for sublist in encoded_backbone_data for item in sublist],
            'Y': [item[5] for sublist in encoded_backbone_data for item in sublist],
            'Z': [item[6] for sublist in encoded_backbone_data for item in sublist],
            'Occupancy': [item[7] for sublist in encoded_backbone_data for item in sublist],
            'Temp Factor': [item[8] for sublist in encoded_backbone_data for item in sublist],
            'Element Symbol': [item[9] for sublist in encoded_backbone_data for item in sublist],
            'Protein': [item[10] for sublist in encoded_backbone_data for item in sublist]
        })

        sidechain_df = pd.DataFrame({
            'X': [item[4] for sublist in sidechain_data for item in sublist],
            'Y': [item[5] for sublist in sidechain_data for item in sublist],
            'Z': [item[6] for sublist in sidechain_data for item in sublist]
        })
        return backbone_df, sidechain_df

    def extract_protein_name(self, file_path):
        return os.path.basename(file_path).split('_')[0]

    def main_function(self, file_paths):
        all_sidechain_df = pd.DataFrame()
        all_backbone_df = pd.DataFrame()

        with ThreadPoolExecutor() as executor:
            results = list(executor.map(self.process_pdb_file, file_paths))

        for backbone_data, sidechain_data in results:
            all_backbone_df = pd.concat([all_backbone_df, backbone_data], ignore_index=True)
            all_sidechain_df = pd.concat([all_sidechain_df, sidechain_data], ignore_index=True)

        return all_backbone_df, all_sidechain_df


class SimpleDataset(Dataset):
    def __init__(self, file_paths):
        self.file_paths = file_paths
        self.pdb_processor = Preprocessament_BS()

    def __len__(self):
        return len(self.file_paths)

    def __getitem__(self, idx):
        file_path = self.file_paths[idx]
        backbone_data, sidechain_data = self.pdb_processor.process_pdb_file(file_path)
        data = torch.tensor(backbone_data.values, dtype=torch.float32)
        labels = torch.tensor(sidechain_data.values, dtype=torch.float32)
        sample = {'features': data, 'label': labels}
        return sample


directory_path = '/home/jplans/home/def_trajectories/pdb_files/'
files_paths = [os.path.join(directory_path, f) for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]

dataset = SimpleDataset(files_paths)
dataloader = DataLoader(dataset, batch_size=1, shuffle=True)

for i, batch in enumerate(dataloader):
    X = batch['features'][0]
    y = batch['label'][0]
    print(f'Batch {i} - Features: {X}')
    print(f'Batch {i} - Labels: {y}')

