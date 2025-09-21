"""
main.py: třetí projekt do Engeto Online Python Akademie

author: Ondřej Petrů
email: ondra.petru@gmail.com
"""

import sys
import requests
from bs4 import BeautifulSoup
import csv
from typing import List, Tuple, Union

BASE_URL = "https://www.volby.cz/pls/ps2017nss/"
DECORATIVE_LINE = "-" * 50


def validate_arguments(args: List[str]) -> Tuple[str, str]:
    if len(args) != 3:
        print(f"{DECORATIVE_LINE}\nChybné množství argumentů. Zadejte:\npython3 main.py <URL> <vystup.csv>\n{DECORATIVE_LINE}")
        sys.exit(1)

    url, output_file = args[1], args[2]
    if not url.startswith(BASE_URL):
        print(f"{DECORATIVE_LINE}\nURL musí začínat {BASE_URL}\n{DECORATIVE_LINE}")
        sys.exit(1)

    if not output_file.endswith(".csv"):
        print(f"{DECORATIVE_LINE}\nVýstupní soubor musí mít příponu .csv\n{DECORATIVE_LINE}")
        sys.exit(1)

    return url, output_file


def get_soup(url: str) -> BeautifulSoup:
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def parse_number(s: str) -> Union[int, float]:
    """Převede český formát čísla (s mezerami a čárkami) na int nebo float."""
    if s is None:
        return None
    s = s.strip().replace("\xa0", "").replace(" ", "")
    if s == "" or s == "-":
        return None
    if "," in s:  # desetinné číslo (procenta)
        return float(s.replace(",", "."))
    return int(s)  # celé číslo


def extract_obec_links(soup: BeautifulSoup) -> List[Tuple[str, str, str]]:
    """Získá odkazy na obce z tabulky."""
    links = []
    for table in soup.find_all("table", {"class": "table"}):
        for row in table.find_all("tr")[2:]:
            cells = row.find_all("td")
            if not cells:
                continue
            code = cells[0].text.strip()
            name = cells[1].text.strip()
            link_tag = cells[0].find("a")
            if link_tag:
                link = BASE_URL + link_tag.get("href")
                links.append((code, name, link))
    return links


def extract_vote_data(soup: BeautifulSoup) -> Tuple[int, int, int, dict, dict]:
    """Získá počet voličů, obálek, platných hlasů a hlasy pro každou stranu."""
    tds = soup.select("#ps311_t1 td")
    voters = parse_number(tds[3].text)
    envelopes = parse_number(tds[4].text)
    valid = parse_number(tds[7].text)

    party_numbers = {}
    party_votes = {}
    party_tables = soup.find_all("div", class_="t2_470")
    for table in party_tables:
        rows = table.find_all("tr")[2:]  # skip header
        for row in rows:
            cells = row.find_all("td")
            if len(cells) < 3:
                continue
            number = parse_number(cells[0].text)
            party = cells[1].text.strip()
            votes = parse_number(cells[2].text)
            if number is None or votes is None:
                continue
            party_numbers[number] = party
            party_votes[party] = votes
    return voters, envelopes, valid, party_numbers, party_votes


def write_csv(filename: str, data: List[dict], headers: List[str]) -> None:
    with open(filename, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)


def main():
    url, output_file = validate_arguments(sys.argv)
    print(f"{DECORATIVE_LINE}\nStahuji data z: {url}\nUkládám do: {output_file}\n{DECORATIVE_LINE}")
    main_soup = get_soup(url)
    obce = extract_obec_links(main_soup)

    results = []
    all_party_numbers = {}

    for code, name, detail_url in obce:
        detail_soup = get_soup(detail_url)
        voters, envelopes, valid, party_numbers, party_votes = extract_vote_data(detail_soup)
        row = {
            "kód obce": code,
            "název obce": name,
            "voliči v seznamu": voters,
            "vydané obálky": envelopes,
            "platné hlasy": valid,
        }
        row.update(party_votes)
        all_party_numbers.update(party_numbers)
        results.append(row)

    headers = ["kód obce", "název obce", "voliči v seznamu", "vydané obálky", "platné hlasy"] + [v for _, v in sorted(all_party_numbers.items(), key=lambda item: item[0])]
    write_csv(output_file, results, headers)
    print(f"{DECORATIVE_LINE}\nHotovo! Výsledky uloženy do {output_file}\n{DECORATIVE_LINE}")


if __name__ == "__main__":
    main()
