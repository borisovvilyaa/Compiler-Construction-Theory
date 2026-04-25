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


# ── допоміжні функції ─────────────────────────────────────────────────────────

def get_rules_for(nt):
    """Return all right-hand sides for the given non-terminal."""
    return [rhs for (lhs, rhs) in RULES if lhs == nt]


# ── функція ПЕРШ ──────────────────────────────────────────────────────────────

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


# ── функція СЛІД ──────────────────────────────────────────────────────────────

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


# ── множина ВИБІР ─────────────────────────────────────────────────────────────

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


# ── визначення типу граматики ─────────────────────────────────────────────────

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


# ── форматування множини ──────────────────────────────────────────────────────

def fmt_set(s):
    """Format a set: terminals alphabetically, $ and # always last."""
    terminals = sorted(x for x in s if x not in (EPSILON, END_MARKER))
    extras    = sorted(x for x in s if x in (EPSILON, END_MARKER))
    return "{" + ", ".join(terminals + extras) + "}"


# ── головна функція ───────────────────────────────────────────────────────────

def main():
    # ── правила ──
    print("Правила граматики:")
    for i, (lhs, rhs) in enumerate(RULES, 1):
        print(f"  {i}. {lhs} -> {' '.join(rhs)}")
    print()

    # ── ПЕРШ для кожного правила ──
    first_all = compute_first_all()
    print("Функція ПЕРШ(µ) для кожного правила:")
    for rule_key, first_set in first_all.items():
        print(f"  ПЕРШ({rule_key}) = {fmt_set(first_set)}")
    print()

    print("Функція ПЕРШ(µ) для нетерміналів:")
    for nt in sorted(NON_TERMINALS):
        print(f"  ПЕРШ({nt}) = {fmt_set(first_of_nt(nt))}")
    print()

    # ── СЛІД ──
    follow = compute_follow()
    print("Функція СЛІД(µ):")
    for nt in sorted(NON_TERMINALS):
        print(f"  СЛІД({nt}) = {fmt_set(follow[nt])}")
    print()

    # ── ВИБІР ──
    info   = determine_grammar_type(follow)
    choice = info["choice"]

    print("Множина ВИБІР:")
    for rule_key, choice_set in choice.items():
        print(f"  ВИБІР({rule_key}) = {fmt_set(choice_set)}")
    print()

    # ── тип граматики ──
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