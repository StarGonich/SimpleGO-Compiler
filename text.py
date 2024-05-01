# Драйвер исходного текста

import sys
import error

# Позиция в строке
pos = 0
lex_pos = 0

chEOT = '\0'
chEOL = '\n'
chSPACE = ' '
chTAB = '\t'
chFF = '\f'

src = ''


def reset():
    global src
    if len(sys.argv) < 2:
        error.error("Запуск: python O.py <файл программы>")
    else:
        try:
            f = open(sys.argv[1], 'r', encoding='utf-8')
            src = f.read()
            f.close()
        except FileNotFoundError:
            error.error("Файл не найден")


i = 0
ch = ''


def next_ch():
    global src, i, ch, pos
    if i < len(src):
        ch = src[i]
        print(ch, end="")
        pos += 1
        i += 1
        if ch in {'\n', '\r'}:
            ch = chEOL
            pos = 0
    else:
        ch = chEOT
