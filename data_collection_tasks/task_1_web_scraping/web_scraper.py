import csv
import json
import requests
from bs4 import BeautifulSoup

# URL сайту для збору новин (використовуємо надійний новинний ресурс)
URL = "https://www.pravda.com.ua/news/"

# Ключові слова для фільтрації (Варіант 1). Якщо залишити список порожнім [], збере всі новини
KEYWORDS = ["ЗСУ", "оборон", "технолог", "дрон", "ППО", "наук", "Україн"]

def scrape_news():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    titles_data = []

    try:
        response = requests.get(URL, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Шукаємо заголовки новин у стандартних тегах заголовків та посилань
        elements = soup.find_all(["h3", "div"], class_=["article_header", "article_title"])
        if not elements:
            elements = soup.find_all(["h1", "h2", "h3"])

        raw_titles = [el.get_text(strip=True) for el in elements if len(el.get_text(strip=True)) > 15]
    except Exception as e:
        print(f"Попередження при підключенні ({e}). Використовуємо демонстраційний набір заголовків:")
        raw_titles = [
            "Нові технології зв'язку впроваджено в підрозділах ОУВ",
            "Українські розробники представили новий розвідувальний дрон",
            "Аналіз логістичного забезпечення за останній місяць",
            "Науковий підхід до автоматизації інформаційно-аналітичного забезпечення",
            "Зведення щодо стану відновлення техніки у визначеній смузі"
        ]

    # Фільтрація за ключовими словами (Варіант 1)
    for idx, title in enumerate(raw_titles, start=1):
        matches_keyword = any(kw.lower() in title.lower() for kw in KEYWORDS) if KEYWORDS else True
        titles_data.append({
            "id": idx,
            "title": title,
            "matches_filter": matches_keyword
        })

    # Якщо потрібно залишити ТІЛЬКИ відфільтровані (або всі, якщо збігів немає):
    filtered_data = [item for item in titles_data if item["matches_filter"]] or titles_data

    # 1. Збереження у CSV-файл (базове завдання)
    csv_file = "news_titles.csv"
    with open(csv_file, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "title", "matches_filter"])
        writer.writeheader()
        writer.writerows(filtered_data)
    print(f"✔ Зібрано заголовків: {len(filtered_data)}. Збережено у {csv_file}")

    # 2. Збереження у JSON-файл (Варіант 5)
    json_file = "news_titles.json"
    with open(json_file, mode="w", encoding="utf-8") as f:
        json.dump(filtered_data, f, ensure_ascii=False, indent=4)
    print(f"✔ Дані також продубльовано у формат JSON: {json_file}")

if __name__ == "__main__":
    scrape_news()