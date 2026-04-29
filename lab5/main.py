"""
Лабораторна робота 5 - Побудова команд магазинного автомата
та перевірка вхідних ланцюжків.

Граматика if-else:
    1. I  -> If(A){B;R}C
    2. A  -> exp
    3. B  -> smth
    4. R  -> B;R | $
    5. C  -> Else X | $
    6. X  -> {B;R} | I
"""

import re
import pprint

# ── тестові рядки ─────────────────────────────────────────────────────────────

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

# ── правила граматики ─────────────────────────────────────────────────────────

RULES = [
    ("I", ["If", "(", "A", ")", "{", "B", ";", "R", "}", "C"]),
    ("A", ["exp"]),
    ("B", ["smth"]),
    ("R", ["B", ";", "R"]),
    ("R", ["$"]),
    ("C", ["Else", "X"]),
    ("C", ["$"]),
    ("X", ["{", "B", ";", "R", "}"]),
    ("X", ["I"]),
]

NON_TERMINALS = {"I", "A", "B", "R", "C", "X"}
TERMINALS     = {"If", "(", ")", "{", "}", ";", "exp", "smth", "Else"}
EPSILON       = "$"
END_MARKER    = "#"


# ── сканер ────────────────────────────────────────────────────────────────────

REGEX_SPACE      = re.compile(r'[ \t\n\r]')
REGEX_LETTER     = re.compile(r'[a-zA-Z_]')
REGEX_DIGIT      = re.compile(r'[0-9]')
REGEX_DELIM      = re.compile(r'[(){};]')
REGEX_KEYWORD    = re.compile(r'^(if|else)$')
REGEX_IDENTIFIER = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')
REGEX_NUMBER     = re.compile(r'^\d+$')

transition_table = {
    'S0': {'space': 'S0', 'letter': 'S1', 'digit': 'S2', 'delim': 'S0',    'other': 'S_ERR'},
    'S1': {'space': 'S0', 'letter': 'S1', 'digit': 'S1', 'delim': 'S0',    'other': 'S_ERR'},
    'S2': {'space': 'S0', 'letter': 'S_ERR', 'digit': 'S2', 'delim': 'S0', 'other': 'S_ERR'},
}

def get_char_class(ch):
    """Визначити клас символу для таблиці переходів."""
    if REGEX_SPACE.match(ch):  return 'space'
    if REGEX_LETTER.match(ch): return 'letter'
    if REGEX_DIGIT.match(ch):  return 'digit'
    if REGEX_DELIM.match(ch):  return 'delim'
    return 'other'

