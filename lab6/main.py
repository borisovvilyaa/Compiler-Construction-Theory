import re
import pprint

# ── test input strings ────────────────────────────────────────────────────────

source = """if ( expr ){
    stmt1;
]
"""

source1 = """if ( expr ){
    stmt;
}
else {
    1stmt;
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
    }
}
"""

# ── grammar rules ─────────────────────────────────────────────────────────────

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


# ── scanner ───────────────────────────────────────────────────────────────────

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
    """Determine character class for the transition table."""
    if REGEX_SPACE.match(ch):  return 'space'
    if REGEX_LETTER.match(ch): return 'letter'
    if REGEX_DIGIT.match(ch):  return 'digit'
    if REGEX_DELIM.match(ch):  return 'delim'
    return 'other'

def scanner(source):
    """Tokenize the input string using a finite automaton."""
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


# ── convert scanner tokens to grammar symbols ─────────────────────────────────

def tokens_to_grammar_symbols(tokens):
    """
    Map scanner tokens to grammar terminal symbols.
    'if' -> 'If', 'else' -> 'Else',
    identifiers starting with 'expr' -> 'exp', others -> 'smth',
    delimiters -> corresponding terminal.
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


# ── grammar helper functions ──────────────────────────────────────────────────

def get_rules_for(nt):
    """Return all right-hand sides for the given non-terminal."""
    return [rhs for (lhs, rhs) in RULES if lhs == nt]


# ── FIRST function ────────────────────────────────────────────────────────────

def first_of_sequence(seq, visiting=None):
    """Compute the FIRST set for a sequence of grammar symbols."""
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
    """Compute the FIRST set for a non-terminal."""
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


# ── FOLLOW function ───────────────────────────────────────────────────────────

def compute_follow():
    """
    Compute the FOLLOW set for every non-terminal.
    The start symbol I receives the end-marker #.
    Uses a fixed-point iteration algorithm.
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


# ── SELECT set ────────────────────────────────────────────────────────────────

def compute_choice(follow):
    """
    Compute the SELECT (CHOICE) set for every grammar rule.

    SELECT(B -> µ):
      - if µ does not derive ε : FIRST(µ)
      - if µ derives ε         : (FIRST(µ) \\ {$}) ∪ FOLLOW(B)
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


# ── grammar type classification ───────────────────────────────────────────────

def determine_grammar_type(follow):
    """Classify the grammar and return a dict with analysis results."""
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
                        f"  SELECT({nt_keys[i]}) ∩ "
                        f"SELECT({nt_keys[j]}) = {{ {', '.join(sorted(inter))} }}"
                    )

    return {
        "choice":             choice,
        "all_start_terminal": all_start_terminal,
        "has_epsilon_rule":   has_epsilon_rule,
        "choice_disjoint":    choice_disjoint,
        "conflict_details":   conflict_details,
    }


# ── set formatting helper ──────────────────────────────────────────────────────

def fmt_set(s):
    """Format a set: terminals alphabetically, $ and # always last."""
    terminals = sorted(x for x in s if x not in (EPSILON, END_MARKER))
    extras    = sorted(x for x in s if x in (EPSILON, END_MARKER))
    return "{" + ", ".join(terminals + extras) + "}"


# ══════════════════════════════════════════════════════════════════════════════
# LAB 5 — PDA COMMAND CONSTRUCTION
# ══════════════════════════════════════════════════════════════════════════════

