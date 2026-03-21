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

Для розпізнавання лексем визначено набір регулярних виразів, що застосовуються після накопичення лексеми автоматом:

| Тип токена | Регулярний вираз | Опис |
|------------|-----------------|------|
| `KEYWORD` | `^(if\|else)$` | Ключові слова `if` та `else` |
| `IDENTIFIER` | `^[a-zA-Z_][a-zA-Z0-9_]*$` | Ідентифікатор: починається з літери або `_` |
| `NUMBER` | `^\d+$` | Ціле невід'ємне число |
| `DELIMITER` | `^[(){};]$` | Роздільники: дужки та крапка з комою |
| `ERROR` | — | Будь-який нерозпізнаний символ (стан `S_ERR`) |

**Таблиця 1 — Специфікація токенів лексичного аналізатора (варіант 7)**

Регулярні вирази застосовуються **не до всього рядка**, а лише до вже накопиченої лексеми у функціях `flush_word()` та `flush_num()`.

---

## 3. Таблиця переходів автомата

Сканер реалізовано у вигляді скінченного детермінованого автомата з трьома робочими станами та одним станом помилки:

| Стан | Опис |
|------|------|
| `S0` | Початковий стан, очікування нової лексеми |
| `S1` | Накопичення літер/цифр (ідентифікатор або ключове слово) |
| `S2` | Накопичення цифр (число) |
| `S_ERR` | Стан помилки — сканування зупиняється |

Кожен символ вхідного рядка відноситься до одного з класів:

| Клас | Символи |
|------|---------|
| `space` | пробіл, `\t`, `\n`, `\r` |
| `letter` | `a-z`, `A-Z`, `_` |
| `digit` | `0-9` |
| `delim` | `(`, `)`, `{`, `}`, `;` |
| `other` | усі інші символи |

Таблиця переходів `transition_table[поточний_стан][клас_символу] = наступний_стан`:

| Стан \ Клас | `space` | `letter` | `digit` | `delim` | `other` |
|-------------|---------|----------|---------|---------|---------|
| `S0` | `S0` | `S1` | `S2` | `S0` | `S_ERR` |
| `S1` | `S0` | `S1` | `S1` | `S0` | `S_ERR` |
| `S2` | `S0` | `S_ERR` | `S2` | `S0` | `S_ERR` |

**Таблиця 2 — Таблиця переходів скінченного автомата**

---

## 4. Алгоритм роботи сканера

1. Ініціалізуємо стан `S0` та порожній буфер лексеми.
2. Для кожного символу вхідного рядка:
   - Визначаємо клас символу через `get_char_class()`.
   - За таблицею переходів знаходимо наступний стан.
   - Якщо наступний стан `S_ERR` — додаємо токен помилки та зупиняємось.
   - Залежно від поточного стану — накопичуємо символ у буфер або скидаємо накопичену лексему.
3. Скидання лексеми (`flush_word` / `flush_num`):
   - `flush_word` — перевіряє накопичене слово через `REGEX_KEYWORD`, класифікує як `KEYWORD` або `IDENTIFIER`.
   - `flush_num` — перевіряє накопичені цифри через `REGEX_NUMBER`, додає токен `NUMBER`.
4. Роздільники додаються як окремі токени `DELIMITER` одразу при зустрічі.
5. Пробіли пропускаються — вони не несуть семантичного значення.
6. Після обходу всього рядка скидаємо залишок буфера.

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

# регулярні вирази для визначення класу символу
REGEX_SPACE   = re.compile(r'[ \t\n\r]')
REGEX_LETTER  = re.compile(r'[a-zA-Z_]')
REGEX_DIGIT   = re.compile(r'[0-9]')
REGEX_DELIM   = re.compile(r'[(){};]')

# регулярні вирази для класифікації токенів
REGEX_KEYWORD    = re.compile(r'^(if|else)$')
REGEX_IDENTIFIER = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')
REGEX_NUMBER     = re.compile(r'^\d+$')

def get_char_class(ch):
    """Визначити клас символу за допомогою регулярних виразів."""
    if REGEX_SPACE.match(ch):
        return 'space'
    if REGEX_LETTER.match(ch):
        return 'letter'
    if REGEX_DIGIT.match(ch):
        return 'digit'
    if REGEX_DELIM.match(ch):
        return 'delim'
    return 'other'

def scanner(source):
    tokens = []
    state = 'S0'
    lexeme = []

    def flush_word():
        """Класифікувати накопичену лексему як ключове слово або ідентифікатор за допомогою регулярних виразів."""
        if not lexeme:
            return
        word = ''.join(lexeme)
        if REGEX_KEYWORD.match(word):
            tokens.append({'type': 'KEYWORD',    'value': word})
        elif REGEX_IDENTIFIER.match(word):
            tokens.append({'type': 'IDENTIFIER', 'value': word})
        lexeme.clear()

    def flush_num():
        """Перевірити накопичені цифри регулярним виразом і додати числовий токен."""
        if not lexeme:
            return
        word = ''.join(lexeme)
        if REGEX_NUMBER.match(word):
            tokens.append({'type': 'NUMBER', 'value': word})
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

**Вивід для рядка 1** (`if ( expr ){ stmt; }`):

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
| 5 | `(` | DELIMITER | — |
| 6 | `)` | DELIMITER | — |
| 7 | `{` | DELIMITER | — |
| 8 | `}` | DELIMITER | — |
| 9 | `;` | DELIMITER | — |

---

## 8. Висновки

У ході виконання лабораторної роботи:

1. Визначено множину метасимволів та ключових слів для розпізнавання лексем типів: `KEYWORD`, `IDENTIFIER`, `NUMBER`, `DELIMITER`, `ERROR`.

2. Побудовано таблицю переходів скінченного детермінованого автомата з трьома станами (`S0`, `S1`, `S2`) та станом помилки `S_ERR`, що описує логіку переходів між класами символів: `space`, `letter`, `digit`, `delim`, `other`.

3. Реалізовано сканер мовою **Python** на основі таблиці переходів із застосуванням регулярних виразів для фінальної класифікації накопичених лексем — розрізнення ключових слів (`KEYWORD`) та ідентифікаторів (`IDENTIFIER`) у функціях `flush_word()` та `flush_num()`.

4. Перевірено роботу програмної моделі на трьох тестових прикладах — простий `if`, конструкція `if-else` та ланцюжок `if-else if-else if-else`. Усі коректні лексеми розпізнано правильно з визначенням їх типів.

5. Поєднання явної таблиці переходів автомата з регулярними виразами для класифікації дозволяє чітко розмежувати логіку посимвольного розбору та логіку розпізнавання типів токенів, що підвищує прозорість та розширюваність реалізації.

---