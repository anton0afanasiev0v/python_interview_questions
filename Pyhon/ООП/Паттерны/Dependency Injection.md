#### **3. Dependency Injection (Внедрение зависимостей)**

**Суть:** Объект не создает свои зависимости сам, а получает их извне (обычно через конструктор `__init__`). Это превращает жестко закодированные зависимости в гибкие параметры.

**Как реализовать вручную (Pure Python):**

```python
# Без DI: сильная связь, невозможно протестировать
class UserService:
    def __init__(self):
        self.repository = UserRepository()  # Зависимость захардкожена

    def get_user(self, user_id):
        return self.repository.get(user_id)

# С DI: слабая связь, легко тестировать
class UserService:
    def __init__(self, repository: UserRepository):  # Зависимость внедряется
        self.repository = repository

    def get_user(self, user_id):
        return self.repository.get(user_id)

# Где-то в корне приложения (Composition Root) собираем наш граф объектов
repo = UserRepository()
service = UserService(repository=repo)  # Внедряем зависимость

# Тестирование с Mock-объектом
def test_user_service():
    mock_repo = Mock()  # Создаем заглушку
    mock_repo.get.return_value = User("John")
    service = UserService(repository=mock_repo)  # Внедряем заглушку
    user = service.get_user(1)
    assert user.name == "John"
```

**С помощью библиотек (например, `injector`):**
Библиотеки автоматически управляют графом зависимостей.

```python
from injector import inject, Injector, Module, singleton

class UserRepository:
    pass

class UserService:
    @inject
    def __init__(self, repo: UserRepository):
        self.repo = repo

class AppModule(Module):
    def configure(self, binder):
        binder.bind(UserRepository, to=UserRepository, scope=singleton)

# Инжектор сам разрешит зависимости
injector = Injector([AppModule()])
service = injector.get(UserService) # Автоматически создаст UserRepository и передаст его
```

**Вывод:** DI — краеугольный камень чистого, гибкого и тестируемого кода. В Python его часто реализуют вручную, но для больших проектов библиотеки очень помогают.

---

