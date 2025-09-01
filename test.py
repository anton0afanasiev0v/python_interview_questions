class FileManager:
    def __init__(self, filename, mode='r'):
        self.filename = filename
        self.mode = mode
        self.file = None
    
    def __enter__(self):
        self.file = open(self.filename, self.mode)
        return self.file
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()
        # Обработка исключений (необязательно)
        if exc_type is not None:
            print(f"Произошла ошибка: {exc_val}")
        # Возвращаем False, чтобы исключение продолжило распространяться
        # Возвращаем True, чтобы подавить исключение
        return False

# Использование
with FileManager('test.txt', 'w') as f:
    f.write('Hello, World!')