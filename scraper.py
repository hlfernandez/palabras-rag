import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import argparse

def main(output_dir):
    today = datetime.today()
    date_str = today.strftime('%Y_%m_%d')

    filename = f"palabras_{date_str}.txt"
    file_path = os.path.join(output_dir, filename)

    if os.path.exists(file_path):
        print(f"El archivo {file_path} ya existe. No se escribirá nada.")
        return

    url = 'https://academia.gal/dicionario'

    response = requests.get(url)
    html_content = response.content

    soup = BeautifulSoup(html_content, 'html.parser')

    top_searches_div = soup.find('div', id='_com_ideit_ragportal_liferay_dictionary_TopSearchsPortlet_INSTANCE_kzkg_')

    if top_searches_div:
        week_list = top_searches_div.find('ul', class_='dictionary-topsearch__list--week')

        words = [item.find('a').text for item in week_list.find_all('li', class_='dictionary-topsearch__item')]

        with open(file_path, 'w', encoding='utf-8') as file:
            for word in words:
                file.write(f"{word}\n")
        print(f"Las palabras más buscadas han sido escritas en {file_path}")
    else:
        print("No se encontró el div específico.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Descargar las palabras más buscadas y guardarlas en un archivo.')
    parser.add_argument('output_dir', type=str, help='Directorio donde se guardará el archivo.')

    args = parser.parse_args()

    main(args.output_dir)
