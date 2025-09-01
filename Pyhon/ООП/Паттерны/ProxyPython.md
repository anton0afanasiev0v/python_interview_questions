#### **3. Proxy (Заместитель)**
**Цель:** Объект-заместитель контролирует доступ к другому объекту.

*   **Виртуальный прокси (ленивая загрузка):**
    ```python
    class HeavyObject:
        def __init__(self):
            print("Expensive operation: loading heavy object...")
        def method(self): print("Method called")

    class LazyProxy:
        def __init__(self):
            self._heavy_object = None

        def method(self):
            if self._heavy_object is None: # Инициализация только при первом вызове
                self._heavy_object = HeavyObject()
            return self._heavy_object.method()

    # Использование
    proxy = LazyProxy()
    print("Proxy created") # HeavyObject еще не создан
    proxy.method() # Создается здесь
    ```

*   **Защищающий прокси (контроль доступа):**
    ```python
    class Subject(ABC):
        @abstractmethod
        def request(self): pass

    class RealSubject(Subject):
        def request(self): print("RealSubject: Handling request.")

    class ProtectionProxy(Subject):
        def __init__(self, real_subject: RealSubject, user: str):
            self._real_subject = real_subject
            self._user = user

        def request(self):
            if self._user == "admin":
                self._real_subject.request()
            else:
                print("ProtectionProxy: Access denied.")
    ```

---
