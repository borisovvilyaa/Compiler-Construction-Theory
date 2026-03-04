const source = `if ( expr ){
    stmt1;
}`;

const source1 = `if ( expr ){
    stmt;
}
else {
    stmt;
    stmt;
    stmt;
}`;

const source2 = `if ( expr ){
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
}`;

// які ключові слова ми розпізнаємо
const KEYWORDS = new Set(['if', 'else']);

// які символи вважаємо роздільниками
const DELIMITERS = new Set(['(', ')', '{', '}', ';']);

// таблиця переходів між станами автомата
// transitionTable[поточний_стан][клас_символу] = наступний_стан
const transitionTable = {
    S0: { space: 'S0', letter: 'S1', digit: 'S2', delim: 'S0',    other: 'S_ERR' },
    S1: { space: 'S0', letter: 'S1', digit: 'S1', delim: 'S0',    other: 'S_ERR' },
    S2: { space: 'S0', letter: 'S_ERR', digit: 'S2', delim: 'S0', other: 'S_ERR' },
};

// визначаємо до якого класу відноситься символ
function getCharClass(ch) {
    if (' \t\n\r'.includes(ch)) return 'space';
    if (/[a-zA-Z_]/.test(ch))  return 'letter';
    if (/[0-9]/.test(ch))      return 'digit';
    if (DELIMITERS.has(ch))    return 'delim';
    return 'other';
}

function scanner(source) {
    const chars = Array.from(source);
    let tokens = [];
    let state = 'S0';
    let lexeme = [];

    // якщо накопичили слово - визначаємо це ключове слово чи ідентифікатор
    function flushWord() {
        if (lexeme.length === 0) return;
        const word = lexeme.join('');
        tokens.push(KEYWORDS.has(word)
            ? { type: 'KEYWORD',    value: word }
            : { type: 'IDENTIFIER', value: word }
        );
        lexeme = [];
    }

    // якщо накопичили цифри - це число
    function flushNum() {
        if (lexeme.length === 0) return;
        tokens.push({ type: 'NUMBER', value: lexeme.join('') });
        lexeme = [];
    }

    for (let i = 0; i < chars.length; i++) {
        const cls = getCharClass(chars[i]);

        // дивимось куди переходимо з поточного стану
        const nextState = transitionTable[state][cls];

        // якщо наступний стан помилковий - зупиняємось
        if (nextState === 'S_ERR') {
            tokens.push({ type: 'ERROR', value: chars[i], pos: i });
            return tokens;
        }

        if (state === 'S0') {
            if (cls === 'letter' || cls === 'digit') {
                lexeme.push(chars[i]);
            }
            else if (cls === 'delim') {
                tokens.push({ type: 'DELIMITER', value: chars[i] });
            }
            // пробіл просто пропускаємо
        }
        else if (state === 'S1') {
            if (cls === 'letter' || cls === 'digit') {
                lexeme.push(chars[i]);
            }
            else if (cls === 'space') {
                flushWord();
            }
            else if (cls === 'delim') {
                flushWord();
                tokens.push({ type: 'DELIMITER', value: chars[i] });
            }
        }
        else if (state === 'S2') {
            if (cls === 'digit') {
                lexeme.push(chars[i]);
            }
            else if (cls === 'space') {
                flushNum();
            }
            else if (cls === 'delim') {
                flushNum();
                tokens.push({ type: 'DELIMITER', value: chars[i] });
            }
        }

        state = nextState;
    }

    // виділяємо залишок якщо рядок закінчився без роздільника
    flushWord();
    flushNum();

    return tokens;
}

console.log('Рядок 1:\n',  scanner(source));
console.log('Рядок 2:\n', scanner(source1));
console.log('Рядок 3:\n', scanner(source2));