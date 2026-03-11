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