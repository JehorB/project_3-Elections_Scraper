"""
projekt_3.py: třetí projekt do Engeto Online Python Akademie
Elections Scraper

author: Yehor Baranov
email: yhr.baranov@post.cz
"""

import csv
import re
import sys
from pathlib import Path
from time import sleep

from bs4 import BeautifulSoup
import requests

def get_html(url: str) -> str:
    """
    Stáhne HTML stránku a vrátí její obsah jako text.

    Parametry:
        url (str): URL adresa stránky.

    Návratová hodnota:
        str: HTML obsah stránky jako text nebo None v případě chyby.
    """
    headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/109.0.0.0 Safari/537.36"
            )
    }
    try:
        response = requests.get(url, headers=headers)
        #sleep(1) # Přidáme pauzu mezi požadavky (zabrání blokaci IP)
        if response.status_code != 200:
            print(f"Chyba při načítání stránky ({url}): {response.status_code}")
            sys.exit(1)  # Ukončí program s chybovým kódem 1
        
        return response.text  # Vrací HTML obsah stránky jako text
    
    except requests.exceptions.RequestException as e:
        print(f"Chyba při připojení k URL ({url}): {e}")
        sys.exit(1)  # Ukončí program při síťové chybě

def get_okres_url(html: str) -> dict:
    """
    Analyzuje HTML a extrahuje URL adresy jednotlivých okresů.

    Parametry:
        html (str): HTML obsah stránky.

    Návratová hodnota:
        dict: Slovník, kde klíčem je název okresu a hodnotou jeho URL adresa.
    """
    soup = BeautifulSoup(html, "html.parser")
    okres_dict = {}
    base_url = "https://www.volby.cz/pls/ps2017nss/" # Prefix odkazu
    rows = soup.find_all("tr")
    td_nazev = [
        row.find("td", attrs={"headers": re.compile(r"t\d+sa1 t\d+sb2")})
        for row in rows
    ]
    td_link = [
        row.find("td", attrs={"headers": re.compile(r"t\d+sa3")})
        for row in rows
    ]
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

def validate_cmd() -> list:
    """
    Funkce kontroluje, zda jsou předány přesně dva argumenty příkazového řádku.
    Pokud ne, vypíše chybovou zprávu a ukončí program.
    Jinak vrátí seznam těchto dvou argumentů po odstranění přebytečných mezer.

    Parametry:
        Žádné

    Návratová hodnota:
        Funkce kontroluje, zda jsou předány přesně dva argumenty příkazového řádku.
        Pokud ne, vypíše chybovou zprávu a ukončí program.
        Jinak vrátí seznam těchto dvou argumentů po odstranění přebytečných mezer.
    """
    if len(sys.argv) != 3:
        print(f"Chyba: Očekávány jsou 2 argumenty - název uzemí a název souboru s daty.")
        print(f"Použití: python volby_2017.py <název_uzemí> <vysledky_obec.csv>")
        print(f"Zkuste to znovu")
        sleep(3)
        sys.exit(1)

    cmd_vstup = [arg.strip() for arg in sys.argv[1:]]
    return cmd_vstup

def transliterate_input(text: str) -> str:
    """
    Transliterace vstupního textu.

    Parametry:
        text (str): Řetězec, který má být transliterován.

    Návratová hodnota:
        str: Transliterovaný a zmenšený řetězec.

    Tato funkce bere vstupní řetězec a transliteruje české znaky 
    na jejich odpovídající ASCII znaky. Výsledný řetězec je převeden
    na malá písmena.

    Příklad:
        >>> transliterate_input("Česká republika")
        'ceska republika'
    """
    translit_map = str.maketrans("áčďéěíňóřšťúůýžÚČŠŽ", "acdeeinorstuuyzUCSZ")
    return text.translate(translit_map).lower()

