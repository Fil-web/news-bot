import requests

def ask_gigachat(question: str, api_key: str) -> str:
    """
    Отправляет запрос к API GigaChat и возвращает ответ.
    
    :param question: Вопрос пользователя.
    :param api_key: API-ключ для доступа к GigaChat.
    :return: Ответ от GigaChat.
    """
    url = "https://developers.sber.ru/portal/products/gigachat-api"  # Пример URL API GigaChat
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo",  # Укажите модель, если требуется
        "messages": [{"role": "user", "content": question}]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Проверка на ошибки
        result = response.json()
        return result["choices"][0]["message"]["content"]  # Возвращаем ответ
    except Exception as e:
        return f"Ошибка при запросе к GigaChat: {e}"