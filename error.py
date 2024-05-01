# Сообщения об ошибках
import text


def _error(msg, p):
    while text.ch not in {text.chEOL, text.chEOT}:
        text.next_ch()
    print(' ' * (p - 1), '^', sep='')
    print(msg)
    exit(1)


def lex_error(msg):
    _error('Лексическая ошибка: ' + msg, text.pos)


def expect(msg):
    _error("Ожидается " + msg, text.lex_pos)


def ctx_error(msg):
    _error(msg, text.lex_pos)


def error(msg):
    print()
    print(msg)
    exit(2)


def warning(msg):
    print()
    print(msg)
