# Elections Scraper

## Popis projektu

Tento projekt je webový scraper pro sběr dat o volbách v České republice v roce 2017. Pomocí Pythonu a knihovny BeautifulSoup skript extrahuje informace o výsledcích hlasování a ukládá je ve formátu CSV.

## Instalace

### 1. Klonování repozitáře

```sh
git clone https://github.com/JehorB/project_3-Elections_Scraper
```

### 2. Vytvoření a aktivace virtuálního prostředí

```sh
python -m venv venv
source venv/bin/activate  # pro Linux/macOS
venv\Scripts\activate    # pro Windows
```

### 3. Instalace závislostí

```sh
pip install -r requirements.txt
```

## Použití

### Spuštění skriptu

```sh
python volby_2017.py <název_uzemí> <vysledky_obec.csv>
```

Příklad:

```sh
python volby_2017.py "Plzeň-město" vysledky_plzen.csv
```

Skript stáhne výsledky voleb z daného olkresu a uloží je do souboru CSV.

## Struktura projektu

```
├── volby_2017.py       # Hlavní skript pro sběr dat
├── requirements.txt    # Závislosti projektu
├── data_csv/           # Složka pro ukládání CSV souborů s data
├── README.md           # Popis projektu
├── LICENSE             # Licence
```

## Závislosti

- Python 3.8+
- BeautifulSoup4
- Requests

## Licence

Tento projekt je licencován pod licencí MIT. Další informace naleznete v souboru LICENSE.

### Autor
* [Yehor Baranov](https://github.com/JehorB)