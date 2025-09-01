#### **2. Factory / Abstract Factory (Фабрика / Абстрактная Фабрика)**

*   **Простая Фабрика (Factory Method):** Используется, когда у нас есть один общий интерфейс (базовый класс) и несколько реализаций, а логика выбора конкретного класса должна быть инкапсулирована.
    ```python
    class Notification:
        def send(self): pass

    class EmailNotification(Notification):
        def send(self): print("Sending Email")

    class SMSNotification(Notification):
        def send(self): print("Sending SMS")

    class NotificationFactory:
        @staticmethod
        def get_notification(type_: str) -> Notification:
            if type_ == "email":
                return EmailNotification()
            elif type_ == "sms":
                return SMSNotification()
            else:
                raise ValueError("Unknown notification type")

    # Клиентский код
    notification = NotificationFactory.get_notification("email")
    notification.send()
    ```

*   **Абстрактная Фабрика (Abstract Factory):** Используется, когда нужно создавать *семейства* связанных или зависимых объектов, без привязки к их конкретным классам.

    ```python
    # Абстрактная фабрика и продукты
    class GUIFactory(ABC):
        @abstractmethod
        def create_button(self): pass
        @abstractmethod
        def create_checkbox(self): pass

    class WinFactory(GUIFactory):
        def create_button(self): return WinButton()
        def create_checkbox(self): return WinCheckbox()

    class MacFactory(GUIFactory):
        def create_button(self): return MacButton()
        def create_checkbox(self): return MacCheckbox()

    # Клиентский код
    class Application:
        def __init__(self, factory: GUIFactory):
            self.factory = factory
            self.button = None

        def create_ui(self):
            self.button = self.factory.create_button()

        def paint(self):
            self.button.paint()

    # Конфигурация фабрики в зависимости от ОС
    config = {"os": "windows"}
    if config["os"] == "windows":
        factory = WinFactory()
    else:
        factory = MacFactory()

    app = Application(factory)
    app.create_ui()
    app.paint()
    ```

**Итог:** Use **Factory Method** для создания объектов одного типа, выбор которого зависит от условия. Use **Abstract Factory** для создания целых групп связанных объектов.

---