def build_pda_commands(choice):
    """
    Build all pushdown automaton (PDA) transition commands.

    Command types (per the lab guidelines):
      Type 1 – rule starts with a terminal  A -> b α
               f(s0, b, A) = (s, mirror(α))      [head advances]
      Type 2 – rule starts with a non-terminal  A -> B α
               f*(s0, x, A) = (s, mirror(B α))   [head does not advance],
               one command per element x in SELECT(A -> B α)
      Type 3 – epsilon rule  A -> $
               f*(s0, x, A) = (s, $)             [head does not advance],
               one command per element x in SELECT(A -> $)
      Type 4 – terminal b appears in the middle or at the end of a rule
               f(s0, b, b) = (s, $)              [head advances]
      Type 5 – transition to the accepting state
               f*(s0, $, h0) = (s, $)
    """
    commands = []

    for (lhs, rhs) in RULES:
        rule_key = f"{lhs} -> {' '.join(rhs)}"

        if rhs == [EPSILON]:
            # ── type 3: epsilon rule ──────────────────────────────────────────
            for x in sorted(choice[rule_key]):
                commands.append({
                    "type":    "f*",
                    "input":   x,
                    "stack":   lhs,
                    "result":  "$",
                    "comment": f"Epsilon rule {lhs} -> $",
                })

        elif rhs[0] not in NON_TERMINALS:
            # ── type 1: rule starts with a terminal ───────────────────────────
            # the first terminal is consumed; the rest is pushed in reverse order
            first_terminal = rhs[0]
            rest           = rhs[1:]
            push_str       = " ".join(reversed(rest)) if rest else "$"

            commands.append({
                "type":    "f",
                "input":   first_terminal,
                "stack":   lhs,
                "result":  push_str,
                "comment": f"Rule starts with terminal: {lhs} -> {' '.join(rhs)}",
            })

        else:
            # ── type 2: rule starts with a non-terminal ───────────────────────
            # the entire RHS is pushed in reverse; number of commands = |SELECT|
            push_str = " ".join(reversed(rhs))

            for x in sorted(choice[rule_key]):
                commands.append({
                    "type":    "f*",
                    "input":   x,
                    "stack":   lhs,
                    "result":  push_str,
                    "comment": f"Rule starts with non-terminal: {lhs} -> {' '.join(rhs)}",
                })

    # ── type 4: commands for terminals in the middle/end of rules ─────────────
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
            "comment": f"Terminal match: consume '{t}' from input and stack",
        })

    # ── type 5: transition to the accepting state ─────────────────────────────
    commands.append({
        "type":    "f*",
        "input":   "$",
        "stack":   "h0",
        "result":  "$",
        "comment": "Accept: input and stack are both empty",
    })

    return commands


def fmt_command(cmd, index):
    """Format a single PDA command as a string."""
    return (
        f"{index}. {cmd['type']}(s0, {cmd['input']}, {cmd['stack']}) "
        f"= (s, {cmd['result']})"
    )


# ══════════════════════════════════════════════════════════════════════════════
# LAB 6 — PDA SIMULATION (SYNTAX ANALYSER)
# ══════════════════════════════════════════════════════════════════════════════

def find_command(commands, lexeme, stack_top):
    """
    Find the matching transition command for the current lexeme and stack top.
    Returns (command, 1-based index) or (None, -1) if not found.
    """
    for i, cmd in enumerate(commands):
        if cmd["input"] == lexeme and cmd["stack"] == stack_top:
            return cmd, i + 1
    return None, -1


