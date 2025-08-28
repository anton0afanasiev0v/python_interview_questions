<details><summary>🔥 Основы Python</summary>

---

<details><summary>Какие типы данных существуют в Python?</summary>

В Python типы данных можно классифицировать по их изменяемости и упорядоченности.

**Изменяемость**  
- **Изменяемые**: `list`, `set`, `dict`  
- **Неизменяемые**: `int`, `float`, `complex`, `str`, `tuple`, `frozenset`

**Упорядоченность**  
- **Упорядоченные**: `list`, `str`, `tuple`, `dict` (с Python 3.7+)  
- **Неупорядоченные**: `set`, `frozenset`

**Доп. вопрос: может ли tuple быть ключом в словаре?**  
Да, если все элементы кортежа также неизменяемые.
</details>

<details><summary>Какой объект не может быть ключом в словаре (dict)?</summary>

Ключами `dict` могут быть **только неизменяемые** типы данных.  
**Не могут быть ключами**: `list`, `set`, `dict`.

**Могут быть ключами**: `int`, `float`, `str`, `tuple` (если его элементы неизменяемы).
</details>

<details><summary>Как словарь (dict) и множество (set) реализованы внутри?</summary>

- **Реализация**: хэш-таблицы (открытая адресация)  
- **Сложность**:  
  - лучший случай — `O(1)`  
  - худший случай — `O(n)`  
- **Память**: `O(n)` + резерв для минимизации коллизий
</details>

<details><summary>Что такое контекстный менеджер и для чего он нужен?</summary>

Контекстный менеджер — объект с методами `__enter__` и `__exit__`, который создаёт временный контекст и **гарантированно освобождает ресурсы** (файлы, сетевые соединения, блокировки и т.д.) даже при возникновении исключений.

**Пример:**  
```python
with open('file.txt') as f:
    data = f.read()
```
После выхода из блока `with` файл автоматически закроется.
</details>

<details><summary>Декоратор</summary>

Декоратор — функция-обёртка, которая **расширяет поведение** другой функции без изменения её кода.  
```python
def timer(func):
    def wrapper(*args, **kwargs):
        start = time.now()
        result = func(*args, **kwargs)
        print(time.now() - start)
        return result
    return wrapper
```
Использование: `@timer` перед функцией.
</details>

<details><summary>Декоратор с параметрами</summary>

Добавляется **дополнительный уровень вложенности**:
```python
def repeat(n):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for _ in range(n):
                func(*args, **kwargs)
        return wrapper
    return decorator

@repeat(3)
def greet(name):
    print(f"Привет, {name}")
```
</details>

<details><summary>Что такое итератор?</summary>

Итератор — объект, реализующий методы `__iter__()` и `__next__()`, позволяющий **последовательно обходить элементы** коллекции без раскрытия её внутреннего устройства.

```python
class MyIter:
    def __iter__(self):
        self.n = 0
        return self
    def __next__(self):
        if self.n < 3:
            self.n += 1
            return self.n
        raise StopIteration
```
</details>

<details><summary>Что такое генератор?</summary>

Генератор — функция, содержащая ключевое слово `yield`, которая **возвращает объект-генератор** и **лениво** выдаёт элементы по одному.

```python
def gen(n):
    for i in range(n):
        yield i
```
**Преимущества**: экономия памяти, ленивые вычисления, работа с бесконечными последовательностями.

**Генераторное выражение**:  
```python
squares = (x*x for x in range(5))
```
</details>

<details><summary>Практическая задача: {i for i in [1,2,3]} vs (i …) vs [i …]</summary>

- `{i for i in [1,2,3]}` → **множество** `{1,2,3}` (уникальные, неупорядоченные)  
- `(i for i in [1,2,3])` → **генератор** (ленивый, экономит память)  
- `[i for i in [1,2,3]]` → **список** `[1,2,3]` (упорядоченный, полностью в памяти)
</details>

<details><summary>Что такое замыкания (closure)?</summary>

Замыкание — функция, которая **запоминает переменные из внешнего лексического окружения**, даже после завершения внешней функции.

```python
def outer(x):
    def inner(y):
        return x + y
    return inner

add5 = outer(5)
print(add5(2))  # 7
```

**UnboundLocalError** возникает, если внутри вложенной функции пытаемся изменить свободную переменную без `nonlocal`.
</details>

<details><summary>Что такое SOLID?</summary>

| Буква | Принцип                            | Кратко |
|-------|------------------------------------|--------|
| S     | Single Responsibility               | у класса одна причина для изменения |
| O     | Open/Closed                         | открыт для расширения, закрыт для изменения |
| L     | Liskov Substitution                 | подклассы должны заменять базовые классы |
| I     | Interface Segregation               | клиенты не должны зависеть от неиспользуемых методов |
| D     | Dependency Inversion                | зависимости от абстракций, а не от конкретных классов |
</details>

<details><summary>Задача «что не так?» — изменяемый аргумент по умолчанию</summary>

