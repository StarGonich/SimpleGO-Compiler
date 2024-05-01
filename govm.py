# Виртуальная машина

import error

STOP = -1
ADD = -2
SUB = -3
MULT = -4
DIV = -5
MOD = -6
NEG = -7
LOAD = -8
SAVE = -9
DUP = -10
DROP = -11
SWAP = -12
OVER = -13
GOTO = -14
IFLT = -15
IFLE = -16
IFGT = -17
IFGE = -18
IFEQ = -19
IFNE = -20
IN = -21
OUT = -22
LN = -23

MEM_SIZE = 8 * 1024

M = [STOP] * MEM_SIZE

mnemo = [
    "",
    "STOP",
    "ADD",
    "SUB",
    "MULT",
    "DIV",
    "MOD",
    "NEG",
    "LOAD",
    "SAVE",
    "DUP",
    "DROP",
    "SWAP",
    "OVER",
    "GOTO",
    "IFLT",
    "IFLE",
    "IFGT",
    "IFGE",
    "IFEQ",
    "IFNE",
    "IN",
    "OUT",
    "LN"
]


def run():
    pc = 0
    sp = MEM_SIZE
    cnt = 0
    while True:
        cnt += 1
        cmd = M[pc]
        pc += 1
        if cmd >= 0:
            sp -= 1
            M[sp] = cmd
        elif cmd == ADD:
            sp += 1
            M[sp] = M[sp] + M[sp - 1]
        elif cmd == SUB:
            sp += 1
            M[sp] = M[sp] - M[sp - 1]
        elif cmd == MULT:
            sp += 1
            M[sp] = M[sp] * M[sp - 1]
        elif cmd == DIV:
            sp += 1
            M[sp] = M[sp] // M[sp - 1]
        elif cmd == MOD:
            sp += 1
            M[sp] = M[sp] % M[sp - 1]
        elif cmd == NEG:
            M[sp] = -M[sp]
        elif cmd == LOAD:
            M[sp] = M[M[sp]]
        elif cmd == SAVE:
            M[M[sp + 1]] = M[sp]
            sp += 2
        elif cmd == DUP:
            M[sp - 1] = M[sp]
            sp -= 1
        elif cmd == DROP:
            sp += 1
        elif cmd == SWAP:
            temp = M[sp]
            M[sp] = M[sp + 1]
            M[sp + 1] = temp
        elif cmd == OVER:
            sp -= 1
            M[sp] = M[sp + 2]
        elif cmd == GOTO:
            pc = M[sp]
            sp += 1
        elif cmd == IFEQ:
            if M[sp + 2] == M[sp + 1]:
                pc = M[sp]
            sp += 3
        elif cmd == IFNE:
            if M[sp + 2] != M[sp + 1]:
                pc = M[sp]
            sp += 3
        elif cmd == IFLT:
            if M[sp + 2] < M[sp + 1]:
                pc = M[sp]
            sp += 3
        elif cmd == IFLE:
            if M[sp + 2] <= M[sp + 1]:
                pc = M[sp]
            sp += 3
        elif cmd == IFGT:
            if M[sp + 2] > M[sp + 1]:
                pc = M[sp]
            sp += 3
        elif cmd == IFGE:
            if M[sp + 2] >= M[sp + 1]:
                pc = M[sp]
            sp += 3
        elif cmd == IN:
            sp -= 1
            try:
                M[sp] = int(input('?'))
            except ValueError:
                error.error('Неправильный ввод')
        elif cmd == OUT:
            print(f'{M[sp + 1]:{M[sp]}}', end='')
            sp += 2
        elif cmd == LN:
            print()
        elif cmd == STOP:
            break
        else:
            error.error('Недопустимая команда')

    # print("\nКоличество тактов", cnt)
    if sp < MEM_SIZE:
        print('Код возврата', M[sp])


def print_code(pc):
    for pc in range(0, pc):
        print(pc, ') ', M[pc] if M[pc] >= 0 else mnemo[-M[pc]])
