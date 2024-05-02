from enum import Enum

import error
import gen
import govm
import items
import lexer
import table
from text import next_ch
from lexer import next_lex, semi, Lex


class Types(Enum):
    Bool, Int = range(2)


def skip(lex):
    if lexer.lex == lex:
        next_lex()
    else:
        error.expect(lexer.get_lex_name(lex))


def check(lex):
    if lexer.lex != lex:
        error.expect(lexer.get_lex_name(lex))


def golang_compile():
    next_ch()
    next_lex()
    table.open_scope()
    table.new(items.Proc('fmt.Scan'))
    table.new(items.Proc('fmt.Println'))
    table.new(items.Func('math.Abs', Types.Int))
    table.new(items.Type('int', Types.Int))

    table.open_scope()
    source_file()
    packages = table.get_packages()
    for pack in packages:
        if not pack.usage:
            error.error('Пакет ' + pack.name + ' импортирован, но не используется')
    variables = table.get_vars()
    for v in variables:
        if v.last_use > 0:
            gen.fixup(v.last_use, gen.PC)
            gen.cmd(0)
        else:
            error.error('Переменная ' + v.name + ' объявлена, но не используется')
    table.close_scope()

    table.close_scope()


# SourceFile = PackageClause ";" { ImportDecl ";" } FunctionDecl ";" .
def source_file():
    package_clause()
    semi()
    while lexer.lex == Lex.IMPORT:
        import_decl()
        semi()
    function_decl()
    gen.cmd(govm.STOP)


# PackageClause  = "package" PackageName .
# PackageName    = "main" .
def package_clause():
    skip(Lex.PACKAGE)
    check(Lex.IDENTIFIER)
    if lexer.name != 'main':
        error.ctx_error('имя пакета должно быть "main"')
    table.new(items.Package('main'))
    next_lex()


# ImportDecl = "import" ( string_lit | "(" { string_lit ";" } ")" ) .
def import_decl():
    skip(Lex.IMPORT)
    if lexer.lex == Lex.LPAR:
        next_lex()
        while lexer.lex == Lex.STRING:
            if lexer.string_literal not in {"fmt", "math"}:
                error.ctx_error('Предусмотрены только пакеты "fmt" и "math"')
            table.new(items.Package(lexer.string_literal))
            next_lex()
            semi()
        skip(Lex.RPAR)
    else:
        check(Lex.STRING)
        if lexer.string_literal not in {"fmt", "math"}:
            error.ctx_error('Предусмотрены только пакеты "fmt" и "math"')
        table.new(items.Package(lexer.string_literal))
        next_lex()


# FunctionDecl = "func" "main" "(" ")" Block
def function_decl():
    skip(Lex.FUNC)
    check(Lex.IDENTIFIER)
    if lexer.name != 'main':
        error.ctx_error('в пакете main должна быть функция main')
    x = table.find(lexer.name)
    x.usage = True
    next_lex()
    skip(Lex.LPAR)
    skip(Lex.RPAR)
    block()
    semi()


# Block = "{" StatementList "}" .
def block():
    skip(Lex.BEGIN)
    lexer.semicolon = False
    statement_list()
    skip(Lex.END)


# StatementList = { Statement ";" } .
def statement_list():
    while lexer.lex != Lex.END:
        statement()
        semi()


# Statement = Declaration | Assignment | Procedure | IncDecStmt | IfStmt | ForStmt .
def statement():
    if lexer.lex in {Lex.CONST, Lex.VAR}:
        declaration()
    elif lexer.lex == Lex.IDENTIFIER:
        x = table.find(lexer.name)
        if isinstance(x, items.Var):
            next_lex()
            if lexer.lex in {Lex.INC, Lex.DEC}:
                int_dec_stmt(x)
            elif lexer.lex == Lex.EQ:
                assignment(x)
            else:
                error.expect('имя "++", "--" или "="')
        elif isinstance(x, items.Package):
            procedure(x)
        else:
            error.expect('имя переменной или пакета, с последующей функцией')
    elif lexer.lex == Lex.IF:
        if_stmt()
    elif lexer.lex == Lex.FOR:
        for_stmt()


# Declaration   = ConstDecl | VarDecl .
def declaration():
    if lexer.lex == Lex.CONST:
        const_decl()
    else:  # var
        var_decl()


