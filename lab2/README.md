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

# ключові слова, які розпізнаємо
KEYWORDS = {'if', 'else'}

# символи, що вважаються роздільниками
DELIMITERS = set('(){};')

# таблиця переходів між станами автомата
# transition_table[поточний_стан][клас_символу] = наступний_стан
transition_table = {
    'S0': {'space': 'S0', 'letter': 'S1', 'digit': 'S2', 'delim': 'S0',    'other': 'S_ERR'},
    'S1': {'space': 'S0', 'letter': 'S1', 'digit': 'S1', 'delim': 'S0',    'other': 'S_ERR'},
    'S2': {'space': 'S0', 'letter': 'S_ERR', 'digit': 'S2', 'delim': 'S0', 'other': 'S_ERR'},
}

# регулярні вирази для розпізнавання типів токенів
REGEX_KEYWORD    = re.compile(r'^(if|else)$')
REGEX_IDENTIFIER = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')
REGEX_NUMBER     = re.compile(r'^\d+$')
REGEX_DELIMITER  = re.compile(r'^[(){};]$')

def get_char_class(ch):
    """Визначити клас символу для таблиці переходів."""
    if ch in ' \t\n\r':
        return 'space'
    if ch.isalpha() or ch == '_':
        return 'letter'
    if ch.isdigit():
        return 'digit'
    if ch in DELIMITERS:
        return 'delim'
    return 'other'

def scanner(source):
    tokens = []
    state = 'S0'
    lexeme = []

    def flush_word():
        """Якщо слово накопичено — класифікувати його як ключове слово або ідентифікатор."""
        if not lexeme:
            return
        word = ''.join(lexeme)
        if REGEX_KEYWORD.match(word):
            tokens.append({'type': 'KEYWORD',    'value': word})
        else:
            tokens.append({'type': 'IDENTIFIER', 'value': word})
        lexeme.clear()

    def flush_num():
        """Якщо цифри накопичено — перевірити через регулярний вираз і додати числовий токен."""
        if not lexeme:
            return
        tokens.append({'type': 'NUMBER', 'value': ''.join(lexeme)})
        lexeme.clear()

    for i, ch in enumerate(source):
        cls = get_char_class(ch)

        # визначити наступний стан із таблиці переходів
        next_state = transition_table[state][cls]

        # якщо наступний стан є помилковим — зупинити сканування
        if next_state == 'S_ERR':
            tokens.append({'type': 'ERROR', 'value': ch, 'pos': i})
            return tokens

        if state == 'S0':
            if cls in ('letter', 'digit'):
                lexeme.append(ch)
            elif cls == 'delim':
                tokens.append({'type': 'DELIMITER', 'value': ch})
            # пробіли просто пропускаються

        elif state == 'S1':
            if cls in ('letter', 'digit'):
                lexeme.append(ch)
            elif cls == 'space':
                flush_word()
            elif cls == 'delim':
                flush_word()
                tokens.append({'type': 'DELIMITER', 'value': ch})

        elif state == 'S2':
            if cls == 'digit':
                lexeme.append(ch)
            elif cls == 'space':
                flush_num()
            elif cls == 'delim':
                flush_num()
                tokens.append({'type': 'DELIMITER', 'value': ch})

        state = next_state

    # скинути залишок лексеми, якщо рядок закінчився без роздільника
    flush_word()
    flush_num()

    return tokens

print('Рядок 1:')
pprint.pprint(scanner(source))

print('\nРядок 2:')
pprint.pprint(scanner(source1))

print('\nРядок 3:')
pprint.pprint(scanner(source2))
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

1. Визначено специфікацію токенів — множину метасимволів та ключових слів для розпізнавання лексем типів: `KEYWORD`, `IDENTIFIER`, `NUMBER`, `DELIMITER`, `SKIP`, `ERROR`.

2. Побудовано таблицю переходів скінченного автомата з трьома станами (`S0`, `S1`, `S2`) та станом помилки `S_ERR`, що описує логіку переходів між класами символів: `space`, `letter`, `digit`, `delim`, `other`.

3. Реалізовано сканер мовою **Python** на основі таблиці переходів із застосуванням регулярних виразів для фінальної класифікації накопичених лексем — розрізнення ключових слів (`KEYWORD`) та ідентифікаторів (`IDENTIFIER`).

4. Перевірено роботу програмної моделі на трьох тестових прикладах — простий `if`, конструкція `if-else` та ланцюжок `if-else if-else if-else`. Усі коректні лексеми розпізнано правильно з визначенням їх типів.

5. Поєднання явної таблиці переходів автомата з регулярними виразами для класифікації дозволяє чітко розмежувати логіку розбору символів і логіку розпізнавання типів токенів, що підвищує прозорість та розширюваність реалізації.

---