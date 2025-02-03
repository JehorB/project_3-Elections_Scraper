"""
projekt_3.py: třetí projekt do Engeto Online Python Akademie
Elections Scraper

author: Yehor Baranov
email: yhr.baranov@post.cz
"""

import csv
import re
import sys
from time import sleep

from bs4 import BeautifulSoup
import requests

# Kontrola vstupu příkazového řádku / Checks command line arguments
def validate_cmd():
    if len(sys.argv) != 3:
        print(f"Chyba: Očekávány jsou 2 argumenty - název uzemí a název souboru s daty.")
        print(f"Použití: python volby_2017.py <název_uzemí> <vysledky_obec.csv>")
        print(f"Zkuste to znovu")
        sleep(3)
        sys.exit(1)

    cmd_vstup = [arg.strip() for arg in sys.argv[1:]]
    return cmd_vstup

# Kontrola 1.argumentu příkazového řádku / Checks arguments command line arguments
def validate_args_okres(uzemi, okres_dict):
    translit_map = str.maketrans("áčďéěíňóřšťúůýžÚČŠŽ", "acdeeinorstuuyzUCSZ")
    if uzemi in okres_dict:
        return okres_dict[uzemi]
    uzemi_translit = uzemi.translate(translit_map).lower()
    for key, url in okres_dict.items():
        if key.translate(translit_map).lower() == uzemi_translit:
            return url
    
    # Práce s chybou
    first_letter = uzemi[0].lower() # Получаем первую букву введённого округа
    # Фильтруем список округов
    podobne_okresy = [okres for okres in okres_dict if okres.lower().startswith(first_letter)]
    # Выводим список
    if podobne_okresy:
        print("📌 Možná jste mysleli:", ", ".join(podobne_okresy))
    else:
        print("📌 Žádné podobné okresy nenalezeny.")
    sleep(3)
    sys.exit(1)


# Kontrola 2.argumentu příkazového řádku / Checks arguments command line arguments
def validate_args_filename(filename: str) -> str:
    file_name = re.sub(r'[\\/:;"*?<>|]', '_', filename) # Odstranění neplatných znaků
    if not file_name.endswith(".csv"):
        file_name += ".csv"
    return file_name


# Stáhne HTML stránku a vrátí její obsah jako text / Downloads HTML page
def get_html(url):
    headers = {
        "User-Agent":
        ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/109.0.0.0 Safari/537.36")
    }

    try:
        response = requests.get(url, headers=headers)
        # Přidáme pauzu mezi požadavky (zabrání blokaci IP)
        sleep(1)
        if response.status_code != 200:
            print(f"Chyba při načítání stránky ({url}): {response.status_code}")
            sys.exit(1)  # Ukončí program s chybovým kódem 1
        
        return response.text  # Vrací HTML obsah stránky jako text
    
    except requests.exceptions.RequestException as e:
        print(f"Chyba při připojení k URL ({url}): {e}")
        sys.exit(1)  # Ukončí program při síťové chybě


# Načte hlavní stránku, vytvoří seznam url adres na stránky okresu / Loads the home page
def get_okres_url(html):
    soup = BeautifulSoup(html, "html.parser")
    okres_dict = {}
    # Prefix odkazu
    base_url = "https://www.volby.cz/pls/ps2017nss/"
    # Regulární vyhledávací výraz pro <td headers=„t1sa3“ až po t14sa3">
    rows = soup.find_all("tr")
    td_nazev = [row.find("td", attrs={"headers": re.compile(r"t\d+sa1 t\d+sb2")}) for row in rows]
    td_link = [row.find("td", attrs={"headers": re.compile(r"t\d+sa3")}) for row in rows]

    # Získat seznamy měst a URL adres
    if any(td_nazev) and any(td_link):
        mesto = [td.get_text(strip=True) for td in td_nazev if td] # Název okresu
        a_tag = [link.find("a", href=True) for link in td_link if link]  # Odkaz na okres

    # Kontrola délek seznamů
    assert len(mesto) == len(a_tag), "Chyba: seznamy mají různou délku!"

    # Zápis výsledků do slovníku {město: url_adresa}
    for name, tag in zip(mesto, a_tag):
        full_url = base_url + tag["href"]  # Úplný odkaz
        okres_dict[name] = full_url  # Přidání do slovníku
    
    return okres_dict





if __name__ == "__main__":
    cmd_args = validate_cmd()
    uzemi, filename = cmd_args
    filename = validate_args_filename(filename)
    # Odkaz na výsledky voleb
    url_volby_2017 = "https://www.volby.cz/pls/ps2017nss/ps3?xjazyk=CZ"
    html_main = get_html(url_volby_2017)
    okres_urls = get_okres_url(html_main)
    url_uzemi = validate_args_okres(uzemi, okres_urls)
    
    # Testy: zakomentuj před odevzdáním
    print(url_uzemi)
    # print("Stránka byla úspěšně načtena.")
    # print("\nKontrola okresních URL:")
    # for i, (okres, url) in enumerate(okres_urls.items(), start=1):
    #     try:
    #         response = requests.get(url, timeout=5)  # Таймаут 5 секунд
    #         if response.status_code == 200:
    #             print(f"{i}. ✅ {okres}: OK ({url})")
    #         else:
    #             print(f"{i}. ❌ {okres}: CHYBA {response.status_code} ({url})")
    #     except requests.exceptions.RequestException as e:
    #         print(f"{i}. ⚠️ {okres}: Síťová chyba ({url}) ({e})")