# ConstDecl      = "const" ( ConstSpec | "(" { ConstSpec ";" } ")" ) .
def const_decl():
    next_lex()  # Пропустили "const"
    if lexer.lex == Lex.IDENTIFIER:
        const_spec()
    elif lexer.lex == Lex.LPAR:
        next_lex()
        while lexer.lex == Lex.IDENTIFIER:
            const_spec()
            semi()
        skip(Lex.RPAR)
    else:
        error.expect('имя или "("')


# ConstSpec = identifier [ Type ] "=" ConstExpr .
def const_spec():
    name = lexer.name
    next_lex()  # Пропустили identifier
    if lexer.lex == Lex.IDENTIFIER:  # Type
        if lexer.name != 'int':
            error.ctx_error('Допустим только тип int')
        next_lex()
    skip(Lex.EQ)
    value = const_expr()
    table.new(items.Const(name, Types.Int, value))


# ConstExpr = [ unary_op ] ( number | identifier )
def const_expr():
    sign = 1
    if lexer.lex in {Lex.PLUS, Lex.MINUS}:
        if lexer.lex == Lex.MINUS:
            sign = -1
        next_lex()
    if lexer.lex == Lex.NUM:
        value = lexer.num * sign
        next_lex()
        return value
    elif lexer.lex == Lex.IDENTIFIER:
        x = table.find(lexer.name)
        if x is not items.Const:
            error.expect('константа')
        next_lex()
        return x.value * sign
    else:
        error.expect('число или имя')


# VarDecl     = "var" ( VarSpec | "(" { VarSpec ";" } ")" ) .
def var_decl():
    next_lex()  # "var"
    if lexer.lex == Lex.IDENTIFIER:
        var_spec()
    elif lexer.lex == Lex.LPAR:
        next_lex()
        while lexer.lex == Lex.IDENTIFIER:
            var_spec()
            semi()
        skip(Lex.RPAR)
    else:
        error.expect('имя или "("')


# VarSpec     = IdentifierList Type .
# IdentifierList = identifier { "," identifier } .
def var_spec():
    check(Lex.IDENTIFIER)
    table.new(items.Var(lexer.name, Types.Int))
    next_lex()  # Identifier
    while lexer.lex == Lex.COMMA:
        next_lex()
        check(Lex.IDENTIFIER)
        table.new(items.Var(lexer.name, Types.Int))
        next_lex()
    check(Lex.IDENTIFIER)  # Type
    x = table.find(lexer.name)
    if not isinstance(x, items.Type):
        error.expect('имя типа')
    next_lex()


# Assignment = identifier "=" Expression .
def assignment(x):
    gen.address(x)
    next_lex()
    if x.typ != expression():
        error.ctx_error('Несоответствие типов при присваивании')
    gen.cmd(govm.SAVE)


# Procedure = identifier "." identifier Arguments
def procedure(x):
    next_lex()  # Пропустили identifier .
    check(Lex.DOT)
    if not isinstance(x, items.Package):
        error.ctx_error('пакет не обнаружен')
    x.usage = True
    next_lex()
    check(Lex.IDENTIFIER)
    key = x.name + '.' + lexer.name
    x = table.find(key)
    if not isinstance(x, items.Proc):
        error.ctx_error('процедура не обнаружена')
    next_lex()
    arguments(x)


# Arguments = "(" [ "&" ] identifier ")"
def arguments(x):
    skip(Lex.LPAR)
    if x.name == 'fmt.Scan':
        skip(Lex.AMPER)
        check(Lex.IDENTIFIER)
        v = table.find(lexer.name)
        if not isinstance(v, items.Var):
            error.ctx_error('В fmt.Scan разрешён только ввод переменных')
        gen.address(v)
        gen.cmd(govm.IN)
        gen.cmd(govm.SAVE)
        next_lex()
    elif x.name == 'fmt.Println':
        return_type = expression()
        if return_type != Types.Int:
            error.ctx_error('В fmt.Println разрешён только вывод выражений целого типа')
        gen.cmd(0)
        gen.cmd(govm.OUT)
        gen.cmd(govm.LN)
    else:
        assert False
    skip(Lex.RPAR)


# IncDecStmt = identifier ( "++" | "--" ) .
def int_dec_stmt(x):
    gen.address(x)
    gen.cmd(govm.DUP)
    gen.cmd(govm.LOAD)
    gen.const(1)
    if lexer.lex == Lex.INC:
        gen.cmd(govm.ADD)
    else:
        gen.cmd(govm.SUB)
    gen.cmd(govm.SAVE)
    next_lex()


