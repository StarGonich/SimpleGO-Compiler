from enum import Enum
import text
import error


class Lex(Enum):
    NONE, IDENTIFIER, NUM, STRING, EOT, \
        CONST, ELSE, FOR, FUNC, IF, IMPORT, PACKAGE, VAR, \
        PLUS, MINUS, MUL, DIV, MOD, AMPER, EQ, EQEQ, NE, LT, LE, GT, GE, \
        LPAR, RPAR, BEGIN, END, COMMA, DOT = range(32)


lex = Lex.NONE
name = ''
num = 0
string_literal = ''
MAXINT = 0x7FFFFFFF
with open('go_letters.txt', 'r', encoding='utf-8') as file:
    go_letter = file.read() + '_'
go_letter_or_digit = go_letter + '0123456789'
semicolon = False


def get_lex_name(lex_name):
    return names.get(lex_name, lex_name.name)


keywords = {
    'break': Lex.NONE,
    'case': Lex.NONE,
    'chan': Lex.NONE,
    'const': Lex.CONST,
    'continue': Lex.NONE,
    'default': Lex.NONE,
    'defer': Lex.NONE,
    'else': Lex.ELSE,
    'fallthrough': Lex.NONE,
    'for': Lex.FOR,
    'func': Lex.FUNC,
    'go': Lex.NONE,
    'goto': Lex.NONE,
    'if': Lex.IF,
    'import': Lex.IMPORT,
    'interface': Lex.NONE,
    'map': Lex.NONE,
    'package': Lex.PACKAGE,
    'range': Lex.NONE,
    'return': Lex.NONE,
    'select': Lex.NONE,
    'struct': Lex.NONE,
    'switch': Lex.NONE,
    'type': Lex.NONE,
    'var': Lex.VAR,
}


names = {
    Lex.IDENTIFIER: 'имя',
    Lex.NUM: 'число',
    Lex.STRING: 'строка',
    Lex.PLUS: '"+"',
    Lex.MINUS: '"-"',
    Lex.MUL: '"*"',
    Lex.DIV: '"/"',
    Lex.MOD: '"%"',
    Lex.EQ: '"="',
    Lex.EQEQ: '"=="',
    Lex.NE: '"!="',
    Lex.LT: '"<"',
    Lex.LE: '"<="',
    Lex.GT: '">"',
    Lex.GE: '">="',
    Lex.COMMA: '","',
    Lex.DOT: '"."',
    Lex.LPAR: '"("',
    Lex.RPAR: '")"',
    Lex.BEGIN: '"{"',
    Lex.END: '"}"',
    Lex.EOT: 'конец текста'
}


def semi():
    global semicolon
    if not semicolon:
        error.lex_error('Ожидается ";", или перевод строки')
    semicolon = False


def line_comment():
    text.next_ch()
    while text.ch not in {text.chEOL, text.chEOT}:
        text.next_ch()


def general_comment():
    text.next_ch()
    while True:
        if text.ch == '*':
            text.next_ch()
            if text.ch == '/':
                text.next_ch()
                break
        elif text.ch == text.chEOT:
            error.lex_error('Не закончен комментарий')
        else:
            text.next_ch()


def next_lex():
    global lex, name, num, string_literal, semicolon
    while text.ch in {text.chSPACE, text.chTAB, text.chFF}:
        text.next_ch()
    text.lex_pos = text.pos
    match text.ch:
        # Идентификаторы
        case _ if text.ch in go_letter:
            name = text.ch
            text.next_ch()
            while text.ch in go_letter_or_digit:
                name += text.ch
                text.next_ch()
            lex = keywords.get(name, Lex.IDENTIFIER)

        # Литералы
        case _ if text.ch in '0123456789':
            num = 0
            while text.ch in '0123456789':
                if num <= (MAXINT - int(text.ch)) // 10:
                    num = 10 * num + int(text.ch)
                else:
                    error.lex_error("Слишком большое число")
                text.next_ch()
            lex = Lex.NUM
        case '"':  # StringLiteral
            string_literal = ''
            text.next_ch()
            while True:
                if text.ch == '"':
                    text.next_ch()
                    lex = Lex.STRING
                    break
                elif text.ch == text.chEOT:
                    error.lex_error('Не закончена строка')
                else:
                    string_literal += text.ch
                    text.next_ch()

        # Операторы
        case '+':
            text.next_ch()
            lex = Lex.PLUS
        case '-':
            text.next_ch()
            lex = Lex.MINUS
        case '*':
            text.next_ch()
            lex = Lex.MUL
        case '/':
            text.next_ch()
            if text.ch == '/':
                line_comment()
                next_lex()
            elif text.ch == '*':
                general_comment()
                next_lex()
            else:
                lex = Lex.DIV
        case '%':
            text.next_ch()
            lex = Lex.MOD
        case '&':
            text.next_ch()
            lex = Lex.AMPER
        case '=':
            text.next_ch()
            if text.ch == '=':
                text.next_ch()
                lex = Lex.EQEQ
            else:
                lex = Lex.EQ
        case '!':
            text.next_ch()
            if text.ch == '=':
                text.next_ch()
                lex = Lex.NE
            else:
                error.lex_error('Ожидается =')
        case '<':
            text.next_ch()
            if text.ch == '=':
                text.next_ch()
                lex = Lex.LE
            else:
                lex = Lex.LT
        case '>':
            text.next_ch()
            if text.ch == '=':
                text.next_ch()
                lex = Lex.GE
            else:
                lex = Lex.GT

        # Разделители
        case '(':
            text.next_ch()
            lex = Lex.LPAR
        case ')':
            text.next_ch()
            lex = Lex.RPAR
        case '{':
            text.next_ch()
            lex = Lex.BEGIN
        case '}':
            text.next_ch()
            lex = Lex.END
        case ',':
            text.next_ch()
            lex = Lex.COMMA
        case '.':
            text.next_ch()
            lex = Lex.DOT
        case ';' | text.chEOL:
            text.next_ch()
            semicolon = True
            next_lex()
        case text.chEOT:
            lex = Lex.EOT
        case _:
            error.lex_error('Недопустимый символ под unicode ' + str(ord(text.ch)))
