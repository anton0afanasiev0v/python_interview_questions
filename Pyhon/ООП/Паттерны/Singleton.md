#### **1. Singleton (Одиночка)**

**Как реализовать в Python:**

*   **Через метакласс (наиболее "правильный" ООП-способ):**
    ```python
    class SingletonMeta(type):
        _instances = {}
        
        def __call__(cls, *args, **kwargs):
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
            return cls._instances[cls]

    class Database(metaclass=SingletonMeta):
        def __init__(self, connection_url):
            self.connection_url = connection_url
            # ... инициализация соединения ...

    # Использование
    db1 = Database("postgresql://localhost:5432")
    db2 = Database("another_url")  # Будет проигнорировано, вернет тот же instance, что и db1
    print(db1 is db2)  # True
    ```

*   **Через декоратор (более питоничный и гибкий):**
    ```python
    def singleton(cls):
        instances = {}
        def wrapper(*args, **kwargs):
            if cls not in instances:
                instances[cls] = cls(*args, **kwargs)
            return instances[cls]
        return wrapper

    @singleton
    class AppConfig:
        def __init__(self):
            self.settings = {}

    config1 = AppConfig()
    config2 = AppConfig()
    print(config1 is config2)  # True
    ```

*   **Через модуль (самый простой и часто лучший способ в Python).** Модули в Python по своей природе являются синглтонами. Просто создайте нужный объект в модуле (например, `config.py` или `database.py`), и импортируйте его отовсюду.

**Почему это часто антипаттерн:**

1.  **Глобальное состояние:** Синглтон вводит глобальные переменные в ООП-обертке, что усложняет понимание потока данных и приводит к скрытым зависимостям между компонентами.
2.  **Нарушение принципа единственной ответственности:** Класс начинает отвечать и за свою бизнес-логику, и за контроль своего жизненного цикла.
3.  **Проблемы с тестированием:** Невозможно изолировать тесты, так как синглтон хранит состояние между ними. Приходится сбрасывать его состояние перед каждым тестом, что ломает инкапсуляцию.
4.  **Наследование:** Паттерн сложно расширять через наследование.

**Когда использовать:** Крайне редко. Например, для логирования (где глобальное состояние не так страшно) или для кешей, где единственный экземпляр действительно нужен. Чаще всего **Dependency Injection** — лучшее решение.