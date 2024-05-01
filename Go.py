# Компилятор языка "Go"
import lexer
import parser
import text
# import pars
import govm
import gen
import time


def test_text():
    while text.ch != text.chEOT:
        text.next_ch()


def test_lexer():
    text.next_ch()
    lexer.next_lex()
    n = 0
    while lexer.lex != lexer.Lex.EOT:
        n += 1
        # print(lexer.lex)
        lexer.next_lex()
    print("Число лексем", n)


print('Компилятор языка "Go"')
print("----------------------------------")
text.reset()
# test_text()
# test_lexer()
parser.golang_compile()
print("----------------------------------")
print("Компиляция завершена")
print("----------------------------------")
govm.print_code(gen.PC)
print("----------------------------------")
t1 = time.time()
govm.run()
t2 = time.time()
print("----------------------------------")
print(f"Время работы {(t2 - t1):0.3} c")
print("----------------------------------")
