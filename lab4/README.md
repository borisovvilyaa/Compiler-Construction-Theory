# ЛАБОРАТОРНА РОБОТА № 4
## Визначення типу граматики

**Студент:** Борисов Ілля  
**Група:** КН-Н921  
**Варіант:** 7  

---

## 1. Постановка задачі

Відповідно до правил граматики, побудованих у лабораторній роботі 3, визначити тип граматики. Для цього необхідно:

1. Побудувати функцію ПЕРШ(µ).
2. Побудувати функцію СЛІД(µ).
3. Побудувати множину ВИБІР.
4. Визначити тип граматики: проста, слабко-розділена або LL(1).

---

## 2. Правила граматики

Граматика описує конструкцію `if-else` та була побудована у лабораторній роботі 3:

| № | Правило |
|---|---------|
| 1 | `I -> If ( A ) { B ; R } C` |
| 2 | `A -> exp` |
| 3 | `B -> smth` |
| 4 | `R -> B ; R` |
| 5 | `R -> $` |
| 6 | `C -> Else X` |
| 7 | `C -> $` |
| 8 | `X -> { B ; R }` |
| 9 | `X -> I` |

**Нетермінали:** `I, A, B, R, C, X`  
**Термінали:** `If, (, ), {, }, ;, exp, smth, Else`  
**Епсилон:** `$`  
**Маркер кінця:** `#`

---

## 3. Функція ПЕРШ(µ)

Функція ПЕРШ(µ) визначає множину термінальних символів, що можуть стояти на першому місці в ланцюжках, виведених з ланцюжка µ.

**Правила обчислення:**
- якщо µ починається терміналом `b` → ПЕРШ(µ) = `{b}`
- якщо µ = `$` → ПЕРШ(µ) = `{$}`
- якщо µ починається нетерміналом `B` і `B` не анулює → ПЕРШ(µ) = об'єднання ПЕРШ усіх правил для `B`
- якщо µ починається нетерміналом `B` і `B` анулює → ПЕРШ(µ) = ПЕРШ(решти ланцюжка) ∪ ПЕРШ усіх правил для `B`

### ПЕРШ для кожного правила:

| Правило | ПЕРШ |
|---------|------|
| `I -> If ( A ) { B ; R } C` | `{If}` |
| `A -> exp` | `{exp}` |
| `B -> smth` | `{smth}` |
| `R -> B ; R` | `{smth}` |
| `R -> $` | `{$}` |
| `C -> Else X` | `{Else}` |
| `C -> $` | `{$}` |
| `X -> { B ; R }` | `{{}` |
| `X -> I` | `{If}` |

### ПЕРШ для нетерміналів:

| Нетермінал | ПЕРШ |
|------------|------|
| `A` | `{exp}` |
| `B` | `{smth}` |
| `C` | `{Else, $}` |
| `I` | `{If}` |
| `R` | `{smth, $}` |
| `X` | `{If, {}` |

---

## 4. Функція СЛІД(µ)

Функція СЛІД(B) визначає множину термінальних символів, що можуть стояти безпосередньо після нетермінала `B` у ланцюжках, виведених з початкового символу граматики.

**Правила обчислення:**
- стартовий символ `I` отримує маркер кінця `#`
- якщо є правило `X -> µBα` і `α` не анулює → СЛІД(B) ⊇ ПЕРШ(α)
- якщо є правило `X -> µBα` і `α` анулює → СЛІД(B) ⊇ ПЕРШ(α) ∪ СЛІД(X)
- якщо є правило `X -> µB` → СЛІД(B) ⊇ СЛІД(X)

### Обчислення СЛІД:

**СЛІД(I):**  
`I` є стартовим символом → `{#}`  
`I` входить у праву частину правила `X -> I` → СЛІД(I) ⊇ СЛІД(X) = `{#}`  
Отже: **СЛІД(I) = `{#}`**

