#  Volby.cz Scraper

## Popis
Tento projekt slouží ke scrapování volebních výsledků z webu [volby.cz](https://www.volby.cz). Program stáhne informace pro všechny obce v daném územním celku a uloží je do CSV souboru.

## Instalace
Doporučeno je použití virtuálního prostředí:

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Použití
Soubor se spouští pomocí 2 arguemntů:
- `<odkaz-na-uzemni-celek>` - odkaz na územní celek který chcete scrapovat (př. [územní celek Prostějov](https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103))
- `<vystupni-soubor>` - jméno výstupního souboru

```bash
python main.py <odkaz-na-uzemni-celek> <vystupni-soubor>
```
