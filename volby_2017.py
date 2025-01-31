"""
projekt_3.py: třetí projekt do Engeto Online Python Akademie
Elections Scraper

author: Yehor Baranov
email: yhr.baranov@post.cz
"""

import csv
import sys
from time import sleep

from bs4 import BeautifulSoup
import requests


# Stáhne HTML stránku a vrátí její obsah jako text / Downloads HTML page
def get_html(url):
    try:
        response = requests.get(url)
        
        # Přidáme pauzu mezi požadavky (zabrání blokaci IP)
        sleep(1)
        
        if response.status_code != 200:
            print(f"Chyba při načítání stránky ({url}): {response.status_code}")
            sys.exit(1)  # Ukončí program s chybovým kódem 1
        
        return response.text  # Vrací HTML obsah stránky jako text
    
    except requests.exceptions.RequestException as e:
        print(f"Chyba při připojení k URL ({url}): {e}")
        sys.exit(1)  # Ukončí program při síťové chybě


# Načte hlavní stránku, vytvoří seznam všech obcí / Loads the home page
def get_obce_list():
    


# Kontroluje argumenty příkazového řádku / Checks command line arguments
# def overit_argumenty(url_seznam_obci)
#     if len(sys.argv) != 3:
#         print(f"Chyba: Očekávány jsou 2 argumenty - název obce a název souboru s daty.")
#         print(f"Použití: python volby_2017.py <název_obce> <vysledky_obec.csv>")
#         print(f"Zkuste to znovu")
#         sleep(3)
#         sys.exit(1)


if __name__ == "__main__":
    # Odkaz na výsledky voleb
    url_volby_2017 = "https://www.volby.cz/pls/ps2017nss/ps3?xjazyk=CZ"
    html_stranka = get_html(url_volby_2017)
    print("Stránka byla úspěšně načtena.")  # Zakomentuj před odevzdáním