def scanner(source):
    """Розбити вхідний рядок на токени за допомогою скінченного автомата."""
    tokens = []
    state  = 'S0'
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
        cls        = get_char_class(ch)
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
    Перетворити список токенів сканера у термінальні символи граматики.
    'if' -> 'If', 'else' -> 'Else',
    ідентифікатори 'expr*' -> 'exp', решта ідентифікаторів -> 'smth',
    роздільники -> відповідний термінал.
    """
    symbols = []
    for tok in tokens:
        if tok['type'] == 'KEYWORD':
            if tok['value'] == 'if':
                symbols.append('If')
            elif tok['value'] == 'else':
                symbols.append('Else')
        elif tok['type'] == 'IDENTIFIER':
            if tok['value'].startswith('expr'):
                symbols.append('exp')
            else:
                symbols.append('smth')
        elif tok['type'] == 'DELIMITER':
            symbols.append(tok['value'])
    return symbols


# ── допоміжні функції граматики ───────────────────────────────────────────────

def get_rules_for(nt):
    """Повернути всі праві частини правил для заданого нетермінала."""
    return [rhs for (lhs, rhs) in RULES if lhs == nt]


# ── функція ПЕРШ ──────────────────────────────────────────────────────────────

def first_of_sequence(seq, visiting=None):
    """Обчислити множину ПЕРШ для послідовності символів граматики."""
    if visiting is None:
        visiting = set()
    result = set()
    if not seq or seq == [EPSILON]:
        result.add(EPSILON)
        return result
    for sym in seq:
        if sym in TERMINALS:
            result.add(sym)
            break
        elif sym in NON_TERMINALS:
            sym_first = first_of_nt(sym, visiting)
            result |= sym_first - {EPSILON}
            if EPSILON not in sym_first:
                break
    else:
        result.add(EPSILON)
    return result


def first_of_nt(nt, visiting=None):
    """Обчислити множину ПЕРШ для нетермінала."""
    if visiting is None:
        visiting = set()
    if nt in visiting:
        return set()
    visiting = visiting | {nt}
    result = set()
    for rhs in get_rules_for(nt):
        result |= first_of_sequence(rhs, visiting)
    return result


def compute_first_all():
    """Обчислити ПЕРШ для кожного правила граматики."""
    result = {}
    for (lhs, rhs) in RULES:
        key = f"{lhs} -> {' '.join(rhs)}"
        result[key] = first_of_sequence(rhs)
    return result


# ── функція СЛІД ──────────────────────────────────────────────────────────────

def compute_follow():
    """
    Обчислити множину СЛІД для кожного нетермінала.
    Стартовий символ I отримує маркер кінця #.
    Використовується ітеративний алгоритм фіксованої точки.
    """
    follow = {nt: set() for nt in NON_TERMINALS}
    follow["I"].add(END_MARKER)

    changed = True
    while changed:
        changed = False
        for (lhs, rhs) in RULES:
            for i, sym in enumerate(rhs):
                if sym not in NON_TERMINALS:
                    continue
                after       = rhs[i + 1:]
                first_after = first_of_sequence(after) if after else {EPSILON}
                to_add = first_after - {EPSILON}
                if to_add - follow[sym]:
                    follow[sym] |= to_add
                    changed = True
                if EPSILON in first_after:
                    if follow[lhs] - follow[sym]:
                        follow[sym] |= follow[lhs]
                        changed = True
    return follow


# ── множина ВИБІР ─────────────────────────────────────────────────────────────

def compute_choice(follow):
    """
    Обчислити множину ВИБІР для кожного правила граматики.

    ВИБІР(B -> µ):
      - якщо µ не породжує ε : ПЕРШ(µ)
      - якщо µ породжує ε    : (ПЕРШ(µ) \\ {$}) ∪ СЛІД(B)
    """
    result = {}
    for (lhs, rhs) in RULES:
        key   = f"{lhs} -> {' '.join(rhs)}"
        first = first_of_sequence(rhs)
        if EPSILON in first:
            result[key] = (first - {EPSILON}) | follow[lhs]
        else:
            result[key] = first
    return result


# ── визначення типу граматики ─────────────────────────────────────────────────

def determine_grammar_type(follow):
    """Класифікувати граматику та повернути словник з результатами аналізу."""
    choice = compute_choice(follow)

    all_start_terminal = True
    has_epsilon_rule   = False

    for (lhs, rhs) in RULES:
        if rhs == [EPSILON]:
            has_epsilon_rule = True
        elif rhs[0] in NON_TERMINALS:
            all_start_terminal = False

    choice_disjoint  = True
    conflict_details = []

    for nt in NON_TERMINALS:
        nt_keys = [
            f"{lhs} -> {' '.join(rhs)}"
            for (lhs, rhs) in RULES
            if lhs == nt
        ]
        if len(nt_keys) < 2:
            continue
        sets = [choice[k] for k in nt_keys]
        for i in range(len(sets)):
            for j in range(i + 1, len(sets)):
                inter = sets[i] & sets[j]
                if inter:
                    choice_disjoint = False
                    conflict_details.append(
                        f"  ВИБІР({nt_keys[i]}) ∩ "
                        f"ВИБІР({nt_keys[j]}) = {{ {', '.join(sorted(inter))} }}"
                    )

    return {
        "choice":             choice,
        "all_start_terminal": all_start_terminal,
        "has_epsilon_rule":   has_epsilon_rule,
        "choice_disjoint":    choice_disjoint,
        "conflict_details":   conflict_details,
    }


# ── форматування множини ──────────────────────────────────────────────────────

def fmt_set(s):
    """Відформатувати множину: термінали за алфавітом, $ та # завжди останні."""
    terminals = sorted(x for x in s if x not in (EPSILON, END_MARKER))
    extras    = sorted(x for x in s if x in (EPSILON, END_MARKER))
    return "{" + ", ".join(terminals + extras) + "}"


