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

# Stáhne HTML stránku a vrátí její obsah jako text / Downloads HTML page
def get_html(url):
    headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/109.0.0.0 Safari/537.36"
            )
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
    # Создаём объект BeautifulSoup
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

def transliterate_input(text):
    translit_map = str.maketrans("áčďéěíňóřšťúůýžÚČŠŽ", "acdeeinorstuuyzUCSZ")
    return text.translate(translit_map).lower()

# Kontrola 1.argumentu příkazového řádku / Checks arguments command line arguments
def validate_args_okres(uzemi, okres_dict):
    translit_map = str.maketrans("áčďéěíňóřšťúůýžÚČŠŽ", "acdeeinorstuuyzUCSZ")
    
    for key, url in okres_dict.items():
        if key.translate(translit_map).lower() == uzemi:
            return url
    
    # Práce s chybou
    first_letter = uzemi[0].lower() # Получаем первую букву введённого округа
    # Фильтруем список округов
    podobne_okresy = [okres for okres in okres_dict if okres.lower().startswith(first_letter)]
    # Выводим список
    if podobne_okresy:
        print("Možná jste mysleli:", ", ".join(podobne_okresy))
    else:
        print("Žádné podobné okresy nenalezeny.")
    sleep(3)
    sys.exit(1)

# Kontrola 2.argumentu příkazového řádku / Checks arguments command line arguments
def validate_args_filename(filename: str) -> str:
    file_name = re.sub(r'[\\/:;"*?<>|]', '_', filename) # Odstranění neplatných znaků
    if not file_name.endswith(".csv"):
        file_name += ".csv"
    return file_name

# Vytvoří seznam url adres na stránky s výsledků / Loads url to the results page
def get_obce_urls(html):
    # Создаём объект BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    obce_dict = {}
    # Prefix odkazu
    base_url = "https://www.volby.cz/pls/ps2017nss/"
    # Находим все <td> с номерами городов
    rows = soup.find_all("td", attrs={"headers": re.compile(r"t\d+sa1")})
    for i in range(0, len(rows), 2):  # Проходим по парам (номер, название)
        td_number = rows[i]  # <td> с номером и ссылкой
        td_name = rows[i + 1] if i + 1 < len(rows) else None  # <td> с названием города
        a_tag = td_number.find("a")  # Ищем <a> внутри <td>
        if a_tag and td_name:
            number = a_tag.text.strip()  # Число города
            link = base_url + a_tag["href"]  # Полная ссылка
            # Проверяем, есть ли <a> внутри названия города
            name_tag = td_name.find("a")
            name = name_tag.text.strip() if name_tag else td_name.get_text(strip=True)  # Берём либо <a>.text, либо текст <td>
            # Kontrola délek seznamů
            assert number and link and name, "Chyba: seznamy mají různou délku!"
            obce_dict[link] = (number, name)  # ✅ Теперь link — ключ, а number и name — значения
    return obce_dict

def result_election(obce_hlasy: dict):
    vyber_dict = {}
    for url, obec in obce_hlasy.items():
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/109.0.0.0 Safari/537.36"
            )
        }
        response = requests.get(url, headers=headers)
        sleep(0.3)
        soup = BeautifulSoup(response.text, "html.parser")  # Создаём объект BeautifulSoup
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
        # Записываем в словарь, чтобы было понятно, какие данные к чему относятся
        vyber_dict[obec] = {
            "Celkový počet": celkovy_pocet,
            "Celkové hlasy": celkovy_hlasy,
            "Strany": strana,
            "Hlasy": hlasy,
        }
    return vyber_dict

def write_to_csv(volby, filename):
    folder = Path("data_csv")  # Создаём объект пути
    folder.mkdir(parents=True, exist_ok=True)  # Создаём папку, если её нет
    file_path = folder / filename  # Автоматически соединяет путь
    
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

            # Заполняем голоса по партиям
            for party in all_parties:
                if party in data["Strany"]:
                    index = data["Strany"].index(party)
                    row[party] = data["Hlasy"][index]  # Берём соответствующий голос
                else:
                    row[party] = "0"  # Если партии нет в этом городе, ставим 0

            writer.writerow(row)
    return f"Soubor '{filename}' je uložen do složky '{folder}'"

