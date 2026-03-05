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

# keywords we recognize
KEYWORDS = {'if', 'else'}

# characters considered delimiters
DELIMITERS = set('(){};')

# transition table between automaton states
# transition_table[current_state][char_class] = next_state
transition_table = {
    'S0': {'space': 'S0', 'letter': 'S1', 'digit': 'S2', 'delim': 'S0',    'other': 'S_ERR'},
    'S1': {'space': 'S0', 'letter': 'S1', 'digit': 'S1', 'delim': 'S0',    'other': 'S_ERR'},
    'S2': {'space': 'S0', 'letter': 'S_ERR', 'digit': 'S2', 'delim': 'S0', 'other': 'S_ERR'},
}

def get_char_class(ch):
    """Determine the character class of a given character."""
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
        """If a word is accumulated, classify it as keyword or identifier."""
        if not lexeme:
            return
        word = ''.join(lexeme)
        if word in KEYWORDS:
            tokens.append({'type': 'KEYWORD',    'value': word})
        else:
            tokens.append({'type': 'IDENTIFIER', 'value': word})
        lexeme.clear()

    def flush_num():
        """If digits are accumulated, emit a number token."""
        if not lexeme:
            return
        tokens.append({'type': 'NUMBER', 'value': ''.join(lexeme)})
        lexeme.clear()

    for i, ch in enumerate(source):
        cls = get_char_class(ch)

        # determine the next state from the transition table
        next_state = transition_table[state][cls]

        # if the next state is an error state, stop scanning
        if next_state == 'S_ERR':
            tokens.append({'type': 'ERROR', 'value': ch, 'pos': i})
            return tokens

        if state == 'S0':
            if cls in ('letter', 'digit'):
                lexeme.append(ch)
            elif cls == 'delim':
                tokens.append({'type': 'DELIMITER', 'value': ch})
            # spaces are simply skipped

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

    # flush any remaining lexeme if the string ended without a delimiter
    flush_word()
    flush_num()

    return tokens

import pprint

print('Рядок 1:')
pprint.pprint(scanner(source))

print('\nРядок 2:')
pprint.pprint(scanner(source1))

print('\nРядок 3:')
pprint.pprint(scanner(source2))