def validate_args_okres(uzemi: str, okres_dict: dict) -> str:
    """
    Kontrola 1.argumentu příkazového řádku.

    Parametry:
        uzemi (str): Název území, který má být zkontrolován.
        okres_dict (dict): Slovník obsahující mapování názvů území na jejich odpovídající URL.

    Návratová hodnota:
        str: URL odpovídající zadanému názvu území.

    Tato funkce překládá zadaný název území do ASCII znaků a 
    porovnává ho se slovenskými názvy v `okres_dict`. Pokud nalezne shodu, 
    vrátí odpovídající URL. Pokud ne, nabídne možné podobné názvy a ukončí program.

    Příklad:
        >>> uzemi = "Praha"
        >>> okres_dict = {"Praha": "url1", "Brno": "url2"}
        >>> validate_args_okres(uzemi, okres_dict)
        'url1'
    """
    uzemi = transliterate_input(uzemi)
    for key, url in okres_dict.items():
        if transliterate_input(key) == uzemi:
            return url
    
    # Práce s chybou
    first_letter = uzemi[0].lower()
    podobne_okresy = [okres for okres in okres_dict if okres.lower().startswith(first_letter)]
    if podobne_okresy:
        print("Možná jste mysleli:", ", ".join(podobne_okresy))
    else:
        print("Žádné podobné okresy nenalezeny.")
    sleep(3)
    sys.exit(1)

def validate_args_filename(filename: str) -> str:
    """
    Kontrola 2.argumentu příkazového řádku.

    Parametry:
        filename (str): Název souboru, který má být zkontrolován.

    Návratová hodnota:
        str: Upravený název souboru s příponou .csv.

    Tato funkce kontroluje zadaný název souboru, odstraňuje všechny 
    neplatné znaky a přidává příponu .csv, pokud tam není. Výsledkem 
    je bezpečný název souboru, který lze použít k ukládání dat.

    Příklad:
        >>> validate_args_filename("vysledky/obec:Praha.csv")
        'vysledky_obec_Praha.csv'
    """
    file_name = re.sub(r'[\\/:;"*?<>|]', '_', filename) # Odstranění neplatných znaků
    if not file_name.endswith(".csv"):
        file_name += ".csv"
    return file_name

def get_obce_urls(url: str) -> dict:
    """
    Vytvoří seznam URL adres na stránky s výsledků.

    Parametry:
        url (str): URL adresa hlavní stránky, ze které se budou načítat data.

    Návratová hodnota:
        dict: Slovník, kde klíčem je URL adresa obce a hodnotou je dvojice (číslo, název obce).

    Tato funkce načte HTML obsah z dané URL, parsuje ho pomocí knihovny BeautifulSoup 
    a vytváří slovník, který obsahuje URL adresy jednotlivých obcí a jejich odpovídající 
    čísla a názvy. Neplatné znaky jsou odstraněny a v případě nesouladu délek seznamů 
    je vyvolána chyba.

    Příklad:
        >>> get_obce_urls("https://www.volby.cz/pls/ps2017nss/ps3?xjazyk=CZ")
        {
            'https://www.volby.cz/pls/ps2017nss/url1': ('1', 'Praha'),
            'https://www.volby.cz/pls/ps2017nss/url2': ('2', 'Brno'),
            ...
        }
    """
    html = get_html(url)
    soup = BeautifulSoup(html, "html.parser")
    obce_dict = {}
    base_url = "https://www.volby.cz/pls/ps2017nss/" # Prefix odkazu
    rows = soup.find_all("td", attrs={"headers": re.compile(r"t\d+sa1")})
    for i in range(0, len(rows), 2):
        td_number = rows[i]
        td_name = rows[i + 1] if i + 1 < len(rows) else None
        a_tag = td_number.find("a")
        if a_tag and td_name:
            number = a_tag.text.strip()
            link = base_url + a_tag["href"]
            name_tag = td_name.find("a")
            name = name_tag.text.strip() if name_tag else td_name.get_text(strip=True) 
            # Kontrola délek seznamů
            assert number and link and name, "Chyba: seznamy mají různou délku!"
            obce_dict[link] = (number, name)
    return obce_dict