def parse_zahranici(url):
    print("Spouštím speciální scraping pro Zahraničí...")
    zahranici_dict ={}
    base_url = "https://www.volby.cz/pls/ps2017nss/"
    headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/109.0.0.0 Safari/537.36"
            )
        }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    rows = soup.select("tr")

    # --- 1. Список стран (s2) ---
    td_zeme = [row.find("td", attrs={"headers": "s2"}) for row in rows]
    if td_zeme and td_zeme[0] is None:
        td_zeme.pop(0)

    last_valid_value = None
    for i, td in enumerate(td_zeme):
        if td is not None:
            last_valid_value = td  # Сохраняем Tag
        else:
            td_zeme[i] = last_valid_value  # Заменяем None предыдущим Tag

    # --- 2. Список городов (s3) ---
    td_mesto = [row.find("td", attrs={"headers": "s3"}) for row in rows]
    if td_mesto and td_mesto[0] is None:
        td_mesto.pop(0)

    # --- 3. Список ссылок (s4) ---
    td_link = [row.find("td", attrs={"headers": "s4"}) for row in rows]
    if td_link and td_link[0] is None:
        td_link.pop(0)

    # Проверяем, что длины всех списков совпадают
    assert len(td_zeme) == len(td_mesto) == len(td_link), "Chyba: seznamy mají různou délku!"

    # --- 4. Запись в словарь ---
    for tg_zeme, tg_mesto, tg_link in zip(td_zeme, td_mesto, td_link):
        a_tag_zeme = tg_zeme.find("a")
        zeme = a_tag_zeme.text.strip() if a_tag_zeme else tg_zeme.get_text(strip=True)
        mesto = tg_mesto.get_text(strip=True)  # Город

        a_tag_link = tg_link.find("a")  # Получаем ссылку
        if a_tag_link:
            link = base_url + a_tag_link["href"]
            zahranici_dict[link] = (zeme, mesto)  # Записываем в словарь
    
    return zahranici_dict

def main():
    # Odkaz na výsledky voleb
    url_volby_2017 = "https://www.volby.cz/pls/ps2017nss/ps3?xjazyk=CZ"
    cmd_args = validate_cmd()
    html_main = get_html(url_volby_2017)
    okres_urls = get_okres_url(html_main)
    uzemi, filename = cmd_args
    uzemi_translit = transliterate_input(uzemi)
    url_uzemi = validate_args_okres(uzemi_translit, okres_urls)
    filename = validate_args_filename(filename)
    html_uzemi = get_html(url_uzemi)
    if uzemi_translit == "zahranici":
        obce_urls = parse_zahranici(url_uzemi)
    else:
        obce_urls = get_obce_urls(html_uzemi)
    volby = result_election(obce_urls)
    print(f"Všechna data jsou připravena pro zápis do {filename}")
    sleep(3)
    finale = write_to_csv(volby, filename)
    print(finale)
    sleep(3)
    
    


if __name__ == "__main__":
    main()
    
    # TESTS: zakomentuj před odevzdáním
    # print("Stránka byla úspěšně načtena.")
    # print(okres_urls) # контрольный вывод данных
    # "Kontrola okresních URL:"
    # for i, (url, obec) in enumerate(obce_urls.items(), start=1):
    #     try:
    #         response = requests.get(url, timeout=5)  # Таймаут 5 секунд
    #         if response.status_code == 200:
    #             print(f"{i}. {obec[1]:<12}: OK ({url})")
    #         else:
    #             print(f"{i}. {obec[1]:<12}: CHYBA {response.status_code} ({url})")
    #     except requests.exceptions.RequestException as e:
    #         print(f"{i}. {obec[1]:<12}: Síťová chyba ({url}) ({e})")
    # print([i[1] for i in obce_urls.values()])