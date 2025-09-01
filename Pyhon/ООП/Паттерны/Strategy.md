#### **2. Strategy (Стратегия)**
**Цель:** Инкапсулировать семейство алгоритмов, сделать их взаимозаменяемыми и позволять выбирать нужный алгоритм во время выполнения.

```python
from abc import ABC, abstractmethod

class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount: int) -> None: pass

class CreditCardPayment(PaymentStrategy):
    def pay(self, amount):
        print(f"Paying ${amount} using Credit Card.")

class PayPalPayment(PaymentStrategy):
    def pay(self, amount):
        print(f"Paying ${amount} using PayPal.")

class Order:
    def __init__(self):
        self._payment_strategy = None

    def set_payment_strategy(self, strategy: PaymentStrategy):
        self._payment_strategy = strategy

    def checkout(self, amount):
        if self._payment_strategy:
            self._payment_strategy.pay(amount)
        else:
            print("No payment method set.")

# Использование
order = Order()
order.set_payment_strategy(CreditCardPayment())
order.checkout(100) # Paying $100 using Credit Card.

order.set_payment_strategy(PayPalPayment())
order.checkout(250) # Paying $250 using PayPal.
```

**В Python:** Часто вместо абстрактных классов используют просто функции (так как функции являются объектами первого класса), что делает паттерн еще более легковесным.

```python
def credit_card_pay(amount):
    print(f"Paying ${amount} using Credit Card.")

def paypal_pay(amount):
    print(f"Paying ${amount} using PayPal.")

order.set_payment_strategy(credit_card_pay)
```

Надеюсь, этот разбор будет полезен для подготовки. Удачи на собеседовании