#### **1. Observer (Наблюдатель)**
**Цель:** Создать механизм подписки, позволяющий одним объектам следить и реагировать на события, происходящие в других объектах.

```python
class Subject:
    def __init__(self):
        self._observers = []

    def attach(self, observer):
        self._observers.append(observer)

    def detach(self, observer):
        self._observers.remove(observer)

    def notify(self, message):
        for observer in self._observers:
            observer.update(message)

class Observer(ABC):
    @abstractmethod
    def update(self, message: str): pass

class ConcreteObserverA(Observer):
    def update(self, message):
        print(f"ObserverA received: {message}")

class ConcreteObserverB(Observer):
    def update(self, message):
        print(f"ObserverB received: {message}")

# Использование
subject = Subject()
observer_a = ConcreteObserverA()
observer_b = ConcreteObserverB()

subject.attach(observer_a)
subject.attach(observer_b)

subject.notify("Hello Observers!") # Оба наблюдателя получат сообщение
```

**На практике:** В Python часто используют готовые реализации из `RxPY` или простые callback-функции вместо полноценных классов-наблюдателей.

---

