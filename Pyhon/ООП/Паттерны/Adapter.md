#### **1. Adapter (Адаптер)**
**Цель:** Преобразовать интерфейс одного класса в интерфейс, ожидаемый клиентом. Позволяет работать вместе классам с несовместимыми интерфейсами.

```python
# Старая система, которую нужно адаптировать
class OldSystem:
    def specific_request(self) -> str:
        return "data from old system"

# Интерфейс, который ожидает клиент
class NewSystemInterface(ABC):
    @abstractmethod
    def request(self) -> str: pass

# Адаптер
class Adapter(NewSystemInterface):
    def __init__(self, adaptee: OldSystem):
        self.adaptee = adaptee

    def request(self) -> str:
        return f"Adapted: {self.adaptee.specific_request()}"

# Клиентский код ожидает работу с NewSystemInterface
def client_code(target: NewSystemInterface):
    print(target.request())

# Использование
old_system = OldSystem()
adapter = Adapter(old_system)
client_code(adapter)  # Выведет: "Adapted: data from old system"
```

---

