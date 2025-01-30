"""
projekt_3.py: třetí projekt do Engeto Online Python Akademie
Elections Scraper

author: Yehor Baranov
email: yhr.baranov@post.cz
"""

import csv
import sys

from bs4 import BeautifulSoup
import requests

if len(sys.argv) != 3:
    print(f"Chyba: Očekávány jsou 2 argumenty - název obce a název souboru s daty.")
    print(f"Použití: python volby_2017.py <název_obce> <vysledky_obec.csv>")
    sys.exit(1)

# Stažení obsahu stránky
url = "https://www.volby.cz/pls/ps2017nss/ps3?xjazyk=CZ"
response = requests.get(url)

# Kontrola, jestli požadavek proběhl úspěšně
if response.status_code == 200:
    print("Stránka úspěšně načtena!")
else:
    print(f"Chyba při načítání stránky: {response.status_code}")


