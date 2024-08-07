# Projecte Molecular Docking Estiu 2024

Aquest projecte utilitza un entorn virtual de Python per gestionar les seves dependències. A continuació s'expliquen les instruccions per configurar l'entorn utilitzant dos mètodes diferents: `requirements.txt` i `environment.yml`.

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


