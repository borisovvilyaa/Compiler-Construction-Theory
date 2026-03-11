# ЛАБОРАТОРНА РОБОТА № 2
## Побудова лексичного аналізатора на основі регулярних виразів

**Студент:** Борисов Ілля  
**Група:** КН-Н921  
**Варіант:** 7  

---

## 1. Постановка задачі

Побудувати модель лексичного аналізатора на основі регулярних виразів для виділення лексем виразу, що містить конструкції мови програмування з ключовими словами `if` та `else`, ідентифікаторами, числами та роздільниками `( ) { } ;`.

**Приклади вхідних рядків:**

```
if ( expr ){
    stmt1;
}
```

```
if ( expr ){
    stmt;
}
else {
    stmt;
    stmt;
    stmt;
}
```

```
if ( expr ){
    stmt;
    stmt;
}
else if ( expr ){
    stmt;
    stmt;
}
else if ( expr ){
    stmt;
}
else {
    stmt;
    stmt;
    stmt;
}
```

---

## 2. Специфікація токенів

Для розпізнавання лексем визначено набір регулярних виразів, що відповідають кожному типу токена:

| Тип токена | Регулярний вираз | Опис |
|------------|-----------------|------|
| `KEYWORD` | `\b(?:if\|else)\b` | Ключові слова `if` та `else` |
| `IDENTIFIER` | `[A-Za-z_]\w*` | Ідентифікатор: починається з літери або `_` |
| `NUMBER` | `-?\d+(\.\d+)?` | Ціле або дійсне число (зі знаком) |
| `DELIMITER` | `[(){};]` | Роздільники: дужки та крапка з комою |
| `SKIP` | `[ \t\n\r]+` | Пробіли та переноси рядка — відкидаються |
| `ERROR` | `.` | Будь-який нерозпізнаний символ |

**Таблиця 1 — Специфікація токенів лексичного аналізатора (варіант 7)**

---

## 3. Майстер-регулярний вираз

Усі шаблони об'єднуються в один майстер-регекс із іменованими групами за допомогою оператора `|`. Пріоритет груп відповідає порядку в специфікації — `KEYWORD` перевіряється раніше `IDENTIFIER`, щоб слово `if` не розпізналось як ідентифікатор.

```
(?P<KEYWORD>\b(?:if|else)\b)|(?P<IDENTIFIER>[A-Za-z_]\w*)|(?P<NUMBER>-?\d+(\.\d+)?)|(?P<DELIMITER>[(){};])|(?P<SKIP>[ \t\n\r]+)|(?P<ERROR>.)
```

Метод `finditer` послідовно знаходить усі збіги в рядку зліва направо, повертаючи об'єкт збігу з полем `lastgroup` — назвою групи, що спрацювала.

---

## 4. Алгоритм роботи сканера

1. Компілюємо майстер-регекс один раз перед скануванням.
2. Викликаємо `finditer` на вхідному рядку.
3. Для кожного збігу:
   - Якщо тип `SKIP` — пропускаємо (пробіли не є токенами).
   - Якщо тип `ERROR` — додаємо токен помилки з позицією символу.
   - Інакше — додаємо токен із типом і значенням.
4. Повертаємо список токенів.

---

## 5. Програмна реалізація (Python)

```python
import re
import pprint

source = """if ( expr ){
    stmt1;
}"""

source1 = """if ( expr ){
    stmt;
}
else {
    stmt;
    stmt;
    stmt;
}"""

source2 = """if ( expr ){
    stmt;
    stmt;
}
else if ( expr ){
    stmt;
    stmt;
}
else if ( expr ){
    stmt;
}
else {
    stmt;
    stmt;
    stmt;
}"""

# специфікація токенів: список пар (тип, шаблон)
TOKEN_SPEC = [
    ('KEYWORD',    r'\b(?:if|else)\b'),
    ('IDENTIFIER', r'[A-Za-z_]\w*'),
    ('NUMBER',     r'-?\d+(\.\d+)?'),
    ('DELIMITER',  r'[(){};]'),
    ('SKIP',       r'[ \t\n\r]+'),
    ('ERROR',      r'.'),
]

# компілюємо всі шаблони в один майстер-регекс із іменованими групами
MASTER_REGEX = re.compile(
    '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_SPEC)
)

def scanner_regex(source):
    tokens = []
    for match in MASTER_REGEX.finditer(source):
        kind  = match.lastgroup
        value = match.group()
        pos   = match.start()

        # пропускаємо пробіли — вони не несуть семантичного значення
        if kind == 'SKIP':
            continue

        # фіксуємо позицію для токенів з помилкою
        if kind == 'ERROR':
            tokens.append({'type': 'ERROR', 'value': value, 'pos': pos})
        else:
            tokens.append({'type': kind, 'value': value})

    return tokens

print('Рядок 1:')
pprint.pprint(scanner_regex(source))

print('\nРядок 2:')
pprint.pprint(scanner_regex(source1))

print('\nРядок 3:')
pprint.pprint(scanner_regex(source2))
```