def result_election(obce_hlasy: dict) -> dict:
    """
    Načte a zpracuje výsledky voleb z URL adres jednotlivých obcí.

    Parametry:
        obce_hlasy (dict): Slovník, kde klíčem je URL adresa obce a hodnotou je její název.

    Návratová hodnota:
        dict: Slovník, kde klíčem je název obce a hodnotou je slovník obsahující 
              "Celkový počet", "Celkové hlasy", "Strany" a "Hlasy".

    Tato funkce iteruje přes slovník obce_hlasy, načte HTML obsah z každé URL, 
    parsuje ho pomocí BeautifulSoup a extrahuje potřebné informace:
    celkový počet, celkové hlasy, strany a hlasy. Tyto informace jsou následně 
    uloženy ve slovníku vyber_dict, kde klíčem je název obce a hodnotou je slovník s informacemi.

    Příklad:
        >>> obce_hlasy = {'url1': 'Praha', 'url2': 'Brno'}
        >>> result_election(obce_hlasy)
        {
            'Praha': {
                'Celkový počet': [...],
                'Celkové hlasy': [...],
                'Strany': [...],
                'Hlasy': [...],
            },
            'Brno': {
                'Celkový počet': [...],
                'Celkové hlasy': [...],
                'Strany': [...],
                'Hlasy': [...],
            },
        }
    """
    vyber_dict = {}
    for url, obec in obce_hlasy.items():
        html = get_html(url)
        #sleep(0.3)
        soup = BeautifulSoup(html, "html.parser")
        celkovy_pocet = [
            " ".join(th.stripped_strings)
            for th in soup.find_all("th", attrs={"data-rel":"L1"})
            if th.get("id") != "sa5"
        ]
        celkovy_hlasy = [
            td.get_text(strip=True).replace("\xa0", " ").strip()
            for td in soup.find_all("td", attrs={"data-rel":"L1"})
            if "sa5" not in td.get("headers") != "sa5"
        ]
        strana = [td.get_text(strip=True) for td in soup.select("td.overflow_name")]
        hlasy = [
            td.get_text(strip=True)
            for td in soup.find_all("td", class_="cislo", attrs={
                "headers": re.compile(r"t\d+sb3")}
            )
        ]
        vyber_dict[obec] = {
            "Celkový počet": celkovy_pocet,
            "Celkové hlasy": celkovy_hlasy,
            "Strany": strana,
            "Hlasy": hlasy,
        }
    return vyber_dict

def write_to_csv(volby: dict, filename: str) -> str:
    """
    Zapisuje výsledky voleb do CSV souboru.

    Parametry:
        volby (dict): Slovník obsahující výsledky voleb pro jednotlivé obce.
        filename (str): Název souboru, do kterého budou data zapsána.

    Návratová hodnota:
        str: Potvrzující zpráva o úspěšném uložení souboru.

    Tato funkce zapisuje výsledky voleb zadané ve slovníku `volby` do 
    CSV souboru s názvem `filename`. Neplatné znaky v názvu souboru jsou 
    nahrazeny podtržítkem a k názvu souboru je připojena přípona .csv, 
    pokud tam není. Funkce vytvoří složku "data_csv", pokud neexistuje, 
    a uloží výsledky do souboru v této složce.
    """
    folder = Path("data_csv") # Vytvoření objektu cesty k složce "data_csv"
    folder.mkdir(parents=True, exist_ok=True) # Vytvoří složku, pokud neexistuje
    file_path = folder / filename  # Vytvoření úplné cesty k souboru
    
    all_parties = list(dict.fromkeys(
        party for obec in volby for party in volby[obec]["Strany"]
        )
    )
    fieldnames = [
        "číslo", "obec", "voliči v seznamu",
        "vydané obálky", "platné hlasy"] + all_parties

    with open(file_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, dialect='excel')
        writer.writeheader()
        for (cislo, obec), data in volby.items():
            row = {
                "číslo": cislo,
                "obec": obec,
                "voliči v seznamu": data["Celkové hlasy"][0],  
                "vydané obálky": data["Celkové hlasy"][1],  
                "platné hlasy": data["Celkové hlasy"][2]
            }
            # Vyplňování hlasů podle stran
            for party in all_parties:
                if party in data["Strany"]:
                    index = data["Strany"].index(party)
                    row[party] = data["Hlasy"][index]
                else:
                    row[party] = "0"
            writer.writerow(row)
    return f"Soubor '{filename}' je uložen do složky '{folder}'"

