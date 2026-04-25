"""
Lab 3 - Перевірка правил граматики if-else
Граматика:
    1. I  -> If(A){B;R}C
    2. A  -> exp
    3. B  -> smth
    4. R  -> B;R | $
    5. C  -> Else X | $
    6. X  -> {B;R} | I
"""

import re
import pprint

# ── тестові рядки ────────────────────────────────────────────────────────────

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

# ── граматика у вигляді структури Rule[i][j][k] ──────────────────────────────

# Rule[i]       — i-те правило
# Rule[i][0]    — ліва частина (нетермінал)
# Rule[i][1]    — права частина (список альтернатив або символів)
# Rule[i][1][j] — j-й символ правої частини
# (T) = термінал, (F) = нетермінал

RULES = [
    # Rule[0]: I -> If ( A ) { B ; R } C
    ["I", ["If", "(", "A", ")", "{", "B", ";", "R", "}", "C"]],
    # Rule[1]: A -> exp
    ["A", ["exp"]],
    # Rule[2]: B -> smth
    ["B", ["smth"]],
    # Rule[3]: R -> B;R | $   (дві альтернативи зберігаємо окремо)
    ["R", ["B", ";", "R"]],   # Rule[3][1][0]="B"(F), Rule[3][1][1]=";"(T), Rule[3][1][2]="R"(F)
    ["R", ["$"]],              # Rule[3][2]="$"
    # Rule[4]: C -> Else X | $
    ["C", ["Else", "X"]],
    ["C", ["$"]],
    # Rule[5]: X -> {B;R} | I
    ["X", ["{", "B", ";", "R", "}"]],
    ["X", ["I"]],
]

# Множина нетерміналів
NON_TERMINALS = {"I", "A", "B", "R", "C", "X"}

# Множина терміналів
TERMINALS = {"If", "(", ")", "{", "}", ";", "exp", "smth", "Else"}

EPSILON = "$"
END_MARKER = "#"


# ── сканер (з попередньої лабораторної) ──────────────────────────────────────

KEYWORDS = {'if', 'else'}
REGEX_SPACE   = re.compile(r'[ \t\n\r]')
REGEX_LETTER  = re.compile(r'[a-zA-Z_]')
REGEX_DIGIT   = re.compile(r'[0-9]')
REGEX_DELIM   = re.compile(r'[(){};]')
REGEX_KEYWORD    = re.compile(r'^(if|else)$')
REGEX_IDENTIFIER = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')
REGEX_NUMBER     = re.compile(r'^\d+$')

transition_table = {
    'S0': {'space': 'S0', 'letter': 'S1', 'digit': 'S2', 'delim': 'S0',    'other': 'S_ERR'},
    'S1': {'space': 'S0', 'letter': 'S1', 'digit': 'S1', 'delim': 'S0',    'other': 'S_ERR'},
    'S2': {'space': 'S0', 'letter': 'S_ERR', 'digit': 'S2', 'delim': 'S0', 'other': 'S_ERR'},
}

def get_char_class(ch):
    """Визначити клас символу."""
    if REGEX_SPACE.match(ch):   return 'space'
    if REGEX_LETTER.match(ch):  return 'letter'
    if REGEX_DIGIT.match(ch):   return 'digit'
    if REGEX_DELIM.match(ch):   return 'delim'
    return 'other'

def scanner(source):
    """Розбити вхідний рядок на токени за допомогою автомата."""
    tokens = []
    state = 'S0'
    lexeme = []

    def flush_word():
        if not lexeme: return
        word = ''.join(lexeme)
        if REGEX_KEYWORD.match(word):
            tokens.append({'type': 'KEYWORD',    'value': word})
        elif REGEX_IDENTIFIER.match(word):
            tokens.append({'type': 'IDENTIFIER', 'value': word})
        lexeme.clear()

    def flush_num():
        if not lexeme: return
        word = ''.join(lexeme)
        if REGEX_NUMBER.match(word):
            tokens.append({'type': 'NUMBER', 'value': word})
        lexeme.clear()

    for i, ch in enumerate(source):
        cls = get_char_class(ch)
        next_state = transition_table[state][cls]
        if next_state == 'S_ERR':
            tokens.append({'type': 'ERROR', 'value': ch, 'pos': i})
            return tokens
        if state == 'S0':
            if cls in ('letter', 'digit'): lexeme.append(ch)
            elif cls == 'delim': tokens.append({'type': 'DELIMITER', 'value': ch})
        elif state == 'S1':
            if cls in ('letter', 'digit'): lexeme.append(ch)
            elif cls == 'space': flush_word()
            elif cls == 'delim':
                flush_word()
                tokens.append({'type': 'DELIMITER', 'value': ch})
        elif state == 'S2':
            if cls == 'digit': lexeme.append(ch)
            elif cls == 'space': flush_num()
            elif cls == 'delim':
                flush_num()
                tokens.append({'type': 'DELIMITER', 'value': ch})
        state = next_state

    flush_word()
    flush_num()
    return tokens