# IfStmt = "if" Expression Block [ "else" ( IfStmt | Block ) ] .
def if_stmt():
    next_lex()
    return_type = expression()
    if return_type != Types.Bool:
        error.ctx_error('В операторе "if" требуется логическое выражение')
    cond_pc = gen.PC
    last_goto = 0
    block()
    while lexer.lex == Lex.ELSE:
        next_lex()
        if lexer.lex == Lex.IF:  # else if
            gen.cmd(last_goto)
            gen.cmd(govm.GOTO)
            last_goto = gen.PC
            gen.fixup(cond_pc, gen.PC)
            next_lex()
            return_type = expression()
            if return_type != Types.Bool:
                error.ctx_error('В операторе "else if" требуется логическое выражение')
            cond_pc = gen.PC
            block()
        elif lexer.lex == Lex.BEGIN:  # Последнее "else"
            gen.cmd(last_goto)
            gen.cmd(govm.GOTO)
            last_goto = gen.PC
            gen.fixup(cond_pc, gen.PC)
            block()
            gen.fixup(last_goto, gen.PC)
            return
        else:
            error.expect('if или "{"')
    else:
        gen.fixup(cond_pc, gen.PC)
        gen.fixup(last_goto, gen.PC)


# ForStmt = "for" Expression Block .
def for_stmt():
    for_pc = gen.PC
    next_lex()
    return_type = expression()
    if return_type != Types.Bool:
        error.ctx_error('В операторе "for" требуется логическое выражение')
    cond_pc = gen.PC
    block()
    gen.cmd(for_pc)
    gen.cmd(govm.GOTO)
    gen.fixup(cond_pc, gen.PC)


# Expression = SimpleExpr [ rel_op SimpleExpr ]
# rel_op     = "==" | "!=" | "<" | "<=" | ">" | ">=" .
def expression():
    simple_expr()
    # next_lex()
    if lexer.lex in {Lex.EQEQ, Lex.NE, Lex.LT, Lex.LE, Lex.GT, Lex.GE}:
        rel_op = lexer.lex
        next_lex()
        simple_expr()
        gen.compare(rel_op)
        return Types.Bool
    else:
        return Types.Int


# SimpleExpr  = ( [ unary_op ] Term { add_op Term } )
# unary_op   = "+" | "-" .
# add_op     = "+" | "-" .
def simple_expr():
    if lexer.lex in {Lex.PLUS, Lex.MINUS}:
        unary_op = lexer.lex
        next_lex()
        term()
        if unary_op == Lex.MINUS:
            gen.cmd(govm.NEG)
    else:
        term()
    while lexer.lex in {Lex.PLUS, Lex.MINUS}:
        add_op = lexer.lex
        next_lex()
        term()
        if add_op == Lex.PLUS:
            gen.cmd(govm.ADD)
        else:
            gen.cmd(govm.SUB)


# Term = Factor { mul_op Factor } .
def term():
    factor()
    while lexer.lex in {Lex.MUL, Lex.DIV, Lex.MOD}:
        mul_op = lexer.lex
        next_lex()
        factor()
        if mul_op == Lex.MUL:
            gen.cmd(govm.MULT)
        elif mul_op == Lex.DIV:
            gen.cmd(govm.DIV)
        else:
            gen.cmd(govm.MOD)


# Factor = identifier [. identifier "(" Expression ")"] | number | "(" SimpleExpr ")".
def factor():
    if lexer.lex == Lex.IDENTIFIER:
        x = table.find(lexer.name)
        if isinstance(x, items.Const):
            gen.const(x.value)
            next_lex()
        elif isinstance(x, items.Var):
            gen.address(x)
            gen.cmd(govm.LOAD)
            next_lex()
        elif isinstance(x, items.Package):
            x.usage = True
            next_lex()
            skip(Lex.DOT)
            key = x.name + '.' + lexer.name
            x = table.find(key)
            if not isinstance(x, items.Func):
                error.ctx_error('функция не обнаружена')
            next_lex()
            skip(Lex.LPAR)  # math.Abs
            simple_expr()
            gen.cmd(govm.DUP)  # x, x
            gen.cmd(0)  # x, x, 0
            gen.cmd(gen.PC + 3)  # x, x, 0, A
            gen.cmd(govm.IFGE)
            gen.cmd(govm.NEG)
            skip(Lex.RPAR)
    elif lexer.lex == Lex.NUM:
        gen.cmd(lexer.num)
        next_lex()
    elif lexer.lex == Lex.LPAR:
        next_lex()
        simple_expr()
        skip(Lex.RPAR)
    else:
        error.expect('имя, число или "("')