# ══════════════════════════════════════════════════════════════════════════════
# ЛАБОРАТОРНА РОБОТА 5 — ПОБУДОВА КОМАНД МАГАЗИННОГО АВТОМАТА
# ══════════════════════════════════════════════════════════════════════════════

def build_pda_commands(choice):
    """
    Побудувати всі команди магазинного автомата (функції переходів).

    Типи команд (згідно з методичними вказівками):
      Тип 1 – правило починається з термінала  A -> b α
               f(s0, b, A) = (s, дзеркало(α))      [голівка зрушується]
      Тип 2 – правило починається з нетермінала  A -> B α
               f*(s0, x, A) = (s, дзеркало(B α))   [голівка не зрушується],
               по одній команді на кожен x з ВИБІР(A -> B α)
      Тип 3 – анулююче правило  A -> $
               f*(s0, x, A) = (s, $)               [голівка не зрушується],
               по одній команді на кожен x з ВИБІР(A -> $)
      Тип 4 – термінал b знаходиться в середині або в кінці правила
               f(s0, b, b) = (s, $)               [голівка зрушується]
      Тип 5 – перехід у заключний стан
               f*(s0, $, h0) = (s, $)
    """
    commands = []

    for (lhs, rhs) in RULES:
        rule_key = f"{lhs} -> {' '.join(rhs)}"

        if rhs == [EPSILON]:
            # ── тип 3: анулююче правило ───────────────────────────────────────
            for x in sorted(choice[rule_key]):
                commands.append({
                    "type":    "f*",
                    "input":   x,
                    "stack":   lhs,
                    "result":  "$",
                    "comment": f"Анулююче правило {lhs} -> $",
                })

        elif rhs[0] not in NON_TERMINALS:
            # ── тип 1: правило починається з термінала ────────────────────────
            # перший термінал споживається; решта заноситься у магазин у зворотному порядку
            first_terminal = rhs[0]
            rest           = rhs[1:]
            push_str       = " ".join(reversed(rest)) if rest else "$"

            commands.append({
                "type":    "f",
                "input":   first_terminal,
                "stack":   lhs,
                "result":  push_str,
                "comment": f"Правило починається з термінала: {lhs} -> {' '.join(rhs)}",
            })

        else:
            # ── тип 2: правило починається з нетермінала ─────────────────────
            # вся права частина заноситься у зворотному порядку;
            # кількість команд = кількість елементів у ВИБІР
            push_str = " ".join(reversed(rhs))

            for x in sorted(choice[rule_key]):
                commands.append({
                    "type":    "f*",
                    "input":   x,
                    "stack":   lhs,
                    "result":  push_str,
                    "comment": f"Правило починається з нетермінала: {lhs} -> {' '.join(rhs)}",
                })

    # ── тип 4: команди для терміналів у середині та в кінці правил ────────────
    all_terminals_in_rules = set()
    for (lhs, rhs) in RULES:
        for sym in rhs:
            if sym in TERMINALS:
                all_terminals_in_rules.add(sym)

    for t in sorted(all_terminals_in_rules):
        commands.append({
            "type":    "f",
            "input":   t,
            "stack":   t,
            "result":  "$",
            "comment": f"Збіг термінала: спожити '{t}' з входу та магазину",
        })

    # ── тип 5: перехід у заключний стан ──────────────────────────────────────
    commands.append({
        "type":    "f*",
        "input":   "$",
        "stack":   "h0",
        "result":  "$",
        "comment": "Прийняття: вхід та магазин порожні",
    })

    return commands


