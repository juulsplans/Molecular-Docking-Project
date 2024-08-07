import requests
from bs4 import BeautifulSoup
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

with open('/home/jplans/def_trajectories/downloadfile.htm', 'r', encoding='utf-8') as file:
    content = file.read()

# Analitzar el contingut HTML
soup = BeautifulSoup(content, 'html.parser')

# Trobar tots els enllaços a la pàgina
links = soup.find_all('a')


# URL base per a les descàrregues
base_url = 'http://www.pdbbind.org.cn/v2007/'

# Director per guardar els fitxers descarregats
download_dir = 'home/def_trajectories/pdb_files'

if not os.path.exists(download_dir):
    os.makedirs(download_dir)

# Iterar sobre els enllaços i descarregar els fitxers
def download_file(link):
    file_name = link.get('href').split('/')[-1]
    file_url = link.get('href')
    output_path = os.path.join(download_dir, file_name)
    
    print(f'Downloading {file_url}...')

    try:
        # Descarregar el fitxer
        file_response = requests.get(file_url)
        file_response.raise_for_status()  # Verifica que la descarrega hagi estat exitosa

        # Escriure el contingut del fitxer
        with open(output_path, 'wb') as file:
            file.write(file_response.content)

        print(f'{output_path} downloaded.')
    except requests.exceptions.HTTPError as err:
        print(f'HTTP error occurred: {err}')
    except Exception as err:
        print(f'An error occurred: {err}')


with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(download_file, link) for link in links]

    for future in as_completed(futures):
        try:
            future.result()  
        except Exception as e:
            print(f'Error during download: {e}')

print('All files have been downloaded.')