**СЛІД(A):**  
`A` входить у правило `I -> If ( A ) { B ; R } C`, після `A` стоїть `)` → СЛІД(A) ⊇ `{)}`  
Отже: **СЛІД(A) = `{)}`**

**СЛІД(B):**  
`B` входить у правила `I -> ... { B ; R } C` та `R -> B ; R` та `X -> { B ; R }`, після `B` стоїть `;`  
Отже: **СЛІД(B) = `{;}`**

**СЛІД(R):**  
`R` входить у правила `I -> ... R } C` та `R -> B ; R` та `X -> { B ; R }`, після `R` стоїть `}`  
Отже: **СЛІД(R) = `{}`}`**

**СЛІД(C):**  
`C` входить у правило `I -> ... } C`, `C` стоїть в кінці → СЛІД(C) ⊇ СЛІД(I) = `{#}`  
Отже: **СЛІД(C) = `{#}`**

**СЛІД(X):**  
`X` входить у правило `C -> Else X`, `X` стоїть в кінці → СЛІД(X) ⊇ СЛІД(C) = `{#}`  
Отже: **СЛІД(X) = `{#}`**

### Зведена таблиця СЛІД:

| Нетермінал | СЛІД |
|------------|------|
| `I` | `{#}` |
| `A` | `{)}` |
| `B` | `{;}` |
| `R` | `{}}`  |
| `C` | `{#}` |
| `X` | `{#}` |

---

## 5. Множина ВИБІР

Множина ВИБІР визначається для кожного правила граматики:
- якщо правило не анулює → ВИБІР(B → µ) = ПЕРШ(µ)
- якщо правило анулює → ВИБІР(B → $) = СЛІД(B)

| Правило | ВИБІР |
|---------|-------|
| `I -> If ( A ) { B ; R } C` | `{If}` |
| `A -> exp` | `{exp}` |
| `B -> smth` | `{smth}` |
| `R -> B ; R` | `{smth}` |
| `R -> $` | `{}}` |
| `C -> Else X` | `{Else}` |
| `C -> $` | `{#}` |
| `X -> { B ; R }` | `{{}` |
| `X -> I` | `{If}` |

---

## 6. Визначення типу граматики

Перевіряємо три умови:

**Умова 1** — права частина кожного правила являє собою або `$`, або починається з термінального чи нетермінального символу:  
✅ Виконується. Проте правило `X -> I` починається нетерміналом, тому граматика **не є простою і не є слабко-розділеною**.

**Умова 2** — якщо два правила мають однакові ліві частини, праві частини повинні починатися різними символами:  
✅ Виконується для всіх пар правил.

**Умова 3** — множини ВИБІР для правил з однаковою лівою частиною не перетинаються:

| Нетермінал | Правила | ВИБІР | Перетин |
|------------|---------|-------|---------|
| `R` | `R -> B ; R` | `{smth}` | — |
| | `R -> $` | `{}}` | `∅` ✅ |
| `C` | `C -> Else X` | `{Else}` | — |
| | `C -> $` | `{#}` | `∅` ✅ |
| `X` | `X -> { B ; R }` | `{{}` | — |
| | `X -> I` | `{If}` | `∅` ✅ |

✅ Виконується. Всі множини ВИБІР для правил з однаковими лівими частинами не перетинаються.

**Висновок:** граматика є **LL(1) граматикою**.

Граматика не є простою і не є слабко-розділеною, оскільки правило `X -> I` має праву частину що починається нетерміналом. Однак усі три умови LL(1) виконуються — зокрема множини ВИБІР для нетерміналів `R`, `C` та `X` не мають спільних елементів. Це означає, що парсер завжди може однозначно вибрати потрібне правило, дивлячись лише на один поточний токен.

---

## 7. Програмна реалізація (Python)

```python
"""
Lab 4 - Визначення типу граматики (ПЕРШ, СЛІД, ВИБІР)
Граматика if-else:
    1. I  -> If(A){B;R}C
    2. A  -> exp
    3. B  -> smth
    4. R  -> B;R | $
    5. C  -> Else X | $
    6. X  -> {B;R} | I
"""

import pprint

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


def get_rules_for(nt):
    """Return all right-hand sides for the given non-terminal."""
    return [rhs for (lhs, rhs) in RULES if lhs == nt]


def first_of_sequence(seq, visiting=None):
    """
    Compute FIRST for a sequence of grammar symbols.
    Returns a set of terminals (may include EPSILON).
    """
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
    """
    Compute FIRST for a non-terminal.
    Returns the union of FIRST sets for all its productions.
    """
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
    """Compute FIRST for every grammar rule."""
    result = {}
    for (lhs, rhs) in RULES:
        key = f"{lhs} -> {' '.join(rhs)}"
        result[key] = first_of_sequence(rhs)
    return result


def compute_follow():
    """
    Compute FOLLOW for every non-terminal.
    The start symbol I receives the end-marker #.
    Uses iterative fixed-point algorithm.
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


def compute_choice(follow):
    """
    Compute CHOICE for every grammar rule.

    ВИБІР(B -> µ):
      - µ does not derive ε : FIRST(µ)
      - µ derives ε         : (FIRST(µ) \\ {$}) ∪ FOLLOW(B)
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


def determine_grammar_type(follow):
    """
    Classify the grammar as simple, weakly separated, LL(1), or not LL(1).
    Returns a dict with classification flags and conflict details.
    """
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


def fmt_set(s):
    """Format a set: terminals alphabetically, $ and # always last."""
    terminals = sorted(x for x in s if x not in (EPSILON, END_MARKER))
    extras    = sorted(x for x in s if x in (EPSILON, END_MARKER))
    return "{" + ", ".join(terminals + extras) + "}"


def main():
    print("Правила граматики:")
    for i, (lhs, rhs) in enumerate(RULES, 1):
        print(f"  {i}. {lhs} -> {' '.join(rhs)}")
    print()

    first_all = compute_first_all()
    print("Функція ПЕРШ(µ) для кожного правила:")
    for rule_key, first_set in first_all.items():
        print(f"  ПЕРШ({rule_key}) = {fmt_set(first_set)}")
    print()

    print("Функція ПЕРШ(µ) для нетерміналів:")
    for nt in sorted(NON_TERMINALS):
        print(f"  ПЕРШ({nt}) = {fmt_set(first_of_nt(nt))}")
    print()

    follow = compute_follow()
    print("Функція СЛІД(µ):")
    for nt in sorted(NON_TERMINALS):
        print(f"  СЛІД({nt}) = {fmt_set(follow[nt])}")
    print()

    info   = determine_grammar_type(follow)
    choice = info["choice"]

    print("Множина ВИБІР:")
    for rule_key, choice_set in choice.items():
        print(f"  ВИБІР({rule_key}) = {fmt_set(choice_set)}")
    print()

    is_simple           = (
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

    print("Пояснення:")
    if is_simple:
        print("  - Права частина кожного правила починається терміналом.")
        print("  - Анулюючих правил немає.")
        print("  - Множини ВИБІР для правил з однаковими лівими не перетинаються.")
        print("  => Граматика є простою (розділеною), а відтак також слабко-розділеною та LL(1).")
    elif is_weakly_separated:
        print("  - Права частина кожного правила — або $ або починається терміналом.")
        print("  - Граматика містить анулюючі правила.")
        print("  - Множини ВИБІР для правил з однаковими лівими не перетинаються.")
        print("  => Граматика є слабко-розділеною (і, як наслідок, LL(1)).")
    elif is_ll1:
        print("  - Правило X -> I має праву частину що починається нетерміналом,")
        print("    тому граматика не є ні простою, ні слабко-розділеною.")
        print("  - Множини ВИБІР для правил з однаковими лівими не перетинаються:")
        for nt in sorted(NON_TERMINALS):
            nt_keys = [
                f"{lhs} -> {' '.join(rhs)}"
                for (lhs, rhs) in RULES
                if lhs == nt
            ]
            if len(nt_keys) < 2:
                continue
            for k in nt_keys:
                print(f"    ВИБІР({k}) = {fmt_set(choice[k])}")
        print("  => Граматика є LL(1) граматикою.")
    else:
        print("  - Множини ВИБІР для деяких правил з однаковими лівими перетинаються.")
        print("  => Граматика не є детермінованою і не належить до жодного з розглянутих класів.")


if __name__ == "__main__":
    main()
```

---

## 8. Результати роботи програми
Правила граматики:

I -> If ( A ) { B ; R } C
A -> exp
B -> smth
R -> B ; R
R -> $
C -> Else X
C -> $
X -> { B ; R }
X -> I

Функція ПЕРШ(µ) для кожного правила:
  ПЕРШ(I -> If ( A ) { B ; R } C) = {If}
  ПЕРШ(A -> exp) = {exp}
  ПЕРШ(B -> smth) = {smth}
  ПЕРШ(R -> B ; R) = {smth}
  ПЕРШ(R -> ) = {
}
  ПЕРШ(C -> Else X) = {Else}
  ПЕРШ(C -> ) = {
}
  ПЕРШ(X -> { B ; R }) = {{}
  ПЕРШ(X -> I) = {If}
Функція ПЕРШ(µ) для нетерміналів:
ПЕРШ(A) = {exp}
ПЕРШ(B) = {smth}
ПЕРШ(C) = {Else, $}
ПЕРШ(I) = {If}
ПЕРШ(R) = {smth, $}
ПЕРШ(X) = {If, {}
Функція СЛІД(µ):
СЛІД(A) = {)}
СЛІД(B) = {;}
СЛІД(C) = {#}
СЛІД(I) = {#}
СЛІД(R) = {}}
СЛІД(X) = {#}
Множина ВИБІР:
ВИБІР(I -> If ( A ) { B ; R } C) = {If}
ВИБІР(A -> exp) = {exp}
ВИБІР(B -> smth) = {smth}
ВИБІР(R -> B ; R) = {smth}
ВИБІР(R -> $) = {}}
ВИБІР(C -> Else X) = {Else}
ВИБІР(C -> $) = {#}
ВИБІР(X -> { B ; R }) = {{}
ВИБІР(X -> I) = {If}
Тип граматики: LL(1) граматика
Пояснення:

Правило X -> I має праву частину що починається нетерміналом,
тому граматика не є ні простою, ні слабко-розділеною.
Множини ВИБІР для правил з однаковими лівими не перетинаються:
ВИБІР(R -> B ; R) = {smth}
ВИБІР(R -> $) = {}}
ВИБІР(C -> Else X) = {Else}
ВИБІР(C -> $) = {#}
ВИБІР(X -> { B ; R }) = {{}
ВИБІР(X -> I) = {If}
=> Граматика є LL(1) граматикою.

---

## 9. Висновки

У ході виконання лабораторної роботи:

1. Побудовано функцію ПЕРШ(µ) для кожного правила граматики та для кожного нетермінала. Визначено що нетермінали `R` та `C` є анулюючими, оскільки мають правила з епсилон.

2. Побудовано функцію СЛІД(µ) для кожного нетермінала ітеративним методом. Стартовий символ `I` отримав маркер кінця `#`, решта нетерміналів отримали свої множини на основі контексту їх входження у правила.

3. Побудовано множину ВИБІР для кожного правила граматики. Для анулюючих правил (`R -> $`, `C -> $`) множина ВИБІР визначається через функцію СЛІД відповідного нетермінала.

4. Визначено тип граматики — **LL(1)**. Граматика не є простою і не є слабко-розділеною через правило `X -> I`, права частина якого починається нетерміналом. Однак множини ВИБІР для всіх пар правил з однаковими лівими частинами (`R`, `C`, `X`) не перетинаються, що є достатньою умовою для LL(1).

5. Реалізовано програму мовою **Python** що автоматично обчислює функції ПЕРШ, СЛІД та множину ВИБІР для заданої граматики і визначає її тип.
