# Генератор кода

import govm
import govm as cm
from lexer import Lex

PC = 0  # Счетчик команд времени компиляции


def cmd(command):
    global PC
    govm.M[PC] = command
    # print('[', PC, ' := ', cmd, ']', sep='', end=' ')
    PC += 1


def const(c):
    cmd(abs(c))
    if c < 0:
        cmd(cm.NEG)


def address(v):
    cmd(v.last_use)
    v.last_use = PC + 1


def compare(op):
    cmd(0)
    if op == Lex.EQEQ:
        cmd(cm.IFNE)
    elif op == Lex.NE:
        cmd(cm.IFEQ)
    elif op == Lex.GE:
        cmd(cm.IFLT)
    elif op == Lex.GT:
        cmd(cm.IFLE)
    elif op == Lex.LE:
        cmd(cm.IFGT)
    elif op == Lex.LT:
        cmd(cm.IFGE)


def fixup(addr, pc):
    while addr > 0:
        temp = govm.M[addr - 2]
        govm.M[addr - 2] = pc
        # print('[', A - 2, ' := ', PC, ']', sep='', end=' ')
        addr = temp
