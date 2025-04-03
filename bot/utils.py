def load_html_message(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return "Ошибка: файл с сообщением не найден."
    except Exception as e:
        return f"Ошибка при чтении файла: {e}"