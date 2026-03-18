import re
import pprint

source = """if ( expr ){
    stmt;
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