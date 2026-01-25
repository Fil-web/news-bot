import requests
from bs4 import BeautifulSoup as BS
import json
import pandas as pd

# Базовый URL для парсинга
base_url = "https://zab.ru/news/"

# Получаем содержимое страницы
page = requests.get(base_url)
src = page.text
print(src)

# Сохраняем HTML в файл (для отладки)
# with open("news/parsing.html", "w") as file:
#     file.write(src)

# Читаем HTML из файла (если нужно)
with open("news/parsing.html") as file:
    src = file.read()

# Парсим HTML-код страницы
soup = BS(src, "lxml")

# Ищем все карточки с новостями
news_cards = soup.find_all('a', class_='zab-news__link-main')

# Создаем словарь для хранения данных
news_dict = {}

# Извлекаем информацию и добавляем в словарь
for card in news_cards:
    # Парсим заголовок новости
    title = card.find('h2', class_='zab-news__title-light')
    if title:
        title = title.text.strip()
    else:
        title = "Заголовок не указан"

    # Парсим дату новости
    date = card.find('span', class_='zab-news__info-date')
    if date:
        date = date.text.strip()
    else:
        date = "Дата не указана"

    # Парсим краткое описание новости
    description = card.find('div', class_='zab-news__description')
    if description:
        description = description.text.strip()
    else:
        description = "Описание не указано"

    # Парсим ссылку на новость
    news_href = card.get('href')
    if not news_href:
        news_href = "Ссылка не указана"

    # Выводим результат
    print(f"Заголовок: {title}")
    print(f"Дата: {date}")
    print(f"Описание: {description}")
    print(f"Ссылка: {news_href}")
    print("-" * 50)

    # Добавляем данные в словарь
    news_dict[title] = {
        "Заголовок": title,
        "Дата": date,
        "Описание": description,
        "Ссылка": news_href
    }

# Сохраняем словарь в JSON-файл (для отладки)
with open("database/book.json", "w") as file:
    json.dump(news_dict, file, indent=4, ensure_ascii=False)

# Преобразуем словарь в DataFrame
df = pd.DataFrame.from_dict(news_dict, orient='index')

# Сохраняем DataFrame в Excel-файл
df.to_excel("database/book.xlsx", index=False)

print("Данные успешно сохранены в zab_news.xlsx")