```python
def f(data=[]):
    data.append(1)
    return data
```
**Проблема**: `data` создаётся **один раз** при определении функции.  
**Решение**:
```python
def f(data=None):
    if data is None:
        data = []
    data.append(1)
    return data
```
</details>

<details><summary>Как передаются аргументы в функции: по значению или по ссылке?</summary>

В Python **передаётся ссылка на объект** (call-by-object-reference).  
- **Изменяемые объекты** (`list`, `dict`) – изменения видны снаружи.  
- **Неизменяемые объекты** (`int`, `str`) – присваивание внутри функции создаёт новый объект.
</details>

<details><summary>Какие функции из collections и itertools вы используете?</summary>

- `collections.defaultdict(list)` — словарь со значением по умолчанию  
- `collections.Counter` — счётчик элементов  
- `collections.namedtuple` — именованный кортеж  
- `itertools.chain` — соединение итераторов  
- `itertools.groupby` — группировка подряд идущих элементов  
- `itertools.combinations/permutations`
</details>

<details><summary>Python — императивный или декларативный язык?</summary>

Python — **императивный** (последовательные команды).  
Декларативные примеры: SQL, HTML.
</details>

<details><summary>@classmethod и @staticmethod</summary>

- `@classmethod` – получает `cls` (класс), работает с атрибутами класса.  
- `@staticmethod` – не получает `self`/`cls`, обычная функция внутри класса.
</details>

<details><summary>__new__ vs __init__</summary>

- `__new__` – **создаёт** экземпляр (статический метод).  
- `__init__` – **инициализирует** уже созданный экземпляр.
</details>

<details><summary>Что такое Garbage Collector в Python?</summary>

- **Основной механизм** – подсчёт ссылок.  
- **Дополнительно** – циклический сборщик для разрешения циклических ссылок.  
- Управление через модуль `gc`.
</details>

<details><summary>lambda-функция</summary>

Анонимная однострочная функция:
```python
add = lambda x, y: x + y
```
Ограничена одним выражением, возвращает результат автоматически.
</details>

<details><summary>Иерархия исключений</summary>

- `BaseException`
  - `SystemExit`, `KeyboardInterrupt`, `GeneratorExit`
  - `Exception`
    - `StopIteration`, `ArithmeticError`, `AttributeError`, `OSError`, `RuntimeError`, `SyntaxError`, `ValueError`, …
</details>

<details><summary>Тернарный оператор</summary>

```python
result = value_if_true if condition else value_if_false
```
</details>

<details><summary>== vs is</summary>

- `==` – сравнение **значений**.  
- `is` – сравнение **идентичности объектов** (один и тот же адрес в памяти).
</details>

<details><summary>Аннотации типов</summary>

```python
def greet(name: str) -> str:
    return f"Привет, {name}"
```
Помогают IDE и статическим анализаторам находить ошибки.
</details>

<details><summary>List Comprehension</summary>

```python
squares = [x**2 for x in range(10) if x % 2 == 0]
```
Кратко создаёт список на основе существующего итерируемого объекта.
</details>

<details><summary>list vs tuple</summary>

| list | tuple |
|------|-------|
| изменяемый | неизменяемый |
| [] | () |
| медленнее | быстрее |
</details>

<details><summary>set vs tuple</summary>

| set | tuple |
|-----|-------|
| неупорядоченный | упорядоченный |
| уникальные элементы | дубликаты разрешены |
| изменяемый | неизменяемый |
</details>

<details><summary>*args и **kwargs</summary>

- `*args` – произвольное количество **позиционных** аргументов (кортеж).  
- `**kwargs` – произвольное количество **именованных** аргументов (словарь).
</details>

<details><summary>globals() и locals()</summary>

- `globals()` – словарь всех глобальных переменных.  
- `locals()` – словарь локальных переменных текущей области видимости.
</details>

<details><summary>Метод id()</summary>

Возвращает **уникальный идентификатор** (адрес в памяти) объекта.
</details>

<details><summary>__init__</summary>

Конструктор экземпляра; вызывается **после создания объекта** для инициализации его атрибутов.
</details>

<details><summary>Docstring</summary>

Строка документации сразу после заголовка `def`/`class`:
```python
def foo():
    """Однострочное описание."""
```
</details>

<details><summary>Слайс (slice)</summary>

```python
seq[start:stop:step]
```
Позволяет извлекать подпоследовательности.
</details>

<details><summary>Поверхностное vs глубокое копирование</summary>

- `copy.copy()` – **поверхностная** копия (новый контейнер, но вложенные объекты общие).  
- `copy.deepcopy()` – **полная** копия (включая вложенные объекты).
</details>

<details><summary>Как просмотреть методы объекта?</summary>

```python
dir(obj)
```
или `help(obj)`.
</details>

<details><summary>Арены памяти</summary>

Блоки памяти в `pymalloc`, которые эффективно выделяют/освобождают **малые объекты**, снижая фрагментацию.
</details>

---

</details>

<details><summary>⚡ Асинхронность</summary>

---

<details><summary>Async vs Threads vs Processes</summary>