# ── перетворення токенів у граматичні символи ─────────────────────────────────

def tokens_to_grammar_symbols(tokens):
    """
    Перетворити список токенів сканера у граматичні символи.
    'if' -> 'If', 'else' -> 'Else', ідентифікатори -> 'exp' або 'smth',
    роздільники -> відповідний термінал.
    """
    symbols = []
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok['type'] == 'KEYWORD':
            if tok['value'] == 'if':
                symbols.append('If')
            elif tok['value'] == 'else':
                symbols.append('Else')
        elif tok['type'] == 'IDENTIFIER':
            val = tok['value']
            # 'expr' -> граматичний термінал 'exp', інше -> 'smth'
            if val.startswith('expr'):
                symbols.append('exp')
            else:
                symbols.append('smth')
        elif tok['type'] == 'DELIMITER':
            symbols.append(tok['value'])
        i += 1
    return symbols


# ── рекурсивний спуск (парсер) ────────────────────────────────────────────────

class Parser:
    """
    Рекурсивний низхідний парсер для граматики if-else.
    Відповідає структурі RULES: кожен метод — окремий нетермінал.
    """

    def __init__(self, symbols):
        # Вхідна послідовність символів із маркером кінця
        self.symbols = symbols + [END_MARKER]
        self.pos = 0
        self.errors = []

    def current(self):
        """Поточний символ."""
        return self.symbols[self.pos]

    def consume(self, expected):
        """
        Спожити очікуваний термінал.
        Якщо поточний символ не збігається — зафіксувати помилку.
        """
        if self.current() == expected:
            self.pos += 1
            return True
        else:
            self.errors.append(
                f"  Очікувався '{expected}', але знайдено '{self.current()}' (позиція {self.pos})"
            )
            return False

    # Rule[0]: I -> If ( A ) { B ; R } C
    def parse_I(self):
        self.consume('If')
        self.consume('(')
        self.parse_A()
        self.consume(')')
        self.consume('{')
        self.parse_B()
        self.consume(';')
        self.parse_R()
        self.consume('}')
        self.parse_C()

    # Rule[1]: A -> exp
    def parse_A(self):
        self.consume('exp')

    # Rule[2]: B -> smth
    def parse_B(self):
        self.consume('smth')

    # Rule[3]: R -> B;R | $
    def parse_R(self):
        # ВИБІР: якщо поточний символ 'smth' — Rule[3][1] (B;R)
        if self.current() == 'smth':
            self.parse_B()
            self.consume(';')
            self.parse_R()
        # інакше — Rule[3][2] ($), епсилон, нічого не споживаємо

    # Rule[4]: C -> Else X | $
    def parse_C(self):
        # ВИБІР: якщо поточний символ 'Else' — Rule[4][1] (Else X)
        if self.current() == 'Else':
            self.consume('Else')
            self.parse_X()
        # інакше — Rule[4][2] ($), епсилон

    # Rule[5]: X -> {B;R} | I
    def parse_X(self):
        if self.current() == '{':
            # Rule[5][1]: { B ; R }
            self.consume('{')
            self.parse_B()
            self.consume(';')
            self.parse_R()
            self.consume('}')
        elif self.current() == 'If':
            # Rule[5][2]: I  (рекурсивний вкладений if)
            self.parse_I()
        else:
            self.errors.append(
                f"  Очікувався '{{' або 'If' у X, але знайдено '{self.current()}' (позиція {self.pos})"
            )


def check(source_str, label):
    """Перевірити один вхідний рядок і вивести результат."""
    print(f"ПЕРЕВІРКА: {label}")
    print("Вхідний рядок:")
    print(source_str)
    print()

    # Сканування
    tokens = scanner(source_str)
    symbols = tokens_to_grammar_symbols(tokens)

    print("Граматичні символи:")
    pprint.pprint(symbols)
    print()

    # Парсинг
    parser = Parser(symbols)
    parser.parse_I()

    # Перевірка залишку (має бути тільки END_MARKER)
    if parser.current() != END_MARKER:
        parser.errors.append(
            f"  Залишились непрочитані символи починаючи з позиції {parser.pos}: "
            f"{parser.symbols[parser.pos:]}"
        )

    if not parser.errors:
        print("Результат: ПРАВИЛА ГРАМАТИКИ ДОТРИМАНІ")
    else:
        print("Результат: ПОРУШЕННЯ ПРАВИЛ ГРАМАТИКИ")
        print("Помилки:")
        for err in parser.errors:
            print(err)
    print()


# ── головна функція ───────────────────────────────────────────────────────────

def main():
    check(source,  "Рядок 1 — простий if без else")
    check(source1, "Рядок 2 — if з else та кількома операторами")
    check(source2, "Рядок 3 — вкладені if-else if-else")


if __name__ == "__main__":
    main()