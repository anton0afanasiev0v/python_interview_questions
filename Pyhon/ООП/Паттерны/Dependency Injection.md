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

**Dependency Injection (DI)** в FastAPI — это мощный механизм для управления зависимостями, обеспечения тестируемости и поддержания чистоты кода.

## Основы Dependency Injection в FastAPI

### 1. Простая зависимость
```python
from fastapi import FastAPI, Depends

app = FastAPI()

# Функция-зависимость
def get_db_connection():
    return "Database connection established"

@app.get("/items/")
async def read_items(db: str = Depends(get_db_connection)):
    return {"message": db, "data": "some items"}
```

### 2. Зависимости с параметрами
```python
from typing import Annotated
from fastapi import Depends, Query

def pagination_params(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    return {"skip": skip, "limit": limit}

@app.get("/users/")
async def get_users(
    params: Annotated[dict, Depends(pagination_params)]
):
    return f"Skip: {params['skip']}, Limit: {params['limit']}"
```

## Классы как зависимости

### 3. Класс-зависимость
```python
class UserService:
    def __init__(self):
        self.users = ["Alice", "Bob", "Charlie"]
    
    def get_users(self):
        return self.users
    
    def add_user(self, user: str):
        self.users.append(user)
        return user

def get_user_service():
    return UserService()

@app.get("/class-users/")
async def get_class_users(
    service: Annotated[UserService, Depends(get_user_service)]
):
    return {"users": service.get_users()}
```

### 4. Сокращенная форма (без фабрики)
```python
class AuthService:
    def __init__(self, token: str = Query(...)):
        self.token = token
    
    def verify_token(self):
        return self.token == "secret-token"

@app.get("/secure/")
async def secure_route(
    auth: Annotated[AuthService, Depends()]
):
    if not auth.verify_token():
        return {"error": "Invalid token"}
    return {"message": "Access granted"}
```

## Многоуровневые зависимости

### 5. Вложенные зависимости
```python
def get_db():
    return "DB Connection"

def get_user_repository(db: Annotated[str, Depends(get_db)]):
    return f"UserRepository using {db}"

def get_user_service(
    repo: Annotated[str, Depends(get_user_repository)]
):
    return f"UserService using {repo}"

@app.get("/nested/")
async def nested_demo(
    service: Annotated[str, Depends(get_user_service)]
):
    return {"service": service}
```

## Практические примеры

### 6. Аутентификация и авторизация
```python
from fastapi import HTTPException, Header
from typing import Annotated

async def verify_token(
    authorization: Annotated[str, Header()] = None
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    token = authorization[7:]
    if token != "secret":
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return {"user_id": 1, "username": "john_doe"}

@app.get("/profile/")
async def user_profile(
    current_user: Annotated[dict, Depends(verify_token)]
):
    return {"user": current_user}
```

### 7. Валидация данных
```python
from pydantic import BaseModel

class ItemCreate(BaseModel):
    name: str
    price: float
    description: str = None

def validate_item(
    item: ItemCreate,
    min_price: float = Query(0.0)
):
    if item.price < min_price:
        raise HTTPException(
            status_code=400,
            detail=f"Price must be at least {min_price}"
        )
    return item

@app.post("/items/")
async def create_item(
    valid_item: Annotated[ItemCreate, Depends(validate_item)]
):
    return {"item": valid_item.dict(), "status": "created"}
```

## Продвинутые техники

### 8. Кеширование зависимостей
```python
from fastapi import Depends
from functools import lru_cache

@lru_cache()
def get_config():
    print("Loading configuration...")
    return {"db_url": "postgresql://localhost", "debug": True}

@app.get("/config/")
async def get_configuration(
    config: Annotated[dict, Depends(get_config)]
):
    return config
```

### 9. Зависимости для фоновых задач
```python
def get_email_service():
    class EmailService:
        def send_email(self, to: str, subject: str):
            return f"Email sent to {to}: {subject}"
    return EmailService()

@app.post("/notify/")
async def send_notification(
    email_service: Annotated[any, Depends(get_email_service)],
    message: str
):
    result = email_service.send_email("user@example.com", message)
    return {"result": result}
```

### 10. Глобальные зависимости (на уровне приложения)
```python
app = FastAPI(dependencies=[Depends(verify_token)])

# Или для конкретного роута
@app.get("/admin/", dependencies=[Depends(verify_token)])
async def admin_panel():
    return {"message": "Admin panel"}
```

## Тестирование с зависимостями

### 11. Mocking зависимостей в тестах
```python
from fastapi.testclient import TestClient

client = TestClient(app)

# Переопределение зависимости для тестов
def override_get_db():
    return "Mock DB Connection"

app.dependency_overrides[get_db] = override_get_db

def test_read_items():
    response = client.get("/items/")
    assert response.status_code == 200
    assert "Mock DB Connection" in response.json()["message"]
```

## Преимущества Dependency Injection в FastAPI

1. **Тестируемость** - Легко подменять реализации
2. **Чистота кода** - Разделение ответственности
3. **Повторное использование** - Общие зависимости для разных эндпоинтов
4. **Безопасность** - Централизованная обработка аутентификации
5. **Валидация** - Единый подход к проверке данных

Dependency Injection делает код FastAPI более модульным, поддерживаемым и простым для тестирования.