- **Многопроцессность** – несколько процессов, **CPU-bound**, обходит GIL.  
- **Многопоточность** – потоки в одном процессе, **I/O-bound**, GIL ограничивает CPU.  
- **Асинхронность** – один поток, **Event Loop**, **I/O-bound**, максимально эффективно при большом количестве операций ввода-вывода.
</details>

<details><summary>async/await</summary>

- `async def` – корутина.  
- `await` – передача управления Event Loop, пока операция выполняется.
</details>

<details><summary>Future vs Coroutine vs Task</summary>

- **Coroutine** – функция `async def`.  
- **Task** – обёртка `asyncio.create_task(coroutine)` для запуска в Event Loop.  
- **Future** – низкоуровневый объект, представляющий **результат будущей операции**.
</details>

---

</details>

<details><summary>🗃 SQL</summary>

---

<details><summary>ACID</summary>

- **A**tomicity – «всё или ничего».  
- **C**onsistency – база переходит из одного корректного состояния в другое.  
- **I**solation – параллельные транзакции не мешают друг другу.  
- **D**urability – изменения сохраняются после успешного коммита.
</details>

<details><summary>JOIN-ы</summary>

- **INNER** – только совпадающие строки.  
- **LEFT** – все строки левой таблицы + совпадения правой.  
- **RIGHT** – наоборот.  
- **FULL** – все строки из обеих таблиц; отсутствия заполняются `NULL`.
</details>

<details><summary>Индексы и B-tree</summary>

- **B-tree** – сбалансированное дерево, `O(log n)` на поиск/вставку/удаление.  
- Виды: B-tree, Hash, Bitmap, Full-text, Spatial.
</details>

<details><summary>M2M (многие-ко-многим)</summary>

Создаётся **связующая таблица** с двумя внешними ключами:
```sql
CREATE TABLE book_author (
    book_id  INT REFERENCES books(id),
    author_id INT REFERENCES authors(id),
    PRIMARY KEY (book_id, author_id)
);
```
</details>

<details><summary>Недостатки индексов</summary>

1. Занимают дополнительное место.  
2. Замедляют INSERT/UPDATE/DELETE.  
3. Плохо выбранные индексы могут не ускорять, а замедлять.
</details>

---

</details>

<details><summary>🐳 Docker</summary>

---

<details><summary>Docker Compose</summary>

YAML-файл `docker-compose.yml` описывает все сервисы, тома, сети.  
Команды:  
- `docker-compose up -d` – запуск.  
- `docker-compose down` – остановка и удаление контейнеров.
</details>

<details><summary>Типовые проблемы</summary>

- Раздутые образы → используйте `alpine`, многоэтапные сборки.  
- Сети → `docker network create`, `docker network connect`.  
- Безопасность → проверка образов, сканирование уязвимостей.  
- Мониторинг → `cAdvisor`, `Prometheus`, `ELK`.
</details>

<details><summary>Оптимизация образов</summary>

- Базовый образ `alpine`.  
- Объединение RUN-команд, очистка кеша (`--no-cache`).  
- Многоэтапная сборка (`FROM … as builder`).
</details>

<details><summary>Оркестрация</summary>

- **Kubernetes** – масштабирование, rolling update, service mesh.  
- **Docker Swarm** – упрощённая альтернатива.  
- **Amazon ECS / EKS**, **Google GKE**, **Azure AKS**.
</details>

---

</details>

<details><summary>📂 Git</summary>

---

<details><summary>git fetch vs pull</summary>

- `fetch` – **только скачивает** изменения, не мержит.  
- `pull` – `fetch` + `merge`.
</details>

<details><summary>merge vs rebase</summary>

- `merge` – создаёт **коммит слияния**, сохраняет историю веток.  
- `rebase` – переносит коммиты, делая историю **линейной**, но переписывает SHA.
</details>

<details><summary>Git-flow</summary>

- Ветки: `master`, `develop`, `feature/**`, `hotfix/**`, `release/**`.  
- Теги на релизы.  
- Нейминг: `dev/feat/task-123`, `hotfix/bug-456`.
</details>

<details><summary>cherry-pick</summary>

Перенос отдельного коммита в другую ветку без полного слияния:
```bash
git cherry-pick <commit-sha>
```
</details>

---

</details>

<details><summary>🌐 HTTP / REST</summary>

---

<details><summary>HTTP-методы</summary>

- `GET` – чтение.  
- `POST` – создание.  
- `PUT` – полное обновление (идемпотентно).  
- `PATCH` – частичное обновление.  
- `DELETE` – удаление.  
- `HEAD`, `OPTIONS`, `CONNECT`.
</details>

<details><summary>Статус-коды</summary>

- 2xx – успешно.  
- 3xx – перенаправление.  
- 4xx – ошибка клиента.  
- 5xx – ошибка сервера.
</details>

<details><summary>REST-принципы</summary>

1. Клиент-сервер.  
2. Stateless.  
3. Кэширование.  
4. Единообразный интерфейс (стандартные HTTP-методы).  
5. Многоуровневая система.
</details>

---

</details>