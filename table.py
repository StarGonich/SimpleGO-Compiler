# Таблица имен

import error
import items

table = []


def open_scope():
    table.append({})


def close_scope():
    table.pop()


def new(item):
    last = table[-1]
    if item.name in last:
        error.ctx_error("Повторное объявление имени")
    else:
        last[item.name] = item


def find(name):
    for block in reversed(table):
        if name in block:
            return block[name]
    error.ctx_error("Необъявленное имя")


def get_vars():
    variables = []
    last_block = table[-1]
    for item in last_block.values():
        if isinstance(item, items.Var):
            variables.append(item)
    return variables


def get_packages():
    packages = []
    last_block = table[-1]
    for item in last_block.values():
        if isinstance(item, items.Package):
            packages.append(item)
    return packages
