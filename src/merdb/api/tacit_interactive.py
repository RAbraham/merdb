import copy
from dataclasses import dataclass

import merdb.resource as r
from merdb.api.tacit import agg, where, order_by, map, join_inner as ji, join_cross as jc, select, rename, show
from merdb.api.common import Row, C


def table(df):
    return InteractiveTacitTable(df)


t = table


# def join_inner(*args, **kwargs):
#     new_args = list(args)
#     if isinstance(args[0], InteractiveTacitTable) or isinstance(args[0], DerivedTable):
#         new_args[0] = args[0].source
#     return ji(*tuple(new_args), **kwargs)


def join_inner(*args, **kwargs):
    new_args = list(args)
    if isinstance(args[0], InteractiveTacitTable):
        new_args[0] = args[0].source
    return ji(*tuple(new_args), **kwargs)

# class InteractiveTacitTable:
#     def __init__(self, df):
#         self.df = df
#         self.table = r.table
#         self.source = self.table(df)
#
#     def __or__(self, op):
#         self.source = op.operate(self.source)
#
#         return DerivedTable(self.source)
#
#     def __str__(self):
#         return str(self.source().df())
#
#     def __repr__(self):
#         return self.source().df().__repr__()
#
#     def columns(self):
#         return [Column(c) for c in self.df.columns]


@dataclass
class Column:
    name: str


# class DerivedTable:
#     def __init__(self, source):
#         self.source = source
#
#     def __or__(self, op):
#         self.source = op.operate(self.source)
#         return DerivedTable(self.source)
#
#     def __str__(self):
#         return str(self.source().df())
#
#     def __repr__(self):
#         return self.source().df().__repr__()


class InteractiveTacitTable:
    def __init__(self, df):
        # TODO: Remove self.table?
        self.table = r.table
        self.source = self.table(df)

    def __or__(self, op):
        _source = op.operate(self.source)

        return InteractiveTacitTable(_source().df())

    def __str__(self):
        return str(self.df())

    def __repr__(self):
        return self.df().__repr__()

    def columns(self):
        return [Column(c) for c in self.df().columns]

    def df(self):
        return self.source().df()



# class DerivedTable:
#     def __init__(self, df):
#         self.materialized_source = materialized_source
#
#     def __or__(self, op):
#         _source = op.operate(self.materialized_source)
#         return DerivedTable(_source())
#
#     def __str__(self):
#         return str(self.materialized_source().df())
#
#     def __repr__(self):
#         return self.materialized_source().df().__repr__()