def parse_zahranici(url: str) -> dict:
    """
    Načte a zpracuje výsledky voleb pro území Zahraničí.

    Parametry:
        url (str): URL adresa hlavní stránky, ze které se budou načítat data.

    Návratová hodnota:
        dict: Slovník, kde klíčem je URL adresa obce a hodnotou je dvojice (země, město).

    Tato funkce načte HTML obsah z dané URL, parsuje ho pomocí knihovny BeautifulSoup 
    a vytváří slovník, který obsahuje URL adresy jednotlivých obcí a jejich odpovídající 
    země a města. Při parsování se kontroluje, zda délky všech seznamů odpovídají, 
    a případně se vypisuje seznam možných hodnot.

    Příklad:
        >>> parse_zahranici("https://www.volby.cz/pls/ps2017nss/ps3?xjazyk=CZ")
        {
            'https://www.volby.cz/pls/ps2017nss/url1': ('USA', 'New York'),
            'https://www.volby.cz/pls/ps2017nss/url2': ('Kanada', 'Toronto'),
            ...
        }
    """
    print("Spouštím speciální scraping pro Zahraničí...")
    html = get_html(url)
    zahranici_dict ={}
    base_url = "https://www.volby.cz/pls/ps2017nss/" # Prefix odkazu
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.select("tr")

    # Seznam států
    td_zeme = [row.find("td", attrs={"headers": "s2"}) for row in rows]
    if td_zeme and td_zeme[0] is None:
        td_zeme.pop(0)
    # Nahradit None předchozím Tag
    last_valid_value = None
    for i, td in enumerate(td_zeme):
        if td is not None:
            last_valid_value = td
        else:
            td_zeme[i] = last_valid_value

    # Seznam měst
    td_mesto = [row.find("td", attrs={"headers": "s3"}) for row in rows]
    if td_mesto and td_mesto[0] is None:
        td_mesto.pop(0)

    # Seznam URL odkazů
    td_link = [row.find("td", attrs={"headers": "s4"}) for row in rows]
    if td_link and td_link[0] is None:
        td_link.pop(0)

    # Kontrola délek seznamů
    assert len(td_zeme) == len(td_mesto) == len(td_link), "Chyba: seznamy mají různou délku!"

    # Vytvoření slovníku
    for tg_zeme, tg_mesto, tg_link in zip(td_zeme, td_mesto, td_link):
        a_tag_zeme = tg_zeme.find("a")
        zeme = a_tag_zeme.text.strip() if a_tag_zeme else tg_zeme.get_text(strip=True)
        mesto = tg_mesto.get_text(strip=True)
        a_tag_link = tg_link.find("a")
        if a_tag_link:
            link = base_url + a_tag_link["href"]
            zahranici_dict[link] = (zeme, mesto)
    
    return zahranici_dict

def main():
    # Odkaz na výsledky voleb
    url_volby_2017 = "https://www.volby.cz/pls/ps2017nss/ps3?xjazyk=CZ"
    cmd_args = validate_cmd()
    html_main = get_html(url_volby_2017)
    okres_urls = get_okres_url(html_main)
    uzemi, filename = cmd_args
    url_uzemi = validate_args_okres(uzemi, okres_urls)
    name_csv = validate_args_filename(filename)
    obce_urls = (
        parse_zahranici(url_uzemi) if url_uzemi in okres_urls.values()
        and url_uzemi == okres_urls.get("Zahraničí")
        else get_obce_urls(url_uzemi)
    )
    volby = result_election(obce_urls)
    print(f"Všechna data jsou připravena pro zápis do {name_csv}")
    sleep(3)
    finale = write_to_csv(volby, name_csv)
    print(finale)
    sleep(3)
    
    

if __name__ == "__main__":
    main()