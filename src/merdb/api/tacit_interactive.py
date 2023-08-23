import copy
from dataclasses import dataclass

import merdb.resource as r
from merdb.api.tacit import agg, where, order_by, map, join_inner as ji, join_cross as jc, select, rename, show
from merdb.api.common import Row, C


def table(df):
    return InteractiveTacitTable(df)


t = table


def join_inner(*args, **kwargs):
    new_args = list(args)
    if isinstance(args[0], InteractiveTacitTable) or isinstance(args[0], DerivedTable):
        new_args[0] = args[0].source
    return ji(*tuple(new_args), **kwargs)


class InteractiveTacitTable:
    def __init__(self, df):
        self.df = df
        self.table = r.table
        self.source = self.table(df)

    def __or__(self, op):
        self.source = op.operate(self.source)
        return DerivedTable(self.source)

    def __str__(self):
        return str(self.source().df())

    def __repr__(self):
        return self.source().df().__repr__()

    def columns(self):
        return [Column(c) for c in self.df.columns]


@dataclass
class Column:
    name: str


class DerivedTable:
    def __init__(self, source):
        self.source = source

    def __or__(self, op):
        self.source = op.operate(self.source)
        return DerivedTable(self.source)

    def __str__(self):
        return str(self.source().df())

    def __repr__(self):
        return self.source().df().__repr__()
