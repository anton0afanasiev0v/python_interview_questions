<details><summary>Функции map, filter и reduce в Python</summary>

Эти функции являются важными инструментами функционального программирования в Python и часто используются в backend-разработке.

## 1. `map(function, iterable)`
Применяет функцию к каждому элементу итерируемого объекта.

```python
numbers = [1, 2, 3, 4]
squared = map(lambda x: x**2, numbers)
print(list(squared))  # [1, 4, 9, 16]
```

**Особенности**:
- Возвращает итератор (в Python 3)
- Ленивое вычисление (элементы вычисляются по мере необходимости)
- Альтернатива: генераторные выражения `(x**2 for x in numbers)`

## 2. `filter(function, iterable)`
Фильтрует элементы, оставляя только те, для которых функция возвращает True.

```python
numbers = [1, 2, 3, 4, 5, 6]
evens = filter(lambda x: x % 2 == 0, numbers)
print(list(evens))  # [2, 4, 6]
```

**Особенности**:
- Также возвращает итератор
- Если функция None, фильтрует по "истинности" элементов
- Альтернатива: `[x for x in numbers if x % 2 == 0]`

## 3. `reduce(function, iterable[, initializer])`
Последовательно применяет функцию к элементам, сводя их к единственному значению.

```python
from functools import reduce

numbers = [1, 2, 3, 4]
product = reduce(lambda x, y: x * y, numbers)
print(product)  # 24 (1*2*3*4)
```

**Особенности**:
- Требует импорта из `functools` (в Python 3)
- Может принимать начальное значение
- Альтернатива: цикл с аккумулятором

## Практическое применение в backend

1. **Обработка данных API**:
```python
# Преобразование данных от клиента
user_ids = map(int, request.json.get('user_ids', []))
```

2. **Фильтрация запросов**:
```python
# Фильтрация активных пользователей
active_users = filter(lambda u: u.is_active, users)
```

3. **Агрегация данных**:
```python
# Сумма заказов
total = reduce(lambda acc, order: acc + order.total, orders, 0)
```

## Сравнение с другими подходами

1. **Генераторы списков**:
   - Читаемее для простых операций
   - Создают список сразу (не ленивые)

2. **Циклы**:
   - Более явные, но многословные
   - Легче добавлять сложную логику

Для senior-разработчика важно понимать, когда использовать эти функции, а когда предпочесть другие подходы, учитывая читаемость и производительность кода.

</details>