def simulate_pda(input_tokens, commands, label):
    """
    Simulate the pushdown automaton on a sequence of grammar symbols.
    Prints configuration changes in the textual format used in the lab manual.

    Parameters
    ----------
    input_tokens : list[str]   — sequence of grammar symbols (without end-marker)
    commands     : list[dict]  — PDA commands built by build_pda_commands()
    label        : str         — test-case label used in the header
    """
    print(f"CHECKING INPUT CHAIN: {label}")

    # Input tape ends with the end-marker #
    tape  = list(input_tokens) + [END_MARKER]
    # Stack: index 0 = bottom (h0), index -1 = top; initially h0 and start symbol I
    stack = ["h0", "I"]

    # Print initial configuration
    tape_str  = "".join(tape[:-1]) + tape[-1]
    stack_str = "".join(reversed(stack))
    print(f"({tape_str}, {stack_str})", end="")

    step = 0
    ok   = False

    while True:
        lexeme    = tape[0]
        stack_top = stack[-1] if stack else None

        # Acceptance condition: both input and stack are exhausted
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
            print("  ANALYSIS ERROR — stack is empty but input is not exhausted")
            break

        cmd, idx = find_command(commands, lexeme, stack_top)

        if cmd is None:
            print()
            print(
                f"  ANALYSIS ERROR — no command found for "
                f"(input='{lexeme}', stack_top='{stack_top}')"
            )
            break

        # Pop the stack top
        stack.pop()

        if cmd["type"] == "f":
            # Advance the input head (consume the lexeme)
            tape.pop(0)

        # Push the result string onto the stack in reverse order
        result_str = cmd["result"]
        if result_str != "$":
            for tok in result_str.split():
                stack.append(tok)

        # Build the current configuration string
        tape_str  = "".join(tape[:-1]) + tape[-1] if len(tape) > 1 else tape[0]
        stack_str = "".join(reversed(stack)) if stack else "$"
        print(f" ├ {idx}")
        print(f"({tape_str}, {stack_str})", end="")

        step += 1
        if step > 10_000:
            print()
            print("  ANALYSIS ERROR — maximum step count exceeded")
            break

    print()
    if ok:
        print("Result: CHAIN ACCEPTED (Analysis OK)")
    else:
        print("Result: CHAIN REJECTED (Analysis ERROR)")
    print()


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    # ── grammar rules ─────────────────────────────────────────────────────────
    print("Grammar rules:")
    for i, (lhs, rhs) in enumerate(RULES, 1):
        print(f"  {i}. {lhs} -> {' '.join(rhs)}")
    print()

    # ── FIRST function ─────────────────────────────────────────────────────────
    first_all = compute_first_all()
    print("FIRST(µ) for each grammar rule:")
    for rule_key, first_set in first_all.items():
        print(f"  FIRST({rule_key}) = {fmt_set(first_set)}")
    print()

    print("FIRST(µ) for non-terminals:")
    for nt in sorted(NON_TERMINALS):
        print(f"  FIRST({nt}) = {fmt_set(first_of_nt(nt))}")
    print()

    # ── FOLLOW function ────────────────────────────────────────────────────────
    follow = compute_follow()
    print("FOLLOW(µ):")
    for nt in sorted(NON_TERMINALS):
        print(f"  FOLLOW({nt}) = {fmt_set(follow[nt])}")
    print()

    # ── SELECT set ─────────────────────────────────────────────────────────────
    info   = determine_grammar_type(follow)
    choice = info["choice"]

    print("SELECT set:")
    for rule_key, choice_set in choice.items():
        print(f"  SELECT({rule_key}) = {fmt_set(choice_set)}")
    print()

    # ── grammar type ───────────────────────────────────────────────────────────
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
        conclusion = "SIMPLE (separated) grammar"
    elif is_weakly_separated:
        conclusion = "WEAKLY-SEPARATED grammar"
    elif is_ll1:
        conclusion = "LL(1) grammar"
    else:
        conclusion = "NOT an LL(1) grammar"

    print(f"Grammar type: {conclusion}")
    print()

    if info["conflict_details"]:
        print("Conflicts in SELECT sets:")
        for d in info["conflict_details"]:
            print(d)
        print()

    # ── PDA commands ───────────────────────────────────────────────────────────
    commands = build_pda_commands(choice)

    print("PDA transition commands:")
    print("  Notation:")
    print("  f  (s0, input, stack_top) = (s, push_string)  — head advances")
    print("  f* (s0, input, stack_top) = (s, push_string)  — head does NOT advance")
    print("  '$' as push_string means: pop without pushing (empty result)")
    print()
    for i, cmd in enumerate(commands, 1):
        print(f"  {fmt_command(cmd, i):<55}  # {cmd['comment']}")
    print()

    # ── initial configuration ─────────────────────────────────────────────────
    print("Initial configuration:")
    print("  (s0, µ, h0I)")
    print("  where µ is the input chain, h0 is the stack-bottom marker,")
    print("  and I is the grammar start symbol.")
    print()

    # ── test strings ───────────────────────────────────────────────────────────
    print("=" * 70)
    print("LAB 6 — SYNTAX ANALYSER: CHAIN VERIFICATION")
    print("=" * 70)
    print()

    test_cases = [
        (source,  "String 1 — simple if without else (incomplete / error expected)"),
        (source1, "String 2 — if with else and multiple statements"),
        (source2, "String 3 — nested if-else if-else"),
    ]

    for src, label in test_cases:
        print(f"Input string ({label}):")
        print(src)
        print()

        tokens  = scanner(src)
        symbols = tokens_to_grammar_symbols(tokens)

        print("Grammar symbols after scanning:")
        pprint.pprint(symbols)
        print()

        # Lab 6: run the PDA simulation (syntax analyser verification)
        simulate_pda(symbols, commands, label)
        print("-" * 70)
        print()


if __name__ == "__main__":
    main()