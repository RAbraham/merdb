from typing import *

from merdb.core import Map, Where, Column, Order, Source, On, Join, JoinKind, UnaryOperation, BinaryOperation, \
    Aggregate, Rename, Select, Recurse, Limit


def where(source: Source, func: Callable) -> UnaryOperation:
    db = get_db(source)
    return Where(func, source, db)


def get_db(source):
    if hasattr(source, "db"):
        return source.db
    else:
        return None



def agg(source: Source, func: Callable, column: str,  name: str = None, by = None):
    db = get_db(source)
    return Aggregate(func, by, column, name, source, db)

def limit(source: Source, limit):
    db = get_db(source)
    return Limit(limit, source, db)

# def agg_row(source: Source, func: Callable, columns: str, by = None, name: str = None):
#     db = get_db(source)
#     return AggregateRow(func, by, column, name, source, db)
def order_by(source: Source, column: str, ascending:bool) -> UnaryOperation:
    # TODO: Why not just pass source to Order and initialiaze db there? You have to do the same everywhere, make a Operation abstract class
    db = get_db(source)
    return Order([(Column(column), ascending)], source, db)

def order_by_str(source: Source, column: str, order:str) -> UnaryOperation:
    assert order in ["asc", "desc"]
    if order == "asc":
        ascending = True
    else:
        ascending = False
    # TODO: Why not just pass source to Order and initialiaze db there? You have to do the same everywhere, make a Operation abstract class
    return order_by(source, column, ascending)

def join_inner(left, right, on:On = None) -> BinaryOperation:
    dbl = get_db(left)
    dbr = get_db(right)
    assert  dbl == dbr, f"{left} and {right} should have the same Database source"
    return Join(JoinKind.INNER, left, right, on, dbl)

def recurse(start: Source, until) -> BinaryOperation:
    dbl = get_db(start)
    # return Join(JoinKind.INNER, left, right, on, dbl)
    return Recurse(dbl, start, until)

def join_cross(left, right, on:On) -> BinaryOperation:
    dbl = get_db(left)
    dbr = get_db(right)
    assert  dbl == dbr, f"{left} and {right} should have the same Database source"
    return Join(JoinKind.CROSS, left, right, on, dbl)

def map( source: Source, func: Callable, column: str) -> UnaryOperation:
    db = get_db(source)
    return Map(func, column, source, db)

def rename(source: Source, columns:Dict[str, str]):
    db = get_db(source)
    return Rename(db, source, columns)


def select(source: Source, *columns):
    db = get_db(source)
    return Select(db, source, columns)

def show(source: Source):
    print(source().df())
    return source

