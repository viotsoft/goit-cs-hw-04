def search_keywords_in_file(filepath, keywords):
    result = {}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().lower()  # Перетворюємо весь текст у нижній регістр
        for keyword in keywords:
            if keyword.lower() in content:  # Порівнюємо також у нижньому регістрі
                result.setdefault(keyword, []).append(filepath)
    except Exception as e:
        print(f"Помилка при обробці файлу {filepath}: {e}")
    return result
