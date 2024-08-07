# Projecte Molecular Docking Estiu 2024

Aquest projecte utilitza un entorn virtual de Python per gestionar les seves dependències. A continuació s'expliquen les instruccions per configurar l'entorn utilitzant dos mètodes diferents: `requirements.txt` i `environment.yml`.

El primer pas, és **entrar al clúster** de confiança. Per a l'execució d'aquest projecte es requereixen recursos computacionals alts per tal de fer-ho amb un temps eficient i tenir suficient memòria. 

## Opció 1: Configuració amb `requirements.txt`

1. **Crea i activa un entorn virtual**:

   - Windows:
     ```bash
     python -m venv dades
     .\dades\Scripts\activate
     ```

   - MacOS/Linux:
     ```bash
     python3 -m venv dades
     source dades/bin/activate
     ```

2. **Instal·la les dependències**:

   Executa el següent comandament per instal·lar les dependències del fitxer `requirements.txt`:

   ```bash
   pip install -r requirements.txt


## Opció 2: Configuració amb 'environment.yml'

1. **Crear l'entorn:**
```
conda env create -f environment.yml
```
2. **Activar l'entorn**
```
conda activate dades
```

# Instruccions per Processar les Dades

A continuació es descriu els passos necessaris per carregar les dades, necessitarem un clúster amb suficients recursos computacionals.

## Passos per a la Creació de Fitxers `pdb_files`

1. **Entrar al clúster que fem servir i activar el environment com hem ensenyat anteriorment**:
2. **Crear els fitxers PDB**:

   Navega fins a la carpeta `pdb_files` i executa el següent comandament per generar els fitxers:

   ```bash
   sbatch exec_pdb.sh
   ```

Una vegada tenim els fitxers pdb ja podem crear els dataloaders sobre els quals podrem recòrrer en batches les dades carregades. 
# Instruccions per a la Creació de Dataloaders

Seguidament, els passos necessaris per generar els dataloaders a partir dels fitxers PDB.

## Creació dels Dataloaders

Un cop tinguis els fitxers PDB, segueix els passos següents per crear els dataloaders necessaris per al model:

1. **Executa els scripts per crear els dataloaders**:

   Navega fins a la carpeta `dataloaders` i executa els següents scripts:

   - Per crear el dataloader de l'esquelet i la cadena lateral:

     ```bash
     sbatch backbone_sidechain.sh
     ```

   - Per crear el dataloader de lligand i esquelet:

     ```bash
     sbatch ligand_backbone.sh
     ```

   - Per crear el dataloader de lligand i proteïna:

     ```bash
     sbatch ligand_protein.sh
     ```
**Caldrà canviar els paths dels fitxers per tal de no obtenir errors d'adreçes**
Amb aquests passos finalment tindrem els dataloaders preparats per al model.



