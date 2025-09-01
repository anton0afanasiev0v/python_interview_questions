#### **2. Facade (Фасад)**
**Цель:** Представить простой унифицированный интерфейс к сложной подсистеме. Не упрощает саму подсистему, а лишь скрывает ее сложность.

```python
# Сложная подсистема
class CPU:
    def start(self): print("CPU started")
class Memory:
    def load(self): print("Memory loaded")
class HardDrive:
    def read(self): print("HardDrive read")

# Простой Фасад
class ComputerFacade:
    def __init__(self):
        self.cpu = CPU()
        self.memory = Memory()
        self.hd = HardDrive()

    def start_computer(self): # Простой метод, скрывающий сложность
        self.cpu.start()
        self.memory.load()
        self.hd.read()
        print("Computer is ready!")

# Клиенту теперь нужно знать только про Фасад
computer = ComputerFacade()
computer.start_computer()
```

---