---

## 6. Результати роботи програми

**Вивід для рядка 1** (`if ( expr ){ stmt1; }`):

| type | value |
|------|-------|
| KEYWORD | if |
| DELIMITER | ( |
| IDENTIFIER | expr |
| DELIMITER | ) |
| DELIMITER | { |
| IDENTIFIER | stmt1 |
| DELIMITER | ; |
| DELIMITER | } |

**Вивід для рядка 2** (`if ( expr ){ stmt; } else { stmt; stmt; stmt; }`):

| type | value |
|------|-------|
| KEYWORD | if |
| DELIMITER | ( |
| IDENTIFIER | expr |
| DELIMITER | ) |
| DELIMITER | { |
| IDENTIFIER | stmt |
| DELIMITER | ; |
| DELIMITER | } |
| KEYWORD | else |
| DELIMITER | { |
| IDENTIFIER | stmt |
| DELIMITER | ; |
| IDENTIFIER | stmt |
| DELIMITER | ; |
| IDENTIFIER | stmt |
| DELIMITER | ; |
| DELIMITER | } |

**Вивід для рядка 3** (`if...else if...else if...else`):

| type | value |
|------|-------|
| KEYWORD | if |
| DELIMITER | ( |
| IDENTIFIER | expr |
| DELIMITER | ) |
| DELIMITER | { |
| IDENTIFIER | stmt |
| DELIMITER | ; |
| IDENTIFIER | stmt |
| DELIMITER | ; |
| DELIMITER | } |
| KEYWORD | else |
| KEYWORD | if |
| DELIMITER | ( |
| IDENTIFIER | expr |
| DELIMITER | ) |
| DELIMITER | { |
| IDENTIFIER | stmt |
| DELIMITER | ; |
| IDENTIFIER | stmt |
| DELIMITER | ; |
| DELIMITER | } |
| KEYWORD | else |
| KEYWORD | if |
| DELIMITER | ( |
| IDENTIFIER | expr |
| DELIMITER | ) |
| DELIMITER | { |
| IDENTIFIER | stmt |
| DELIMITER | ; |
| DELIMITER | } |
| KEYWORD | else |
| DELIMITER | { |
| IDENTIFIER | stmt |
| DELIMITER | ; |
| IDENTIFIER | stmt |
| DELIMITER | ; |
| IDENTIFIER | stmt |
| DELIMITER | ; |
| DELIMITER | } |

---

## 7. Таблиця символів

| № | Ім'я / Значення | Тип | Атрибут |
|---|-----------------|-----|---------|
| 1 | `if` | KEYWORD | — |
| 2 | `else` | KEYWORD | — |
| 3 | `expr` | IDENTIFIER | змінна |
| 4 | `stmt` | IDENTIFIER | оператор |
| 5 | `stmt1` | IDENTIFIER | оператор |
| 6 | `(` | DELIMITER | — |
| 7 | `)` | DELIMITER | — |
| 8 | `{` | DELIMITER | — |
| 9 | `}` | DELIMITER | — |
| 10 | `;` | DELIMITER | — |

---

## 8. Висновки

У ході виконання лабораторної роботи:

1. Визначено специфікацію токенів за допомогою регулярних виразів для типів: `KEYWORD`, `IDENTIFIER`, `NUMBER`, `DELIMITER`, `SKIP`, `ERROR`.

2. Побудовано майстер-регулярний вираз із іменованими групами, що об'єднує всі шаблони з урахуванням пріоритету — ключові слова перевіряються раніше ідентифікаторів.

3. Реалізовано сканер мовою **Python**, що використовує `re.finditer` для послідовного обходу вхідного рядка та формування списку токенів.

4. Перевірено роботу програмної моделі на трьох тестових прикладах — усі коректні лексеми розпізнано правильно з визначенням їх типів: `KEYWORD`, `IDENTIFIER`, `DELIMITER`.

5. Підхід на основі регулярних виразів є компактнішим порівняно з явною реалізацією скінченного автомата, оскільки рушій регулярних виразів внутрішньо будує і виконує NFA/DFA автоматично.

---