def fmt_command(cmd, index):
    """Відформатувати одну команду МА у рядок."""
    return (
        f"{index}. {cmd['type']}(s0, {cmd['input']}, {cmd['stack']}) "
        f"= (s, {cmd['result']})"
    )


# ══════════════════════════════════════════════════════════════════════════════
# СИМУЛЯЦІЯ МАГАЗИННОГО АВТОМАТА
# ══════════════════════════════════════════════════════════════════════════════

def find_command(commands, lexeme, stack_top):
    """
    Знайти відповідну команду переходу за поточною лексемою та вершиною магазину.
    Повертає (команда, індекс_1) або (None, -1).
    """
    for i, cmd in enumerate(commands):
        if cmd["input"] == lexeme and cmd["stack"] == stack_top:
            return cmd, i + 1
    return None, -1


def simulate_pda(input_tokens, commands, label):
    """
    Виконати симуляцію магазинного автомата на послідовності граматичних символів.
    Виводить зміну конфігурацій у текстовому форматі, як у прикладах з методички.

    Параметри
    ----------
    input_tokens : list[str]   — послідовність граматичних символів (без маркера кінця)
    commands     : list[dict]  — команди МА, побудовані функцією build_pda_commands()
    label        : str         — назва перевірки для заголовка виводу
    """
    print(f"ПЕРЕВІРКА ЛАНЦЮЖКА: {label}")

    # Вхідна стрічка завершується маркером кінця #
    tape  = list(input_tokens) + [END_MARKER]
    # Магазин: індекс 0 = дно (h0), -1 = вершина; початково h0 та стартовий символ I
    stack = ["h0", "I"]

    tape_str  = "".join(tape[:-1]) + tape[-1]
    stack_str = "".join(reversed(stack))
    print(f"({tape_str}, {stack_str})", end="")

    step   = 0
    ok     = False

    while True:
        lexeme    = tape[0]
        stack_top = stack[-1] if stack else None

        # Умова прийняття: вхід і магазин порожні
        if lexeme == END_MARKER and stack_top == "h0":
            cmd, idx = find_command(commands, "$", "h0")
            if cmd:
                stack.pop()
                print(f" ├ {idx}")
                print(f"($, $)")
            ok = True
            break

        if stack_top is None:
            print()
            print("  ПОМИЛКА АНАЛІЗУ — магазин порожній, вхід не вичерпано")
            break

        cmd, idx = find_command(commands, lexeme, stack_top)

        if cmd is None:
            print()
            print(
                f"  ПОМИЛКА АНАЛІЗУ — не знайдено команди для "
                f"(вхід='{lexeme}', вершина магазину='{stack_top}')"
            )
            break

        # Видалити вершину магазину
        stack.pop()

        if cmd["type"] == "f":
            # Зрушення вхідної голівки (споживаємо лексему)
            tape.pop(0)

        # Занести результат у магазин у зворотному порядку
        result_str = cmd["result"]
        if result_str != "$":
            for tok in result_str.split():
                stack.append(tok)

        # Сформувати рядок поточної конфігурації
        tape_str  = "".join(tape[:-1]) + tape[-1] if len(tape) > 1 else tape[0]
        stack_str = "".join(reversed(stack)) if stack else "$"
        print(f" ├ {idx}")
        print(f"({tape_str}, {stack_str})", end="")

        step += 1
        if step > 10_000:
            print()
            print("  ПОМИЛКА АНАЛІЗУ — перевищено максимальну кількість кроків")
            break

    print()
    if ok:
        print("Результат: ЛАНЦЮЖОК РОЗПІЗНАНО (Аналіз ОК)")
    else:
        print("Результат: ЛАНЦЮЖОК НЕ РОЗПІЗНАНО (Помилка аналізу)")
    print()


# ══════════════════════════════════════════════════════════════════════════════
# ГОЛОВНА ФУНКЦІЯ
# ══════════════════════════════════════════════════════════════════════════════

