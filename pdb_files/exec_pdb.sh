#!/bin/bash
#SBATCH --job-name=pdb_dataload
#SBATCH --output=pdb_dataload_%j.log
#SBATCH --error=pdb_dataload_%j.err
#SBATCH --time=07:00:00
#SBATCH --partition=compute
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --partition gpu_short 
#SBATCH --qos=short_gpu


python pdb_files/carrega_pdbind.py