def main():
    # ── правила граматики ─────────────────────────────────────────────────────
    print("Правила граматики:")
    for i, (lhs, rhs) in enumerate(RULES, 1):
        print(f"  {i}. {lhs} -> {' '.join(rhs)}")
    print()

    # ── функція ПЕРШ ──────────────────────────────────────────────────────────
    first_all = compute_first_all()
    print("Функція ПЕРШ(µ) для кожного правила:")
    for rule_key, first_set in first_all.items():
        print(f"  ПЕРШ({rule_key}) = {fmt_set(first_set)}")
    print()

    print("Функція ПЕРШ(µ) для нетерміналів:")
    for nt in sorted(NON_TERMINALS):
        print(f"  ПЕРШ({nt}) = {fmt_set(first_of_nt(nt))}")
    print()

    # ── функція СЛІД ──────────────────────────────────────────────────────────
    follow = compute_follow()
    print("Функція СЛІД(µ):")
    for nt in sorted(NON_TERMINALS):
        print(f"  СЛІД({nt}) = {fmt_set(follow[nt])}")
    print()

    # ── множина ВИБІР ─────────────────────────────────────────────────────────
    info   = determine_grammar_type(follow)
    choice = info["choice"]

    print("Множина ВИБІР:")
    for rule_key, choice_set in choice.items():
        print(f"  ВИБІР({rule_key}) = {fmt_set(choice_set)}")
    print()

    # ── тип граматики ──────────────────────────────────────────────────────────
    is_simple = (
        info["all_start_terminal"]
        and not info["has_epsilon_rule"]
        and info["choice_disjoint"]
    )
    is_weakly_separated = (
        info["all_start_terminal"]
        and info["choice_disjoint"]
    )
    is_ll1 = info["choice_disjoint"]

    if is_simple:
        conclusion = "ПРОСТА (розділена) граматика"
    elif is_weakly_separated:
        conclusion = "СЛАБКО-РОЗДІЛЕНА граматика"
    elif is_ll1:
        conclusion = "LL(1) граматика"
    else:
        conclusion = "НЕ є LL(1) граматикою"

    print(f"Тип граматики: {conclusion}")
    print()

    if info["conflict_details"]:
        print("Конфлікти у множині ВИБІР:")
        for d in info["conflict_details"]:
            print(d)
        print()

    # ── команди магазинного автомата ──────────────────────────────────────────
    commands = build_pda_commands(choice)

    print("Команди магазинного автомата:")
    print("  Позначення:")
    print("  f  (s0, вхід, вершина_магазину) = (s, рядок_запису)  — голівка зрушується")
    print("  f* (s0, вхід, вершина_магазину) = (s, рядок_запису)  — голівка не зрушується")
    print("  '$' як рядок_запису означає: виштовхнути без занесення (порожній результат)")
    print()
    for i, cmd in enumerate(commands, 1):
        print(f"  {fmt_command(cmd, i):<55}  # {cmd['comment']}")
    print()

    # ── початкова конфігурація ────────────────────────────────────────────────
    print("Початкова конфігурація:")
    print("  (s0, µ, h0I)")
    print("  де µ — вхідний ланцюжок, h0 — маркер дна магазину,")
    print("  I — стартовий символ граматики.")
    print()

    # ── перевірка тестових рядків ─────────────────────────────────────────────
    print("=" * 70)
    print("ПЕРЕВІРКА ТЕСТОВИХ РЯДКІВ")
    print("=" * 70)
    print()

    test_cases = [
        (source,  "Рядок 1 — простий if без else"),
        (source1, "Рядок 2 — if з else та кількома операторами"),
        (source2, "Рядок 3 — вкладені if-else if-else"),
    ]

    for src, label in test_cases:
        print(f"Вхідний рядок ({label}):")
        print(src)
        print()

        tokens  = scanner(src)
        symbols = tokens_to_grammar_symbols(tokens)

        print("Граматичні символи після сканування:")
        pprint.pprint(symbols)
        print()

        simulate_pda(symbols, commands, label)
        print("-" * 70)
        print()


if __name__ == "__main__":
    main()